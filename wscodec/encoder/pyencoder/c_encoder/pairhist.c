#include "pairhist.h"
#include "defs.h"
#include "md5.h"
#include "nvtype.h"

extern nv_t nv;

unsigned char hashblock[64];                /*!< Block of RAM for storing data to be passed to the MD5 algorithm. */
const int buflenpairs= BUFLEN_PAIRS;        /*!< Length of the circular buffer in pairs. */
static pair_t pairhistory[BUFLEN_PAIRS];    /*!< Array of unencoded pairs. This mirrors the circular buffer of base64 encoded pairs stored in EEPROM. */
static int endindex = -1;                   /*!< Index marking the end of the circular buffer. The most recent sample is stored here.  */
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
int pairhist_ovr(pair_t pair)
{
  pairhistory[endindex] = pair;

  return 0;
}

/*!
 * @brief Pushes a new pair onto the history buffer.
 * This operation overwrites an old pair if the circular buffer is full.
 *
 * @param pair Value of the new pair.
 */
int pairhist_push(pair_t pair)
{
  if (endindex == BUFLEN_PAIRS-1)
  {
    endindex = 0;   // Write next pair to the start of the buffer.
  }
  else
  {
    endindex = endindex + 1; // Write next pair to the next index in the buffer
  }

  pairhistory[endindex] = pair;

  return 0;
}

/*!
 * @brief Reads one pair at an offset from the end of pairhistory.
 * This function makes it possible to read pairhistory as if it was a linear buffer.
 *
 * @param offset When 0, the most recent pair is returned. When 1, the 2nd most recent pair is returned. When BUFLEN_PAIRS-1, the oldest pair is returned. Any larger offset is invalid.
 * @param error Pointer to an error variable. This is set to 1 when offset exceeds the length of the circular buffer (BUFLEN_PAIRS-1). It is 0 otherwise.
 */
pair_t pairhist_read(unsigned int offset, int * error)
{
    int readindex;
    pair_t pair;
    *error = 0;

    readindex = endindex - offset;

    if (readindex < 0)
    {
        readindex += (BUFLEN_PAIRS);
        if (readindex >= endindex)
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
 * @brief Calculates MD5 or HMAC-MD5 of pairs in pairhistory.
 *
 * @param npairs
 * @param usehmac When 1 the HMAC-MD5 hash is calculated. When 0 only the MD5 is calculated.
 * @param loopcount Extra data to include in the hash.
 * @param resetsalltime Extra data to include in the hash.
 * @param batv_resetcause Extra data to include in the hash.
 * @param cursorpos Extra data to include in the hash.
 *
 * @returns hashn
 */
hashn_t pairhist_hash(int npairs, int usehmac, unsigned int loopcount, unsigned int resetsalltime, unsigned int batv_resetcause, int cursorpos)
{
    pair_t prevpair;
    int error = 0;
    int pairindex = 0;
    hashn_t hashn;
    unsigned int i;
    unsigned char md5result[16];
    char * secretkey = nv.seckey;

    MD5_Init(&ctx);

    if (usehmac)
    {
        // Append inner key.
        for(i=0; i<sizeof(hashblock); i++)
        {
            if (i<SECKEY_LENBYTES)
            {
                hashblock[i] = secretkey[i] ^ ipadchar;
            }
            else
            {
                hashblock[i] = ipadchar;
            }
        }

        MD5_Update(&ctx, hashblock, sizeof(hashblock));
    }

    // Seperate pair history into 64 byte blocks and a partial block.
    i=0;
    // Start to take MD5 of the message.
    while(pairindex<npairs)
    {
        prevpair = pairhist_read(pairindex++, &error);
        if (error == 1)
        {
          for (i=0; i<sizeof(hashn.hash); i++)
          {
              hashn.hash[i] = 9;
          }
          return hashn;
        }
        hashblock[i++] = prevpair.rd0Msb;
        hashblock[i++] = prevpair.rd1Msb;
        hashblock[i++] = prevpair.Lsb;

        // When i is a multiple of 63 pairs, the maximum number that can be store in a 64 byte block.
        if (i == 63)
        {
            MD5_Update(&ctx, hashblock, i);
            i = 0;
        }
    }

    if (i >= 63-8)
    {
       MD5_Update(&ctx, hashblock, i);
       i = 0;
    }

    hashblock[i++] = loopcount >> 8;
    hashblock[i++] = loopcount & 0xFF;
    hashblock[i++] = resetsalltime >> 8;
    hashblock[i++] = resetsalltime & 0xFF;
    hashblock[i++] = batv_resetcause >> 8;
    hashblock[i++] = batv_resetcause & 0xFF;
    hashblock[i++] = cursorpos >> 8;
    hashblock[i++] = cursorpos & 0xFF;

    // Calculate MD5 checksum from pair history.
    MD5_Update(&ctx, hashblock, i);



    if (usehmac)
    {
        // Obtain MD5 digest. Hash sum 1.
        MD5_Final(md5result, &ctx);

        // Copy hash sum 1 to the start of a new MD5 block.
        // Reinitialise MD5.
        MD5_Init(&ctx);

        // Append outer key.
        for(i=0; i<sizeof(hashblock); i++)
        {
            if (i<SECKEY_LENBYTES)
            {
                hashblock[i] = secretkey[i] ^ opadchar;
            }
            else
            {
                hashblock[i] = opadchar;
            }
        }

        MD5_Update(&ctx, hashblock, sizeof(hashblock));

        for(i=0; i<sizeof(md5result); i++)
        {
            hashblock[i] = md5result[i];
        }

        MD5_Update(&ctx, hashblock, sizeof(md5result));
    }

    // Obtain MD5 digest.
    MD5_Final(md5result, &ctx);

    // Place lower 6 bytes into hashn structure.
    for (i=0; i<sizeof(hashn.hash); i++)
    {
        hashn.hash[i] = md5result[i];
    }
    hashn.npairs[0] = (npairs & 0xFF00) >> 8;
    hashn.npairs[1] = (npairs & 0x00FF);

    return hashn;
}
