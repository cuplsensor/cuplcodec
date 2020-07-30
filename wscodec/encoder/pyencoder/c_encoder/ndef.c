#include "ndef.h"
#include "base64.h"
#include "eep.h"
#include "defs.h"
#include "nvtype.h"

extern nv_t nv;

#define URL_RECORDTYPE      0x55                /*!< NDEF record type for a URL. */
#define URL_RECORDTYPE_LEN  1                   /*!< Length of the NDEF record type in bytes. */

#define SMPLINTKEY_LEN  sizeof(smplintkey)-1    /*!< Length of the sample interval key string in bytes. */
#define SMPLINTB64_LEN  4                       /*!< Length of the encoded sample interval string in bytes. */
#define SERIALKEY_LEN   sizeof(serialkey)-1     /*!< Length of the serial key string in bytes. */
#define VERKEY_LEN      sizeof(verkey)-1        /*!< Length of the vfmt key string in bytes. */
#define VFMTB64_LEN     4                       /*!< Length of the encoded VFmt data in bytes. */
#define STATKEY_LEN     sizeof(statkey)-1       /*!< Length of the status key string in bytes. */
#define STATB64_LEN     8                       /*!< Length of the encoded \link #stat_t status \endlink string in bytes. */
#define CBUFKEY_LEN     sizeof(cbufkey)-1       /*!< Length of the circular buffer key string in bytes. */

#define NDEF_RECORD_HEADER_LEN   8           /*!< Length of the NDEF record header in bytes. */
#define TL_LEN            4                  /*!< Length of the Tag and Length fields of the NDEF message TLV in bytes. */

#define TAG_NDEF_MESSSAGE       0x03        /*!< Tag indicating the TLV block contains an NDEF message. */

#define WELLKNOWN_TNF   0x01            /*!< Record Type follows the Record Type Definition (RTD) format. */

#define URI_ID_HTTP     0x03            /*!< URI Identifier Code for the HTTP protocol. */
#define URI_ID_HTTPS    0x04            /*!< URI Identifier Code for the HTTPS protocol. */

typedef union
{
 unsigned char all;
 struct
 {
     unsigned char tnf:3;               /*!< Type Name Format field. */
     unsigned char idpresent:1;         /*!< ID present flag. 1 if the ID field is present. */
     unsigned char srecord:1;           /*!< Short record flag. 1 if the payload length field is 1 byte long. */
     unsigned char chunkflag:1;         /*!< Chunk flag. 1 if this is the first or middle record in a chunked message. */
     unsigned char msgend:1;            /*!< Message end flag. 1 if this is the last record in the message. */
     unsigned char msgbegin:1;          /*!< Message begin flag. 1 if this is the first record in the message. */
 } byte;
} TNFFlags_t;                           /*!< Union for storing the TNF + Flags byte. */

typedef union
{
    unsigned long all;
    unsigned char bytes[4];
} len_t;

static const char serialkey[] = "&s=";             /*!< Seperator, key and equals before the serial string. */
static const char cbufkey[] = "&q=";               /*!< Seperator, key and equals before the circular buffer string. */
static const char verkey[] = "&v=";                /*!< Seperator, key and equals before the vfmt string. */
static const char statkey[] = "&x=";               /*!< Seperator, key and equals before the status string. */
static const char smplintkey[] = "/?t=";           /*!< Start of parameters followed by a key and equals for the sample interval string. */
static const char zeropad[] = "MDAw";              /*!< 4 characters that base64 decode to 0,0,0 */

/*! @brief Create a URL NDEF Record.
 *  @param eepindex Position in the 64-byte array that buffers data to be written into EEPROM.
 *  @param msglenbytes NDEF Message Length in bytes.
 */
static void ndef_createurlrecord(int * eepindex, int msglenbytes, int httpsDisable)
{
    TNFFlags_t tnfflags;
    len_t payloadLength;

    int recordType = URL_RECORDTYPE;
    int typeLength;
    char uriId = URI_ID_HTTPS;

    if (httpsDisable) {
        uriId = URI_ID_HTTP;
    }

    tnfflags.all = 0xD1;
    tnfflags.byte.chunkflag = 0;
    tnfflags.byte.msgend = 1;
    tnfflags.byte.idpresent = 0;
    tnfflags.byte.srecord = 0;
    tnfflags.byte.msgbegin = 1;
    tnfflags.byte.tnf = WELLKNOWN_TNF;
    typeLength = URL_RECORDTYPE_LEN;

    payloadLength.all = msglenbytes-7;

    eep_cpbyte(eepindex, tnfflags.all); // Record header
    eep_cpbyte(eepindex, typeLength);
    eep_cpbyte(eepindex, payloadLength.bytes[3]);
    eep_cpbyte(eepindex, payloadLength.bytes[2]);
    eep_cpbyte(eepindex, payloadLength.bytes[1]);
    eep_cpbyte(eepindex, payloadLength.bytes[0]);
    eep_cpbyte(eepindex, recordType);
    eep_cpbyte(eepindex, uriId); // WWW or FTP
}

void ndef_calclen(int * paddinglen, int * preamblenbytes, int * urllen)
{
    const int preurllen = NDEF_RECORD_HEADER_LEN + TL_LEN;
    const int posturllen_nopadding = SMPLINTKEY_LEN + SMPLINTB64_LEN + SERIALKEY_LEN + SERIAL_LENBYTES + VERKEY_LEN + VFMTB64_LEN + STATKEY_LEN + STATB64_LEN + CBUFKEY_LEN;

    volatile int urllen_nopadding = (posturllen_nopadding + *urllen + preurllen);
    *paddinglen = (BLKSIZE - (urllen_nopadding & 0xF)) & 0xF;
    *preamblenbytes = urllen_nopadding + *paddinglen;
}

