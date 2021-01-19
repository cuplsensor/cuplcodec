#ifndef _DEFS_H_
#define _DEFS_H_

#define CODEC_VERSION       2

#define BYTES_PER_DEMI      8               /*!< The number of bytes per demi. */
#define DEMIS_PER_BLK       2               /*!< The number of demis per block. */
#define PAIRS_PER_DEMI      2               /*!< The number of base64 encoded pairs per demi. */
#define BUFLEN_BLKS         48              /*!< Length of the circular buffer in 16-byte blocks. */
#define ENDSTOP_BLKS        1               /*!< Endstop length in 16-byte blocks. */
#define ENDMARKER_OFFSET_IN_ENDSTOP_1 7
#define BLKSIZE             0x10


#define BUFLEN_PAIRS (PAIRS_PER_DEMI * DEMIS_PER_BLK * (BUFLEN_BLKS - ENDSTOP_BLKS))

#endif
