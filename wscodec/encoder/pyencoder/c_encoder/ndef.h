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

#ifndef _NDEF_H_
#define _NDEF_H_

#include <stdbool.h>


void ndef_writeblankurl(int buflenblks, char * statusb64, int * bufstartblk);
int ndef_writepreamble(int buflenblks, char * statusb64);
void ndef_calclen(int * paddinglen, int * preamblenbytes, int * urllen);

#endif //_NDEF_H_
