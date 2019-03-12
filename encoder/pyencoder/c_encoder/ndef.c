#include "ndef.h"
#include "base64.h"
#include "eep.h"
#include "defs.h"
#include "nvtype.h"

extern nv_t nv;

#define URL_RECORDTYPE      0x55
#define URL_RECORDTYPE_LEN  1

#define TIMEINTPARAM_LEN sizeof(timeintparam)-1
#define TIMEINTB64_LEN  4
#define SERIALPARAM_LEN sizeof(serialparam)-1
#define VERPARAM_LEN    sizeof(verparam)-1
#define VERCHAR_LEN     1
#define STATPARAM_LEN   sizeof(statparam)-1
#define STATB64_LEN     8
#define QPARAM_LEN      sizeof(queryparam)-1

#define URL_RECORD_HEADER_LEN   8
#define TLV_TYPE_LEN_LEN        4

#define TLV_START       0x03

#define WELLKNOWN_TNF   0x01
#define ABSURI_TNF      0x03
#define UNCHANGED_TNF   0x06

#define URI_ID_HTTP     0x03
#define URI_ID_HTTPS    0x04

typedef union
{
 unsigned char all;
 struct
 {
     unsigned char tnf:3;
     unsigned char idpresent:1;
     unsigned char srecord:1;
     unsigned char chunkflag:1;
     unsigned char msgend:1;
     unsigned char msgbegin:1;
 } byte;
} RecordHeader_t;

typedef union
{
    unsigned long all;
    unsigned char bytes[4];
} len_t;

char serialparam[] = "&s=";
static const char queryparam[] = "&q=";
static const char verparam[] = "&v=";
static char _ver = 0;
static const char statparam[] = "&x=";
static const char timeintparam[] = "/?t=";
static const char zeropad[] = "MDAw";

/*! \brief Create a URL NDEF Record.
 *  \param eepindex Position in the 64-byte array that buffers data to be written into EEPROM.
 *  \param msglenbytes NDEF Message Length in bytes.
 */
static void ndef_createurlrecord(int * eepindex, int msglenbytes)
{
    RecordHeader_t rheader;
    len_t payloadLength;

    int recordType = URL_RECORDTYPE;
    int typeLength;
    int idLength;

    rheader.all = 0xD1;
    rheader.byte.chunkflag = 0;
    rheader.byte.msgend = 1;
    rheader.byte.idpresent = 0;
    rheader.byte.srecord = 0;
    rheader.byte.msgbegin = 1;
    rheader.byte.tnf = WELLKNOWN_TNF;
    typeLength = URL_RECORDTYPE_LEN;
    idLength = 1;

    payloadLength.all = msglenbytes-7;

    eep_cpbyte(eepindex, rheader.all); // Record header
    eep_cpbyte(eepindex, typeLength);
    eep_cpbyte(eepindex, payloadLength.bytes[3]);
    eep_cpbyte(eepindex, payloadLength.bytes[2]);
    eep_cpbyte(eepindex, payloadLength.bytes[1]);
    eep_cpbyte(eepindex, payloadLength.bytes[0]);
    eep_cpbyte(eepindex, recordType);
    eep_cpbyte(eepindex, URI_ID_HTTPS); // WWW or FTP
}

void ndef_calclen(int * paddinglen, int * preamblenbytes, int * urllen)
{
    const int preurllen = URL_RECORD_HEADER_LEN + TLV_TYPE_LEN_LEN;
    const int posturllen_nopadding = TIMEINTPARAM_LEN + TIMEINTB64_LEN + SERIALPARAM_LEN + SERIAL_LENBYTES + VERPARAM_LEN + VERCHAR_LEN + STATPARAM_LEN + STATB64_LEN + QPARAM_LEN;

//    printint(*urllen);
//    printint(*preamblenbytes);
//    printint(*paddinglen);
//    printint(preurllen);
//    printint(posturllen_nopadding);
    volatile int urllen_nopadding = (posturllen_nopadding + *urllen + preurllen);
    *paddinglen = (BLKSIZE - (urllen_nopadding & 0xF)) & 0xF;
    *preamblenbytes = urllen_nopadding + *paddinglen;
//    printint(*paddinglen);
//    printint(*preamblenbytes);
}

