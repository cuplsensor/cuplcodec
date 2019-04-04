/*
 * nvtype.h
 *
 *  Created on: 6 Aug 2018
 *      Author: malcolm
 */

#ifndef COMMS_NVTYPE_H_
#define COMMS_NVTYPE_H_


#define SERIAL_LENBYTES     8  /*!< Length of unique box serial. */
#define SECKEY_LENBYTES     16
#define BASEURL_LENBYTES    64
#define SMPLINT_LENBYTES     2
#define VERSION_LENBYTES      2
#define INTEGERFIELD_LENBYTES   4

/**
 *  Structure to hold configuration data held in non-volatile memory.
 */
typedef struct nvstruct {
    char serial[SERIAL_LENBYTES];   /*!< Unique serial of the sensor. This must be SERIAL_LENBYTES bytes long.  */
    char seckey[SECKEY_LENBYTES];   /*!< Secret key array. This must be SECKEY_LENBYTES long. This is used to generate the HMAC. */
    char smplintervalmins[SMPLINT_LENBYTES]; /*!< Time interval betweeen samples in minutes. This is b64 encoded so it is easier to store it as an array. */
    char baseurl[BASEURL_LENBYTES]; /*!< The URL or IP address of the web application running PSWebApp. This can be up to BASEURL_LENBYTES bytes long. */
    char version[VERSION_LENBYTES];  /*!< Version. */
    unsigned int usehmac;           /*!< Enable HMAC otherwise use MD5 only. */
    unsigned int httpsdisable;      /*!< Disable HTTPS and use HTTP. */
    unsigned int sleepintervaldays; /*!< The number of days to wait without scans before putting the sensor into deep sleep mode. */
    unsigned int allwritten;        /*!< Indicates that all required NV parameters have been set. */
    unsigned int resetsperloop;     /*!< Incremented each time the microcontroller resets. Zeroed when the circular buffer has wraps from the end back to the beginning. */
    unsigned int resetsalltime;     /*!< Incremented each time the microcontroller resets. */
} nv_t;

#endif /* COMMS_NVTYPE_H_ */
