#ifndef _EEP_H_
#define _EEP_H_

int eep_write(const int eepblk, const unsigned int bufblk);
int eep_read(const int eepblk, const unsigned int bufblk);
int eep_swap(const unsigned int srcblk, const unsigned int destblk);
int eep_cp(int * indexptr, const char * dataptr, const int lenbytes);
int eep_cpbyte(int * indexptr, const char bytedata);
void eep_waitwritedone(void);

#endif //_BASE64_H_
