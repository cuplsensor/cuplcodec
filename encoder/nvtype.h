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
#define RANDSTATE_LENBYTES      4
#define INTEGERFIELD_LENBYTES   4


typedef struct nvstruct {
    unsigned int randstate;
    int smplintervalmins;
    int sleepintervaldays;
    int allwritten;
    int resetsperloop;
    int resetsalltime;
    char serial[SERIAL_LENBYTES];
    char seckey[SECKEY_LENBYTES];
} nv_t;

#ifndef NOT_CFFI
nv_t nv;
#endif

#endif /* COMMS_NVTYPE_H_ */
