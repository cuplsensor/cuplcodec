/*
 * nt3h2211.c
 *
 *  Created on: 12 Aug 2017
 *      Author: mmackay
 */

#include "nt3h.h"
#include <string.h>
#include "i2c.h"
#include <stdbool.h>
#include "defs.h"

unsigned char rxData[16] = {0};
unsigned char txData[16] = {0};
unsigned char chunk1Data[50] = {0};
unsigned char chunk2Data[50] = {0};

#define DEVADDR     0x55 // Careful. Was 0x55. Got overwritten.

#define PAGE0       0

#define CC_REGADDR  0x0C

#define BLOCKSIZE  16

/*! \brief Initialise PAGE0 of the NT3H2211 I2C EEPROM.
 *
 */
void nt3h_init(void)
{
    volatile int ccval = 0;
    i2c_read_block(DEVADDR, PAGE0, BLOCKSIZE, rxData, 0xFF);
    rxData[0] = 0xAA;
    rxData[12] = 0xE1;
    rxData[13] = 0x10;
    rxData[14] = 0x6D;
    i2c_write_block(DEVADDR, PAGE0, BLOCKSIZE, rxData);
    i2c_read_block(DEVADDR, PAGE0, BLOCKSIZE, rxData, 0xFF);
}

/*! \brief Write a 16-byte block of the NT3H2211 I2C EEPROM.
 *  \param eepromBlock index of the block to write
 *  \param blkdata 16-byte array containing data to write
 */
int nt3h_writetag(int eepromBlock, char * blkdata)
{
    int i=0;

    // Do not overwrite the serial number and slave address.

    i2c_write_block(DEVADDR, eepromBlock, BLOCKSIZE, blkdata);

    return 0;
}

/*! \brief Read a 16-byte block from the NT3H2211 I2C EEPROM.
 *  \param eepromBlock index of the block to read.
 *  \param blkdata 16-byte array into which the EEPROM block contents will be stored.
 */
int nt3h_readtag(int eepromBlock, char * blkdata)
{
    i2c_read_block(DEVADDR, eepromBlock, BLOCKSIZE, blkdata, 0xFF);

    return 0;
}

int nt3h_eepromwritedone(void)
{
    int nsreg = i2c_readreg(DEVADDR, 0xFE, 6);

    return (nsreg & 0x02);
}
