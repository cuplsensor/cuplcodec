#ifndef _SAMPLE_H_
#define _SAMPLE_H_

#include <stdbool.h>


/**
 * @brief Initialise the sample state machine.
 *
 * @param stat Status
 * @param err Error flag
 * @param temponly Configure for temperature only in each sample.
 */
void sample_init(unsigned int status, bool err, bool temponly);

/**
 * @brief  Append a sample containing up to two measurands onto the circular buffer.
 *
 * @param meas1 measurand 1 e.g. temperature.
 * @param meas2 measurand 2 e.g. relative humidity.
 *
 * @returns 1 if the cursor has moved from the end to the start and data are being overwritten.
 * Otherwise 0.
 */
int sample_push(int meas1, int meas2);
void sample_updateendstop(unsigned int minutes);

#endif //_SAMPLE_H_
