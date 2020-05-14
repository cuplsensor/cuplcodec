/*
 * nvtype.h
 *
 *  Created on: 6 Aug 2018
 *      Author: malcolm
 */

#ifndef COMMS_NVTYPE_H_
#define COMMS_NVTYPE_H_


#define SERIAL_LENBYTES       8       /*!< Length of the tag serial string in bytes. */
#define SECKEY_LENBYTES       16      /*!< Length of the secret key used for HMAC-MD5 in bytes. */
#define BASEURL_LENBYTES      64      /*!< Maximum length of the base URL string in bytes. */
#define SMPLINT_LENBYTES      2       /*!< Length of the sample interval (minutes) integer in bytes. */
#define VERSION_LENBYTES      2       /*!< Length of the version string in bytes. */

/**
 *  Structure to hold configuration data held in non-volatile memory.
 */
typedef struct nvstruct {
    char serial[SERIAL_LENBYTES];   /*!< Alphanumeric serial of the tag running the cupl encoder.  */
    char seckey[SECKEY_LENBYTES];   /*!< Secret key string used for HMAC-MD5. */
    char smplintervalmins[SMPLINT_LENBYTES]; /*!< Time interval betweeen samples in minutes. */
    char baseurl[BASEURL_LENBYTES];  /*!< URL of the cupl Web Application frontend. */
    char version[VERSION_LENBYTES];  /*!< Version string. */
    unsigned int usehmac;           /*!< When non-zero enable HMAC otherwise use MD5 only. */
    unsigned int httpsdisable;      /*!< When non-zero use HTTP in the URL otherwise use HTTPS. */
    unsigned int sleepintervaldays; /*!< Number of days to wait without scans before putting the cupl Tag into deep sleep mode. */
    unsigned int allwritten;        /*!< When non-zero all required NV parameters have been set. */
    unsigned int resetsperloop;     /*!< Incremented each time the tag microcontroller resets. Zeroed when the circular buffer loops around (see ::ds_looparound). */
    unsigned int resetsalltime;     /*!< Incremented each time the tag microcontroller resets. */
} nv_t;

#endif /* COMMS_NVTYPE_H_ */
