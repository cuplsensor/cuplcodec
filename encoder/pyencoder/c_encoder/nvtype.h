/*
 * nvtype.h
 *
 *  Created on: 6 Aug 2018
 *      Author: malcolm
 */

#ifndef COMMS_NVTYPE_H_
#define COMMS_NVTYPE_H_


#define SERIAL_LENBYTES     8
#define SECKEY_LENBYTES     8
#define SMPLINT_LENBYTES     2
#define RANDSTATE_LENBYTES      4
#define INTEGERFIELD_LENBYTES   4


typedef struct nvstruct {
    char serial[SERIAL_LENBYTES];
    char seckey[SECKEY_LENBYTES];
    char smplintervalmins[SMPLINT_LENBYTES];
    unsigned int randstate;
    unsigned int sleepintervaldays;
    unsigned int allwritten;
    unsigned int resetsperloop;
    unsigned int resetsalltime;
} nv_t;

#endif /* COMMS_NVTYPE_H_ */
