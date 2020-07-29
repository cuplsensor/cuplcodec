#ifndef _SAMPLE_H_
#define _SAMPLE_H_

#include <stdbool.h>


void enc_init(unsigned int status, bool err, unsigned int batv);
int enc_pushsample(int rd0, int rd1);
void enc_setelapsed(unsigned int minutes);
unsigned int enc_getbatv(void);

#endif //_SAMPLE_H_
