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

/*
 * nt3h.h
 *
 *  Created on: 12 Aug 2017
 *      Author: mmackay
 */

#ifndef _NT3H_H_
#define _NT3H_H_

int nt3h_writetag(int eepromBlock, char * blkdata);
int nt3h_readtag(int eepromBlock, char * blkdata);
int nt3h_eepromwritedone(void);
int nt3h_check_address(void);
void nt3h_clearlock(void);
void nt3h_update_cc(void);
void nt3h_init_wrongaddress(void);

int printint(int myint);

#endif //_NT3H_H_
