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

#ifndef _EEP_H_
#define _EEP_H_

int eep_write(const int eepblk, const unsigned int bufblk);
int eep_read(const int eepblk, const unsigned int bufblk);
int eep_cp(int * indexptr, const char * dataptr, const int lenbytes);
int eep_swap(const unsigned int srcblk, const unsigned int destblk);
int eep_cpbyte(int * indexptr, const char bytedata);
void eep_waitwritedone(void);

#endif //_BASE64_H_
