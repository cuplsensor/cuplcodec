#ifndef _SMPLHIST_H_
#define _SMPLHIST_H_

#include <stdbool.h>


typedef struct sensordatachars
{
        unsigned char m1Msb;
        unsigned char m2Msb;
        unsigned char Lsb;
} sdchars_t;

typedef struct md5len
{
    unsigned char md5[7];
    unsigned char lensmplsbytes[2];
} md5len_t;

int smplhist_ovr(sdchars_t sample);
int smplhist_push(sdchars_t sample);
md5len_t smplhist_md5(int lensmpls, bool usehmac);

#endif //_SMPLHIST_H_
