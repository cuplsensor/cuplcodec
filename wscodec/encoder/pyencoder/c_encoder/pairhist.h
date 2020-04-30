#ifndef _PAIRHIST_H_
#define _PAIRHIST_H_

#include <stdbool.h>


/**
 *  Structure to hold one sample consisting of two 12-bit measurands.
 */
typedef struct
{
        unsigned char m1Msb;    /*!< Measurand 1 Most significant byte.*/
        unsigned char m2Msb;    /*!< Measurand 2 Most significant byte.*/
        unsigned char Lsb;      /*!< Least significant 4-bit nibbles of measurand 1 and measurand 2. */
} pair_t;

typedef struct md5len
{
    unsigned char md5[7];
    unsigned char lenpairsbytes[2];
} md5len_t;

int pairhist_ovr(pair_t sample);
int pairhist_push(pair_t sample);
md5len_t pairhist_md5(int lenpairs, int usehmac, unsigned int loopcount, unsigned int resetsalltime, unsigned int batv_resetcause, int cursorpos);
pair_t pairhist_read(unsigned int index, int * error);

#ifndef NOT_CFFI
const int buflensamples;
#endif

#endif //_PAIRHIST_H_
