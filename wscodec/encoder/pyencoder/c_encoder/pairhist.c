#include "pairhist.h"
#include "defs.h"
#include "md5.h"
#include "nvtype.h"



#define MD5DIGESTLEN_BYTES  16              /*!< Length of the MD5 digest (output) in bytes. */
#define MD5BLKLEN_BYTES     64              /*!< Length of the MD5 input message block in bytes. */

extern nv_t nv;

unsigned char msgblock[MD5BLKLEN_BYTES];    /*!< Block to hold message data as an input to the MD5 algorithm. */
const int buflenpairs= BUFLEN_PAIRS;        /*!< Length of the circular buffer in pairs. */
static pair_t pairhistory[BUFLEN_PAIRS];    /*!< Array of unencoded pairs. This mirrors the circular buffer of base64 encoded pairs stored in EEPROM. */
static int cursorindex = -1;                /*!< Index marking the end of the circular buffer. The most recent sample is stored here. The next index contains the oldest sample.  */
static const char ipadchar = 0x36;          /*!< Inner padding byte for HMAC as defined in <a href="https://tools.ietf.org/html/rfc2104#section-2">RFC 2104</a>.*/
static const char opadchar = 0x5C;          /*!< Outer padding byte for HMAC as defined in <a href="https://tools.ietf.org/html/rfc2104#section-2">RFC 2104</a>. */
static MD5_CTX ctx;                         /*!< MD5 context. */

/*!
 * @brief Overwrites the most recent pair in the history buffer.
 * This is used when the format stipulates one reading per sample (rather than one pair per sample).
 * For the first sample, a full pair is written with \link pairhist_push. The second reading is set to an invalid value.
 * On the next sample, the second reading in the pair is overwritten, so the history buffer must be overwritten  with \link pairhist_ovr
 *
 * @param pair New value of the most recent pair.
 */
void pairhist_ovr(pair_t pair)
{
  pairhistory[cursorindex] = pair;
}

/*!
 * @brief Pushes a new pair onto the history buffer.
 * This operation overwrites an old pair if the circular buffer is full.
 *
 * @param pair Value of the new pair.
 */
void pairhist_push(pair_t pair)
{
  if (cursorindex == BUFLEN_PAIRS-1)
  {
    cursorindex = 0;   // Write next pair to the start of the buffer.
  }
  else
  {
    cursorindex = cursorindex + 1; // Write next pair to the next index in the buffer
  }

  pairhistory[cursorindex] = pair;
}

/*!
 * @brief Reads one pair at an offset from the end of pairhistory.
 * This function makes it possible to read pairhistory as if it was a linear buffer.
 *
 * @param offset When 0, the most recent pair is returned. When 1, the 2nd most recent pair is returned. When BUFLEN_PAIRS-1, the oldest pair is returned. Any larger offset is invalid.
 * @param error Pointer to an error variable. This is set to 1 when offset exceeds the length of the circular buffer (BUFLEN_PAIRS-1). It is 0 otherwise.
 *
 * @returns A pair read from pairhistory or a struct containing 3 zeroes if an error has occurred.
 */
pair_t pairhist_read(unsigned int offset, int * error)
{
    int readindex;
    pair_t pair;
    *error = 0;

    readindex = cursorindex - offset;

    if (readindex < 0)
    {
        readindex += (BUFLEN_PAIRS);
        if (readindex >= cursorindex)
        {
            pair = pairhistory[readindex];
        }
        else
        {
            pair.rd0Msb = 0; // Not allowed to loop around the buffer more than once.
            pair.rd1Msb = 0;
            pair.Lsb = 0;
            *error = 1;
        }
    }
    else
    {
        pair = pairhistory[readindex];
    }

    return pair;
}

/*!
 * @brief Calculates a hash from #pairhistory and other state variables.
 *
 * The hash is calculated according to the table in CODEC_FEAT_24. If HMAC is enabled then the output is the last
 * seven bytes of the HMAC-MD5 digest. If it is not then the hash is an MD5 checksum only. Note that the latter is
 * intended for debug purposes only.
 *
 * The MD5 is calculated iteratively 64 bytes at a time with multiple calls to MD5_Update().
 *
 * @param npairs            The number of pairs from #pairhistory to include in the hash.
 * @param usehmac           When 0 the hash is MD5 only. Otherwise it is HMAC-MD5.
 * @param loopcount         Number of times the circular buffer cursor has looped (or wrapped) from the end to the beginning.
 * @param resetsalltime     Number of times the host firmware has logged a Power-on-Reset.
 * @param batv_resetcause   8-bit battery voltage concatenated with the 8-bit resetcause variable.
 * @param endstopindex      Offset of the sample::ENDSTOP_BYTE relative to the start of the NDEF message circular buffer, measured in bytes.
 *
 * @returns A value of type hashn_t. This contains the last 7 hash bytes together with npairs.
 */
