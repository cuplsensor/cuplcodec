/*
 * nt3h.h
 *
 *  Created on: 12 Aug 2017
 *      Author: mmackay
 */

#ifndef _NT3H_H_
#define _NT3H_H_

#define BLKSIZE 0x10



void nt3h_init(void);
int nt3h_writetag(int eepromBlock, char * blkdata);
int nt3h_readtag(int eepromBlock, char * blkdata);
int nt3h_eepromwritedone(void);
int printint(int myint);

#endif //_NT3H_H_
