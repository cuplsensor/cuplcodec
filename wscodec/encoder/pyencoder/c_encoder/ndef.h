#ifndef _NDEF_H_
#define _NDEF_H_

#define BLKSIZE_BYTES   0x10
#define BLKSIZE_POW2    4
#define TLSIZE_BYTES    4

#include <stdbool.h>


void ndef_writeblankurl(int buflenblks, char * statusb64, int * bufstartblk);
int ndef_writepreamble(int buflenblks, char * statusb64);
void ndef_calclen(int * paddinglen, int * preamblenbytes, int * urllen);

#endif //_NDEF_H_