hashn_t pairhist_hash(int npairs, int usehmac, unsigned int loopcount, unsigned int resetsalltime, unsigned int batv_resetcause, int endstopindex)
{
    pair_t pair;
    int error = 0;
    int offset = 0;
    hashn_t hashn;
    unsigned int i;
    unsigned char md5digest[MD5DIGESTLEN_BYTES];
    char * secretkey = nv.seckey;

    // Initialise MD5 state.
    MD5_Init(&ctx);

    // --------------------------------------------------------------------------
    // HMAC Only: Create the 64-byte padded inner key and update the MD5 from it.
    // ---------------------------------------------------------------------------
    if (usehmac)
    {
        for(i=0; i<sizeof(msgblock); i++)
        {
            if (i<SECKEY_LENBYTES)
            {
                // First bytes contain the secret key XORed with the inner padding byte.
                msgblock[i] = secretkey[i] ^ ipadchar;
            }
            else
            {
                // Remaining bytes contain the inner padding byte.
                msgblock[i] = ipadchar;
            }
        }

        MD5_Update(&ctx, msgblock, sizeof(msgblock));
    }

    // ---------------------------------------------------------------------------------------------------
    // Copy pairs from pairhist into the input message block, starting with the most recent pair first.
    // This is done 63 bytes (21 pairs) at a time. Update MD5 when the message block is full.
    // ---------------------------------------------------------------------------------------------------
    i=0;
    while(offset < npairs)
    {
        pair = pairhist_read(offset++, &error);
        if (error == 1)
        {
          // Set hash to something distinctive and return immediately.
          for (i=0; i<sizeof(hashn.hash); i++)
          {
              hashn.hash[i] = 9;
          }
          return hashn;
        }
        msgblock[i++] = pair.rd0Msb;
        msgblock[i++] = pair.rd1Msb;
        msgblock[i++] = pair.Lsb;

        // When i is a multiple of 63 bytes, the maximum number that can be store in a 64 byte block.
        if (i == MD5BLKLEN_BYTES-1)
        {
            MD5_Update(&ctx, msgblock, i);
            i = 0;
        }
    }

    // ----------------------------------------
    // MD5 of npairs from pairhist is complete.
    // Update MD5 with the 8 status bytes.
    // -----------------------------------------
    if (i >= MD5BLKLEN_BYTES-1-8)
    {
       MD5_Update(&ctx, msgblock, i);   // Update MD5 first if the message block will overflow.
       i = 0;
    }

    msgblock[i++] = loopcount >> 8;
    msgblock[i++] = loopcount & 0xFF;
    msgblock[i++] = resetsalltime >> 8;
    msgblock[i++] = resetsalltime & 0xFF;
    msgblock[i++] = batv_resetcause >> 8;
    msgblock[i++] = batv_resetcause & 0xFF;
    msgblock[i++] = endstopindex >> 8;
    msgblock[i++] = endstopindex & 0xFF;

    // Update MD5 digest from the message block.
    MD5_Update(&ctx, msgblock, i);

    // -----------------------
    // HMAC Only: Second pass
    // -----------------------
    if (usehmac)
    {
        // Read MD5 digest from the first pass (hash sum 1).
        MD5_Final(md5digest, &ctx);

        // Reinitialise MD5 state.
        MD5_Init(&ctx);

        // Create the 64-byte padded outer key.
        for(i=0; i<sizeof(msgblock); i++)
        {
            if (i<SECKEY_LENBYTES)
            {
                msgblock[i] = secretkey[i] ^ opadchar;
            }
            else
            {
                msgblock[i] = opadchar;
            }
        }

        // Update MD5 from the padded outer key
        MD5_Update(&ctx, msgblock, sizeof(msgblock));

        // Copy hash sum 1 to the message block and update MD5.
        for(i=0; i<sizeof(md5digest); i++)
        {
            msgblock[i] = md5digest[i];
        }

        MD5_Update(&ctx, msgblock, sizeof(md5digest));
    }

    // Read MD5 digest from the first pass (MD5) or second pass (HMAC-MD5)
    MD5_Final(md5digest, &ctx);

    // Place lower 7 bytes into the hashn structure.
    for (i=0; i<sizeof(hashn.hash); i++)
    {
        hashn.hash[i] = md5digest[i];
    }
    hashn.npairs[0] = (npairs & 0xFF00) >> 8;
    hashn.npairs[1] = (npairs & 0x00FF);

    return hashn;
}
