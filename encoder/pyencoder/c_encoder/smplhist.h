#ifndef _SMPLHIST_H_
#define _SMPLHIST_H_

#include <stdbool.h>




/**
 *  Structure to hold one sample consisting of two 12-bit measurands.
 */
typedef struct sensordatachars
{
        unsigned char m1Msb;    /*!< Measurand 1 Most significant byte.*/
        unsigned char m2Msb;    /*!< Measurand 2 Most significant byte.*/
        unsigned char Lsb;      /*!< Least significant 4-bit nibbles of measurand 1 and measurand 2. */
} sdchars_t;

typedef struct md5len
{
    unsigned char md5[7];
    unsigned char lensmplsbytes[2];
} md5len_t;

int smplhist_ovr(sdchars_t sample);
int smplhist_push(sdchars_t sample);
md5len_t smplhist_md5(int lensmpls, bool usehmac);
sdchars_t smplhist_read(unsigned int index, int * error);

#ifndef NOT_CFFI
const int buflensamples;
#endif

#endif //_SMPLHIST_H_
