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

#ifndef _DEFS_H_
#define _DEFS_H_

#define CODEC_VERSION       2

#define BYTES_PER_DEMI      8               /*!< The number of bytes per demi. */
#define DEMIS_PER_BLK       2               /*!< The number of demis per block. */
#define PAIRS_PER_DEMI      2               /*!< The number of base64 encoded pairs per demi. */
#define BUFLEN_BLKS         48              /*!< Length of the circular buffer in 16-byte blocks. */
#define ENDSTOP_BLKS        1               /*!< Endstop length in 16-byte blocks. */
#define ENDMARKER_OFFSET_IN_ENDSTOP_1 7
#define BLKSIZE             0x10


#define BUFLEN_PAIRS (PAIRS_PER_DEMI * DEMIS_PER_BLK * (BUFLEN_BLKS - ENDSTOP_BLKS))

#endif
