#ifndef _NDEF_H_
#define _NDEF_H_

#include <stdbool.h>


void ndef_writeblankurl(int buflenblks, char * statusb64, int * bufstartblk);
int ndef_writepreamble(int buflenblks, char * statusb64);
void ndef_calclen(int * paddinglen, int * preamblenbytes, int * urllen);

#endif //_NDEF_H_