int ndef_writepreamble(int qlenblks, char * statusb64)
{
  char timeintb64[TIMEINTB64_LEN+1] = {0};
  int blk = 0;
  int bufblk = 0;
  int eepindex = 0;
  char * serial = nv.serial;
  char * timeinterval = nv.smplintervalmins;
  int blockremaining;
  int padding_remaining;
  int paddinglen;
  int preamblenbytes;

  char * baseurl = nv.baseurl;
  int urllen = strlen(nv.baseurl); // Get this from the nvparams.
  int urlbytes_remaining = urllen;  // The url bytes still to write.

  // Calculate message length
  ndef_calclen(&paddinglen, &preamblenbytes, &urllen);
  int preamblelenblks = preamblenbytes >> 4;
  int msglenbytes =  ((qlenblks + preamblelenblks) * BLKSIZE_BYTES) - TLSIZE_BYTES;

  /* preamblenbytes must be a multiple of 16. */
  if (((preamblenbytes) & 0xF) > 0)
  {
      return -1; // FAULT
  }

  /* qlenblks must be even */
  if ((qlenblks & 0x01) != 0)
  {
      return -2; // FAULT
  }

  Base64encode(timeintb64, timeinterval, SMPLINT_LENBYTES);

  // TLV Message Type
  eep_cpbyte(&eepindex, TLV_START);

  // TLV Message Length
  eep_cpbyte(&eepindex, 0xFF);
  eep_cpbyte(&eepindex, ((msglenbytes & 0xFF00) >> 8));
  eep_cpbyte(&eepindex, (msglenbytes & 0x00FF)); //Remove 0xFE TLV start, TLV length and TLV end. That is 3 bytes in all.

  // Start NDEF record
  ndef_createurlrecord(&eepindex, msglenbytes);

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
  eep_cp(&eepindex, timeintparam, TIMEINTPARAM_LEN);
  // Append time interval value
  eep_cp(&eepindex, timeintb64, TIMEINTB64_LEN);
  // Append serial param
  eep_cp(&eepindex, serialparam, SERIALPARAM_LEN);
  // Append serial
  eep_cp(&eepindex, serial, SERIAL_LENBYTES);
  // Append version param
  eep_cp(&eepindex, verparam, VERPARAM_LEN);
  // Append padding
  padding_remaining = paddinglen;
  while(padding_remaining)
  {
      eep_cpbyte(&eepindex, '0');
      padding_remaining--;
  }
  // Append version
  eep_cp(&eepindex, &_ver, VERCHAR_LEN);
  // Append status header
  eep_cp(&eepindex, statparam, STATPARAM_LEN);
  // Append status data
  eep_cp(&eepindex, statusb64, STATB64_LEN);
  // Append query string
  eep_cp(&eepindex, queryparam, QPARAM_LEN);

  // Write the first 64 bytes to memory.
  while (eepindex > 0)
  {
      eep_write(blk++, bufblk++);
      eepindex -= BLKSIZE;
  }

  eep_waitwritedone();

  return preamblelenblks;
}

int ndef_writeblankurl(int qlenblks, char * statusb64, int * qstartblk, char ver)
{
    int preamblelenblks;
    int eepindex;
    int i, blk, errflag;

    _ver = ver;

    preamblelenblks = ndef_writepreamble(qlenblks, statusb64);

    if (preamblelenblks < 0)
    {
        return preamblelenblks;
    }

    *qstartblk = preamblelenblks;

    // Write 2 blocks of padding.
    eepindex = 0;
    for(i=0; i<4; i++)
    {
      eep_cp(&eepindex, zeropad, sizeof(zeropad)-1);
    }

    // Populate the q parameter with padding.
    for(blk=0; blk<qlenblks; blk++)
    {
        eep_write(*qstartblk + blk, 0);
    }

    eep_waitwritedone();

    return errflag;
}
