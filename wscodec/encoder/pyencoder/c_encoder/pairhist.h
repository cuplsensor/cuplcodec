#ifndef _PAIRHIST_H_
#define _PAIRHIST_H_

#include <stdbool.h>


/**
 *  Structure to hold one sample consisting of two 12-bit readings.
 */
typedef struct
{
        unsigned char rd0Msb;    /*!< Reading0 Most significant byte. */
        unsigned char rd1Msb;    /*!< Reading1 Most significant byte. */
        unsigned char Lsb;      /*!< Least significant 4-bit nibbles of reading0 and reading1. */
} pair_t;

/**
 *  Structure to hold hash and npairs as per CODEC_SPEC_14.
 */
typedef struct
{
    unsigned char hash[7];      /*!< Last 7 bytes of the MD5 or HMAC-MD5 hash. */
    unsigned char npairs[2];    /*!< Number of valid pairs in the circular buffer. */
} hashn_t;

/// Have doxygen ignore this
/// @cond
int pairhist_ovr(pair_t sample);
int pairhist_push(pair_t sample);
hashn_t pairhist_hash(int npairs, int usehmac, unsigned int loopcount, unsigned int resetsalltime, unsigned int batv_resetcause, int cursorpos);
pair_t pairhist_read(unsigned int index, int * error);

#ifndef NOT_CFFI
const int buflenpairs;
#endif
/// @endcond

#endif //_PAIRHIST_H_