/** @brief Write the part of the URL before the circular buffer.
  * @param buflenblks Circular buffer length in 16-byte EEPROM blocks.
  * @param statusb64 Pointer to a base64 encoded  \link #stat_t status \endlink structure.
  * \returns 1 if buflenblks is not even.
  */
int ndef_writepreamble(int buflenblks, char * statusb64)
{
  char smplintb64[SMPLINTB64_LEN+1] = {0};
  char vfmtb64[VFMTB64_LEN+1] = {0};
  int blk = 0;
  int bufblk = 0;
  int eepindex = 0;
  char * serial = nv.serial;
  char * smplinterval = nv.smplintervalmins;
  int blockremaining;
  int padding_remaining;
  int paddinglen;
  int preamblenbytes;
  char vfmt[VFMTINT_LENBYTES];
  char * baseurl = nv.baseurl;
  int urllen = strlen(nv.baseurl); // Get this from the nvparams.
  int urlbytes_remaining = urllen;  // The url bytes still to write.

  // Calculate message length
  ndef_calclen(&paddinglen, &preamblenbytes, &urllen);
  int preamblelenblks = preamblenbytes >> 4;
  int msglenbytes =  ((buflenblks + preamblelenblks) * BLKSIZE) - TL_LEN;

  /* preamblenbytes must be a multiple of 16. */
  if (((preamblenbytes) & 0xF) > 0)
  {
      return -1; // FAULT
  }

  /* buflenblks must be even */
  if ((buflenblks & 0x01) != 0)
  {
      return -2; // FAULT
  }

  /* Encode the sample interval. */
  Base64encode(smplintb64, smplinterval, SMPLINT_LENBYTES);

  /* Prepare the VFmt version, format array. */
  vfmt[0] = (CODEC_VERSION & 0xFF00) >> 8;
  vfmt[1] = (CODEC_VERSION & 0x00FF);
  vfmt[2] = nv.format;
  Base64encode(vfmtb64, vfmt, VFMTINT_LENBYTES);

  // Write TLV Tag field
  eep_cpbyte(&eepindex, TAG_NDEF_MESSSAGE);

  // TLV Message Length
  eep_cpbyte(&eepindex, 0xFF);
  eep_cpbyte(&eepindex, ((msglenbytes & 0xFF00) >> 8));
  eep_cpbyte(&eepindex, (msglenbytes & 0x00FF)); //Remove 0xFE TLV start, TLV length and TLV end. That is 3 bytes in all.

  // Start NDEF record
  ndef_createurlrecord(&eepindex, msglenbytes, nv.httpsdisable);

  // Append URL
  while(urlbytes_remaining > 0) {
      blockremaining = BLKSIZE-eepindex; // Calculate remaining bytes to write in the current block.
      if (urlbytes_remaining > blockremaining)
      {
          eep_cp(&eepindex, baseurl, blockremaining); // Fill the block.
          urlbytes_remaining -= blockremaining;
          eep_write(blk++, 0); // Write block to EEPROM
          eepindex = 0; // Reset eepindex.
          baseurl += blockremaining;
      }
      else
      {
          eep_cp(&eepindex, baseurl, urlbytes_remaining); // Fill the block.
          urlbytes_remaining = 0;
      }
  }

  // Append time interval header
  eep_cp(&eepindex, smplintkey, SMPLINTKEY_LEN);
  // Append time interval value
  eep_cp(&eepindex, smplintb64, SMPLINTB64_LEN);
  // Append serial key
  eep_cp(&eepindex, serialkey, SERIALKEY_LEN);
  // Append serial
  eep_cp(&eepindex, serial, SERIAL_LENBYTES);
  // Append version key
  eep_cp(&eepindex, verkey, VERKEY_LEN);
  // Append padding
  padding_remaining = paddinglen;
  while(padding_remaining)
  {
      eep_cpbyte(&eepindex, '0');
      padding_remaining--;
  }
  // Append version
  eep_cp(&eepindex, vfmtb64, VFMTB64_LEN);
  // Append status header
  eep_cp(&eepindex, statkey, STATKEY_LEN);
  // Append status data
  eep_cp(&eepindex, statusb64, STATB64_LEN);
  // Append circular buffer key
  eep_cp(&eepindex, cbufkey, CBUFKEY_LEN);

  // Write the first 64 bytes to memory.
  while (eepindex > 0)
  {
      eep_write(blk++, bufblk++);
      eepindex -= BLKSIZE;
  }

  eep_waitwritedone();

  return preamblelenblks;
}

/*!
 * @brief Write an NDEF message containing one URL record to EEPROM.
 * @detail The URL contains a circular buffer. This is populated with a placeholder text - all zeroes - initially.
 * @param buflenblks Circular buffer length in 16-byte EEPROM blocks.
 * @param statusb64 Pointer to a base64 encoded  \link #stat_t status \endlink structure.
 * @param bufstartblk The circular buffer start block is written to this pointer.
 */
void ndef_writeblankurl(int buflenblks, char * statusb64, int * bufstartblk)
{
    int preamblelenblks;
    int eepindex;
    int i, blk;

    preamblelenblks = ndef_writepreamble(buflenblks, statusb64);

    if (preamblelenblks < 0)
    {
        return preamblelenblks;
    }

    *bufstartblk = preamblelenblks;

    // Write 2 blocks of padding.
    eepindex = 0;
    for(i=0; i<4; i++)
    {
      eep_cp(&eepindex, zeropad, sizeof(zeropad)-1); // BUG? Not sure about this.
    }

    // Populate the q key with padding.
    for(blk=0; blk<buflenblks; blk++)
    {
        eep_write(*bufstartblk + blk, 0);
    }

    eep_waitwritedone();
}
