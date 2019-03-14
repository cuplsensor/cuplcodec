#ifndef _SAMPLE_H_
#define _SAMPLE_H_

#include <stdbool.h>


void sample_init(unsigned int status, bool err);
int sample_push(int meas1, int meas2);
void sample_updateendstop(unsigned int minutes);

#endif //_SAMPLE_H_
