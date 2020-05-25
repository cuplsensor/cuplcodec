#ifndef _NDEF_H_
#define _NDEF_H_

#define BLKSIZE_BYTES   0x10
#define BLKSIZE_POW2    4
#define TLSIZE_BYTES    4

#include <stdbool.h>


/** \brief Create a URL with a blank circular buffer.
  * \param qlenblks Length of the circular buffer URL parameter (q) in blocks.
  * \param statusb64 Pointer to the status field encoded in base 64.
  * \param qstartblk Pointer to an integer into which this function writes the start block of the q URL parameter.
  * \returns 1 if qlenblks is not even.
  *
  * The circular buffer is zero-padded with a base64 demi
  * that decodes to 0,0,0,0,0,0.
  */
void ndef_writeblankurl(int qlenblks, char * statusb64, int * qstartblk);

/** \brief Write the part of the URL before the circular buffer.
  * \param qlenblks Length of the circular buffer in blocks. This is used to calculate the NDEF message length.
  * \param statusb64 Pointer to the status field encoded in base 64.
  * \returns 1 if qlenblks is not even.
  */
int ndef_writepreamble(int qlenblks, char * statusb64);

void ndef_calclen(int * paddinglen, int * preamblenbytes, int * urllen);

#endif //_NDEF_H_
