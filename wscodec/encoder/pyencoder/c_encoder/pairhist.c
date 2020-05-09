#include "pairhist.h"
#include "defs.h"
#include "md5.h"
#include "nvtype.h"

extern nv_t nv;

const int buflenpairs= BUFLEN_PAIRS;        /*!< Length of the circular buffer in pairs. */
static pair_t hist[BUFLEN_PAIRS];           /*!< Array of unencoded pairs. This mirrors the circular buffer of encoded pairs stored in EEPROM. */
static int endindex = -1;                   /*!< Index marking the end of the circular buffer. The most recent sample is stored here.  */
unsigned char hashblock[64];
static const char ipadchar = 0x36;
static const char opadchar = 0x5C;
static MD5_CTX ctx;

int pairhist_ovr(pair_t sample)
{
  hist[endindex] = sample;

  return 0;
}

int pairhist_push(pair_t sample)
{
  if (endindex == BUFLEN_PAIRS-1)
  {
    endindex = 0;   // Write next pair to the start of the buffer.
  }
  else
  {
    endindex = endindex + 1; // Write next pair to the next index in the buffer
  }

  hist[endindex] = sample;

  return 0;
}

pair_t pairhist_read(unsigned int index, int * error)
{
    int readpos;
    pair_t pair;
    *error = 0;

    readpos = endindex - index;

    if (readpos < 0)
    {
        readpos += (BUFLEN_PAIRS);
        if (readpos >= endindex)
        {
            pair = hist[readpos];
        }
        else
        {
            pair.m1Msb = 0; // Not allowed to loop around the buffer more than once.
            pair.m2Msb = 0;
            pair.Lsb = 0;
            *error = 1;
        }
    }
    else
    {
        pair = hist[readpos];
    }

    return pair;
}

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
        hashblock[i++] = prevpair.m1Msb;
        hashblock[i++] = prevpair.m2Msb;
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
