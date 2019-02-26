/*
 * prng.h
 *
 *  Created on: 29 Jun 2018
 *      Author: malcolm
 */

#ifndef URLENCODER_PRNG_H_
#define URLENCODER_PRNG_H_

void prng_init(unsigned int initialrstate);
unsigned int prng_getrandom(unsigned int lenbits);

#endif /* URLENCODER_PRNG_H_ */
