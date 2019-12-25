/*
 * prng.c
 *
 *  Created on: 29 Jun 2018
 *      Author: malcolm
 */

#include "prng.h"

#define WORDLENBITS 16
/* LCG constants */
#define M 49381                               // Multiplier
#define I 8643                                // Increment

static unsigned int randstate = 0x4D4C;


/**
 * Pseudo-random number generator.
 *
 * Implemented by a 16-bit linear congruential generator.
 * NOTE: Only treat the MSB of the return value as random.
 *
 * @param state Previous state of the generator.
 * @return Next state of the generator.
 */
static inline unsigned int prand() {
    randstate = M * randstate + I;                     // Generate the next state of the LCG
    return randstate;
}

static inline unsigned int prandMSB() {
    return (prand() >> (WORDLENBITS-1));
}

void prng_init(unsigned int initialrstate)
{
    randstate = initialrstate;
}

unsigned int prng_getrandom(unsigned int lenbits)
{
    int i = 0;
    unsigned int randnumber = 0;

    for (i=0; i<lenbits; i++)
    {
        randnumber |= prandMSB();
        randnumber <<= 1;
    }

    return randnumber;
}
