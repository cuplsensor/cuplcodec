#include "eep.h"
#include "nt3h.h"
#include "defs.h"

#define BUFSIZE_BLKS  4
#define BUFSIZE_BYTES (BUFSIZE_BLKS * BLKSIZE)

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
 *  \returns 1 if the block to be written greater than the buffer size. Otherwise 0.
 */
int eep_write(const int eepblk, const unsigned int bufblk)
{
  int errflag = 1;
  int startbyte = bufblk * BLKSIZE;
  if (bufblk < BUFSIZE_BLKS)
  {
    nt3h_writetag(eepblk+1, &_blkbuffer[startbyte]);
    errflag = 0;
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
    nt3h_readtag(eepblk+1, &_blkbuffer[startbyte]);
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
            _blkbuffer[destblk + i] = _blkbuffer[srcblk + i];
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
      _blkbuffer[startbyte + i] = *(dataptr + i);
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
    _blkbuffer[*indexptr] = bytedata;
    (*indexptr) = (*indexptr) + 1;
    errflag = 0;
  }

  return errflag;
}
