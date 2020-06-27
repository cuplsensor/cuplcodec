#ifndef _SAMPLE_H_
#define _SAMPLE_H_

#include <stdbool.h>


void enc_init(unsigned int status, bool err);
int enc_pushsample(int rd0, int rd1);
void enc_setelapsed(unsigned int minutes);

#endif //_SAMPLE_H_
