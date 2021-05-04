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

#include "eep.h"
#include "nt3h.h"
#include "defs.h"

#define BUFSIZE_BLKS  4
#define BUFSIZE_BYTES (BUFSIZE_BLKS * BLKSIZE)

extern void fram_write_enable(void);        /*!< Enable writes to FRAM. Should be defined in the processor-specific cuplTag project. */
extern void fram_write_disable(void);       /*!< Disable writes to FRAM. Should be defined in the processor-specific cuplTag project. */

#pragma PERSISTENT(_blkbuffer)
char _blkbuffer[BUFSIZE_BLKS * BLKSIZE] = {0};

/*! \brief Checks if a byte index is within the bounds the buffer array.
 *
 *  This can be used to prevent the program from accessing memory that is out of bounds.
 * 
 *  \param byteindex Index of a buffer byte that is to be read or written.
 *  \returns 0 if the index is less than the size of the buffer
 *  and can be accessed safely. Otherwise 1.
 */
static inline int inbounds(int byteindex)
{
  return ((byteindex >= 0) && (byteindex < BUFSIZE_BYTES));
}

/*! \brief Write a 16-byte block from the buffer to EEPROM.
 *  \param eepblk Block of the EEPROM to write to.
 *  \param bufblk Block of the buffer to write from.
 *
 *  \returns 1 if the block to be written greater than the buffer size. 0 on success and -1 on write error.
 */
int eep_write(const int eepblk, const unsigned int bufblk)
{
  int errflag = 1;
  int startbyte = bufblk * BLKSIZE;
  if (bufblk < BUFSIZE_BLKS)
  {
    errflag = nt3h_writetag(eepblk+1, &_blkbuffer[startbyte]);
  }

  return errflag;
}

/*! \brief Block until the EEPROM block write has finished.
 *
 *  Writes of Flash memory take some milliseconds to complete.
 */
void eep_waitwritedone()
{
    while(nt3h_eepromwritedone() != 0);
}

/*! \brief Read a 16-byte block from EEPROM to the buffer.
 *  \param eepblk EEPROM block to read.
 *  \param bufblk Block of the buffer to copy the EEPROM contents to.
 */
int eep_read(const int eepblk, const unsigned int bufblk)
{
  int errflag = 1;
  int startbyte = bufblk * BLKSIZE;
  if (bufblk < BUFSIZE_BLKS)
  {
    fram_write_enable();
    nt3h_readtag(eepblk+1, &_blkbuffer[startbyte]);
    fram_write_disable();
    errflag = 0;
  }

  return errflag;
}

/*!
 * @brief Swap two buffer blocks
 * @param srcblk    The buffer block to read from.
 * @param destblk   The buffer block to write to.
 */
int eep_swap(const unsigned int srcblk, const unsigned int destblk)
{
    int errflag = 1;
    int i=0;

    if ((srcblk < BUFSIZE_BLKS) && (destblk < BUFSIZE_BLKS))
    {
        for (i=0; i<BUFSIZE_BLKS; i++)
        {
            fram_write_enable();
            _blkbuffer[destblk + i] = _blkbuffer[srcblk + i];
            fram_write_disable();
        }
        errflag = 0;
    }

    return errflag;
}

/*! \brief Copy data from a pointer into the buffer.
 *  \param indexptr Data are copied into the buffer starting from this index.
 *  An integer from 0 to N-1, where N is the size of the buffer.
 *  indexptr is overwritten by the index one greater than the last data to be written.
 *  \param dataptr Data are copied from this pointer.
 *  \param lenbytes The number of bytes to copy into the buffer from dataptr.
 *  \returns 0 if the data to be copied will fit entirely in the buffer. Otherwise 1.
 */
int eep_cp(int * indexptr, const char * dataptr, const int lenbytes)
{
  int startbyte = *indexptr;
  int endbyte = startbyte + lenbytes - 1;
  int errflag = 1;
  int i;

  if (inbounds(startbyte) && inbounds(endbyte))
  {
    for (i=0; i<lenbytes; i++)
    {
        fram_write_enable();
        _blkbuffer[startbyte + i] = *(dataptr + i);
        fram_write_disable();
    }
    *indexptr = endbyte + 1;
    errflag = 0;
  }

  return errflag;
}

/*! \brief Copy one byte into the buffer.
 *  \param indexptr The byte is copied into this index of the buffer.
 *  An integer from 0 to N-1, where N is the size of the buffer.
 *  indexptr is overwritten by indexptr+1.
 *  \param bytedata Byte to be copied into the buffer.
 *  \returns 0 if indexptr is an index that will not overflow the buffer. Otherwise 1.
 */
int eep_cpbyte(int * indexptr, const char bytedata)
{
  int errflag = 1;

  if (inbounds(*indexptr))
  {
    fram_write_enable();
    _blkbuffer[*indexptr] = bytedata;
    fram_write_disable();
    (*indexptr) = (*indexptr) + 1;
    errflag = 0;
  }

  return errflag;
}
