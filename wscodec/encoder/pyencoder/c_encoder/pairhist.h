/*  cuplcodec encodes environmental sensor data into a URL and the reverse
 *
 *  https://github.com/cuplsensor/cuplcodec
 *
 *  Original Author: Malcolm Mackay
 *  Email: malcolm@plotsensor.com
 *
 *  Copyright (C) 2021. Plotsensor Ltd.
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

/*!
 * @file pairhist.h
 * @brief This maintains a circular buffer named #pairhistory. It contains all pairs that are
 * in the NDEF message circular buffer stored in the NFC-readable EEPROM. A crucial difference is that #pairhistory
 * is stored in RAM, so its contents can be accessed quickly.
 *
 * This allows for a hash to be taken of the unencoded circular buffer pairs, each time this list changes. The decoder uses this
 * to verify that it has decoded the circular buffer faithfully: It must output the same list of pairs, as fed to the encoder
 * with multiple calls to enc_pushsample().
 *
 * After decoding the circular buffer, the hash is calculated. The decoder checks this equals the encoder hash, which is extracted from
 * #endstop_t::hashnb64 in the NDEF message. If it does not, an error is raised and no data are returned.
 *
 * The hash function can either be <a href="https://en.wikipedia.org/wiki/MD5">MD5</a> or <a href="https://en.wikipedia.org/wiki/HMAC">HMAC-MD5</a>
 * The former is a simple checksum for debugging the codec. It should not be used in production, because it is no good as a hash function and
 * collisions can be found easily. The HMAC-MD5 should be used instead. A detailed discussion can be found in the CODEC_FEAT_24.
 *
 * When a pair is pushed to or overwritten in the NDEF message, pairhistory must be updated with pairhist_push() and
 * pairhist_ovr() respectively. This ensures that the output of pairhist_hash() will be accurate.
 */

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
void pairhist_ovr(pair_t pair);
void pairhist_push(pair_t pair);
hashn_t pairhist_hash(int npairs, int usehmac, unsigned int loopcount, unsigned int resetsalltime, unsigned int batv_resetcause, int cursorpos);
pair_t pairhist_read(unsigned int index, int * error);

#ifndef NOT_CFFI
const int buflenpairs;
#endif
/// @endcond

#endif //_PAIRHIST_H_
