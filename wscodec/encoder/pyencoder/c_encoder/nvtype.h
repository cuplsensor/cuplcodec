/*!
 * @file nvtype.h
 * @brief A file for organising configuration data stored in Non-Volatile memory.
 *
 * These data are read by several parts of the encoder, where it is declared as an external global variable.
 *
 * The variable definition depends on how the encoder is being run:
 * - When running under CFFI (see PyEncoder) #nv is defined in nvtype.c
 * - When running as part of a larger project (e.g. the cupl Tag firmware) nv must be defined elsewhere.
 *
 * The intention is for nv to occupy the 512 byte MSP430 <a href="https://www.ti.com/document-viewer/MSP430FR2155/datasheet/memory-organization-slasec43899#SLASEC43899">information FRAM</a>.
 *
 * @date 6 Aug 2018
 * @author Malcolm Mackay
 * @copyright Plotsensor Ltd.
 */

#ifndef COMMS_NVTYPE_H_
#define COMMS_NVTYPE_H_


#define SERIAL_LENBYTES       8       /*!< Length of the tag serial string in bytes. */
#define SECKEY_LENBYTES       16      /*!< Length of the secret key used for HMAC-MD5 in bytes. */
#define BASEURL_LENBYTES      64      /*!< Maximum length of the base URL string in bytes. */
#define SMPLINT_LENBYTES      2       /*!< Length of the sample interval (minutes) integer in bytes. */
#define VFMTINT_LENBYTES      3       /*!< VFmt character array length in bytes.*/
#define FORMAT_ASCII_MAXLEN   3       /*!< Maximum length of the format ASCII string. */
#define MINVOLTAGEMV_ASCII_MAXLEN   4       /*!< Maximum length of the minimum voltage (mV) ASCII string. */
#define SMPLINTERVAL_ASCII_MAXLEN   5       /*!< Maximum length of the sample interval string. */

/**
 *  Structure to hold configuration data held in non-volatile memory.
 */
typedef struct nvstruct {
    char serial[SERIAL_LENBYTES];   /*!< Alphanumeric serial of the tag running the cupl encoder.  */
    char seckey[SECKEY_LENBYTES];   /*!< Secret key string used for HMAC-MD5. */
    char smplintervalmins[SMPLINT_LENBYTES]; /*!< Time interval betweeen samples in minutes. */
    char baseurl[BASEURL_LENBYTES];  /*!< URL of the cupl Web Application frontend. */
    char format;                    /*!< Codec format byte. */
    unsigned int minvoltagemv;      /*!< Minimum startup voltage in mV. */
    unsigned int usehmac;           /*!< When non-zero enable HMAC otherwise use MD5 only. */
    unsigned int httpsdisable;      /*!< When non-zero use HTTP in the URL otherwise use HTTPS. */
    unsigned int sleepintervaldays; /*!< Number of days to wait without scans before putting the cupl Tag into deep sleep mode. */
    unsigned int allwritten;        /*!< When non-zero all required NV parameters have been set. */
    unsigned int resetsperloop;     /*!< Incremented each time the tag microcontroller resets. Zeroed when the circular buffer loops around (see ::ds_looparound). */
    unsigned int resetsalltime;     /*!< Incremented each time the tag microcontroller resets. */
} nv_t;

#endif /* COMMS_NVTYPE_H_ */
