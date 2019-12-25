#include "smplhist.h"
#include "defs.h"
#include "md5.h"
#include "nvtype.h"

extern nv_t nv;

const int buflensamples = BUFLEN_SAMPLES;
static sdchars_t samplehistory[BUFLEN_SAMPLES];
static int histpos = 0;
unsigned char md5block[64];
static const char ipadchar = 0x36;
static const char opadchar = 0x5C;
static MD5_CTX ctx;
static int prevhistpos;


int smplhist_ovr(sdchars_t sample)
{
  samplehistory[prevhistpos] = sample;

  return 0;
}

int smplhist_push(sdchars_t sample)
{
  samplehistory[histpos] = sample;
  prevhistpos = histpos;

  if (histpos == BUFLEN_SAMPLES-1)
  {
    histpos = 0;
  }
  else
  {
    histpos++;
  }

  return 0;
}

sdchars_t smplhist_read(unsigned int index, int * error)
{
    int readpos;
    sdchars_t sample;
    *error = 0;

    readpos = (histpos - 1) - index;

    if (readpos < 0)
    {
        readpos += (BUFLEN_SAMPLES);
        if (readpos >= histpos)
        {
            sample = samplehistory[readpos];
        }
        else
        {
            sample.m1Msb = 0; // Not allowed to loop around the buffer more than once.
            sample.m2Msb = 0;
            sample.Lsb = 0;
            *error = 1;
        }
    }
    else
    {
        sample = samplehistory[readpos];
    }

    return sample;
}

md5len_t smplhist_md5(int lensmpls, int usehmac, unsigned int loopcount, unsigned int resetsalltime, unsigned int batv_resetcause, int cursorpos)
{
    sdchars_t prevsmpl;
    int error = 0;
    int smplindex = 0;
    md5len_t md5length;
    unsigned int i;
    unsigned char md5result[16];
    char * secretkey = nv.seckey;


    MD5_Init(&ctx);

    if (usehmac)
    {
        // Append inner key.
        for(i=0; i<sizeof(md5block); i++)
        {
            if (i<SECKEY_LENBYTES)
            {
                md5block[i] = secretkey[i] ^ ipadchar;
            }
            else
            {
                md5block[i] = ipadchar;
            }
        }

        MD5_Update(&ctx, md5block, sizeof(md5block));
    }

    // Seperate sample history into 64 byte blocks and a partial block.
    i=0;
    // Start to take MD5 of the message.
    while(smplindex<lensmpls)
    {
        prevsmpl = smplhist_read(smplindex++, &error);
        if (error == 1)
        {
          for (i=0; i<sizeof(md5length.md5); i++)
          {
              md5length.md5[i] = 9;
          }
          return md5length;
        }
        md5block[i++] = prevsmpl.m1Msb;
        md5block[i++] = prevsmpl.m2Msb;
        md5block[i++] = prevsmpl.Lsb;

        // When i is a multiple of 63 samples, the maximum number that can be store in a 64 byte block.
        if (i == 63)
        {
            MD5_Update(&ctx, md5block, i);
            i = 0;
        }
    }

    if (i >= 63-8)
    {
       MD5_Update(&ctx, md5block, i);
       i = 0;
    }

    md5block[i++] = loopcount >> 8;
    md5block[i++] = loopcount & 0xFF;
    md5block[i++] = resetsalltime >> 8;
    md5block[i++] = resetsalltime & 0xFF;
    md5block[i++] = batv_resetcause >> 8;
    md5block[i++] = batv_resetcause & 0xFF;
    md5block[i++] = cursorpos >> 8;
    md5block[i++] = cursorpos & 0xFF;

    // Calculate MD5 checksum from sample history.
    MD5_Update(&ctx, md5block, i);



    if (usehmac)
    {
        // Obtain MD5 digest. Hash sum 1.
        MD5_Final(md5result, &ctx);

        // Copy hash sum 1 to the start of a new MD5 block.
        // Reinitialise MD5.
        MD5_Init(&ctx);

        // Append outer key.
        for(i=0; i<sizeof(md5block); i++)
        {
            if (i<SECKEY_LENBYTES)
            {
                md5block[i] = secretkey[i] ^ opadchar;
            }
            else
            {
                md5block[i] = opadchar;
            }
        }

        MD5_Update(&ctx, md5block, sizeof(md5block));

        for(i=0; i<sizeof(md5result); i++)
        {
            md5block[i] = md5result[i];
        }

        MD5_Update(&ctx, md5block, sizeof(md5result));
    }

    // Obtain MD5 digest.
    MD5_Final(md5result, &ctx);

    // Place lower 6 bytes into md5length structure.
    for (i=0; i<sizeof(md5length.md5); i++)
    {
        md5length.md5[i] = md5result[i];
    }
    md5length.lensmplsbytes[0] = (lensmpls & 0xFF00) >> 8;
    md5length.lensmplsbytes[1] = (lensmpls & 0x00FF);

    return md5length;
}
