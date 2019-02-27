#include "ndef.h"
#include "base64.h"
#include "eep.h"
#include "defs.h"
#include "nvtype.h"

extern nv_t nv;

#define URL_RECORDTYPE      0x55
#define URL_RECORDTYPE_LEN  1

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
static const char verparam[] = "&v=0";
static char _ver = 0;
static const char statparam[] = "&x=";
static const char timeintparam[] = "t=";
static const char url[] = "plotsensor.com/?";
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

    int id = 1;

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
    if (rheader.byte.idpresent == 1)
    {
        eep_cpbyte(eepindex, idLength);
    }

    if (typeLength > 0)
    {
        eep_cpbyte(eepindex, recordType);
    }

    if (rheader.byte.idpresent == 1)
    {
        eep_cpbyte(eepindex, id);
    }

    eep_cpbyte(eepindex, URI_ID_HTTPS); // WWW or FTP
}

int ndef_writepreamble(int qlenblks, char * statusb64)
{
  int msglenbytes = ((qlenblks + PREAMBLEN_BLKS) * BLKSIZE_BYTES) - TLSIZE_BYTES;
  char timeintb64[5] = {0};
  int errflag = 0;
  int blk;
  int eepindex = 0;
  char * serial = nv.serial;
  char * timeinterval = nv.smplintervalmins;

  /* qlenblks must be even */
  if ((qlenblks & 0x01) != 0)
  {
      errflag = 1;
  }

  // TLV Message Type
  eep_cpbyte(&eepindex, TLV_START);

  // TLV Message Length
  eep_cpbyte(&eepindex, 0xFF);
  eep_cpbyte(&eepindex, ((msglenbytes & 0xFF00) >> 8));
  eep_cpbyte(&eepindex, (msglenbytes & 0x00FF)); //Remove 0xFE TLV start, TLV length and TLV end. That is 3 bytes in all.

  // Start NDEF record
  ndef_createurlrecord(&eepindex, msglenbytes);

  Base64encode(timeintb64, timeinterval, SMPLINT_LENBYTES);

  // Append URL
  eep_cp(&eepindex, url, sizeof(url)-1);
  // Append time interval header
  eep_cp(&eepindex, timeintparam, sizeof(timeintparam)-1);
  // Append time interval value
  eep_cp(&eepindex, timeintb64, sizeof(timeintb64)-1);
  // Append serial param
  eep_cp(&eepindex, serialparam, sizeof(serialparam)-1);
  // Append serial
  eep_cp(&eepindex, serial, SERIAL_LENBYTES);
  // Append version param
  eep_cp(&eepindex, verparam, sizeof(verparam)-1);
  // Append version
  eep_cp(&eepindex, &_ver, 1);
  // Append status header
  eep_cp(&eepindex, statparam, sizeof(statparam)-1);
  // Append status data
  eep_cp(&eepindex, statusb64, 8);
  // Append padding
  //ndef_append(&blkptr, padparam);
  // Append query string
  eep_cp(&eepindex, queryparam, sizeof(queryparam)-1);

  //ndef_pad(&blkptr, endptr);

  // Write the first 64 bytes to memory.
  for(blk=0; blk<PREAMBLEN_BLKS; blk++)
  {
      eep_write(blk, blk);
  }

  eep_waitwritedone();

  return errflag;
}

int ndef_writeblankurl(int qlenblks, char * statusb64, int * qstartblk, char ver)
{
    int eepindex;
    int i, blk, errflag;

    _ver = ver;

    errflag = ndef_writepreamble(qlenblks, statusb64);

    *qstartblk = PREAMBLEN_BLKS;

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
