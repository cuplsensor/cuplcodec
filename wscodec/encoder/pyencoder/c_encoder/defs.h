#define BYTES_PER_OCTET     8
#define OCTETS_PER_BLK      2
#define SAMPLES_PER_OCTET   2
#define BYTES_PER_SAMPLE    2
#define BUFLEN_BLKS         32  /* Length of the circular buffer in 16-byte blocks. */
#define ENDSTOP_BLKS        1
#define ENDMARKER_OFFSET_IN_ENDSTOP_1 7
#define BLKSIZE 0x10


#define BUFLEN_SAMPLES (SAMPLES_PER_OCTET * OCTETS_PER_BLK * (BUFLEN_BLKS - ENDSTOP_BLKS))
