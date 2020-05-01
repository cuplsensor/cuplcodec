#include "sample.h"
#include "demi.h"
#include "ndef.h"
#include "pairhist.h"
#include "defs.h"
#include "batv.h"
#include "base64.h"
#include "nvtype.h"
#include <stdint.h>

#define TEMPRH          '1' /*!< Last character of the URL version string if the URL contains both temperature and relative humidity measurands. */
#define TEMPONLY        '2' /*!< Last character of the URL version string if the URL contains only temperature measurands. */
#define ENDSTOP_BYTE    '~' /*!< Last character of the endstop. Must be URL safe according to RFC 1738. */

#define BATV_RESETCAUSE(BATV, RSTC) ((BATV << 8) | (RSTC & 0xFF))

typedef enum {
    pair0_both,         /*!< Write both meaurands in the first sample of \link pairbuf */
    pair0_reading1,     /*!< Overwrite measurand 2 in the first sample of \link pairbuf */
    pair1_both,         /*!< Write both measurands in the second sample of \link pairbuf */
    pair1_reading1      /*!< Overwrite measurand 2 in the second sample of \link pairbuf */
} pairbufstate_t;       /*!< Indicates which reading(s) in the \link pairbuf are being written.*/

typedef struct
{
    uint16_t loopcount;  /*!< Number of times the last demi in the circular buffer endstop has wrapped from the end of the buffer to the beginning. */
    uint16_t resetsalltime;     /*!< 2-byte status. Bits are set according to stat_bits.h */
    uint16_t batv_resetcause;   /*!< Battery voltage in mV */
} stat_t;

typedef struct
{
  char md5lenb64[12];   /*!< MD5 length field containing a base64 encoded ::md5len_t. */
  char markerb64[4];    /*!< End-stop marker comprised of base64 encoded minutes since the previous sample and ::ENDSTOP_BYTE */
} endstop_t;

static char demib64[8];             /*!< Stores two pairs from \link pairbuf, after base64 encoding */
static pair_t pairbuf[2];           /*!< Stores two unencoded 3-byte pairs. */
static unsigned int lenpairs = 0;   /*!< Number of base64 encoded pairs in the circular buffer, starting from the endstop and counting backwards. */
static pairbufstate_t state;        /*!< Pair buffer write state. */
static endstop_t endstop;           /*!< The 16 byte end stop. */
extern nv_t nv;                     /*!< Externally defined parameters stored in non-volatile memory. */

#ifndef NOT_CFFI
stat_t status = {0};
#else
static stat_t status = {0};
#endif




/*!
 * @brief Update loop counter and battery voltage in the preamble status field.
 *
 * Calls a function to measure battery voltage, increases loopcount and clears the battery reset field.
 * These data are base64 encoded and written to EEPROM. ndef_writepreamble overwrites the bufferred circular buffer
 * blocks so these must be read again after with demi_restore.
 */
static void sample_updatelc(void)
{
  char statusb64[9];
  uint16_t batv = batv_measure();                           // Measure battery voltage

  status.loopcount += 1;                                 // Increase loopcount by 1.
  status.batv_resetcause = BATV_RESETCAUSE(batv, 0);     // Clear battery reset cause

  Base64encode(statusb64, (const char *)&status, sizeof(status)); // Base64 encode status.
  ndef_writepreamble(BUFLEN_BLKS, statusb64);               // Write URL in EEPROM up to the start of the circular buffer.
  demi_restore();                                           // Re-read circular buffer blocks that were overwritten in the previous operation.
}

/*!
 * @brief Initialise the sample state machine.
 *
 * @param resetcause 16-bit status value.
 * @param err Sets an error condition where data will not be logged to the URL circular buffer.
 */
void sample_init(unsigned int resetcause, bool err)
{
  char statusb64[9];
  int startblk;
  int buflenblks;
  uint16_t batv = batv_measure();

  status.loopcount = 0;
  status.resetsalltime = nv.resetsalltime;
  status.batv_resetcause = BATV_RESETCAUSE(batv, resetcause);
  Base64encode(statusb64, (const char *)&status, sizeof(status));

  lenpairs = 0;
  state = pair0_both;

  if (err == true)
  {
      buflenblks = 0;
  }
  else
  {
      buflenblks = BUFLEN_BLKS;
  }

  ndef_writeblankurl(buflenblks, statusb64, &startblk);
  demi_init(startblk, buflenblks);
}

/**
 * @brief Write the endstop.
 *
 * @param minutes: Minutes elapsed since the previous sample.
 * @param endmarker: Pointer to the end marker byte array.
 */
static void makemarker(unsigned int minutes, char * endmarker)
{
    unsigned int minutesLsb;
    unsigned int minutesMsb;

    minutesLsb = minutes & 0xFF; // Select lower 6 bits of the minutes field.
    minutesMsb = minutes >> 8;

    *(endmarker) = minutesLsb;
    *(endmarker + 1) = minutesMsb;
}

/**
 * @brief Update the endstop and encode it as base64.
 *
 * @param minutes: Minutes elapsed since the previous sample.
 */
static void makeendstop(unsigned int minutes)
{
    char endmarker[2];
    makemarker(minutes, endmarker);
    Base64encode(endstop.markerb64, endmarker, sizeof(endmarker));
    // Change padding byte.
    endstop.markerb64[3] = ENDSTOP_BYTE;
}

/**
 * @brief Update the base64 encoded endstop and write it to the tag.
 *
 * @param minutes: Minutes elapsed since the previous sample.
 */
void sample_updateendstop(unsigned int minutes)
{
    makeendstop(minutes);
    demi_write(Demi2, &endstop.md5lenb64[8]);
    demi_commit2();
}

/**
 * @brief Write both measurands of a sample.
 *
 * @param sample: Pointer to the sample that will be modified.
 * @param meas1: Measurand 1. Only the 12 least sigificant bits will be used.
 * @param meas2: Measurand 2. Only the 12 least sigificant bits will be used.
 */
static void loadboth(pair_t *sample, int meas1, int meas2)
{
    sample->m1Msb = ((meas1 >> 4) & 0xFF);
    sample->m2Msb = ((meas2 >> 4) & 0xFF);
    sample->Lsb = ((meas1 & 0xF) << 4) | (meas2 & 0xF);
}

/**
 * @brief Write measurand 2 of a sample
 *
 * @param sample: Pointer to the sample that will be modified.
 * @param meas2: Measurand 2. Only the 12 least sigificant bits will be used.
 */
static void loadm2(pair_t *sample, int meas2)
{
    sample->m2Msb = ((meas2 >> 4) & 0xFF);
    sample->Lsb &= ~0x0F; // Clear low nibble of LSB.
    sample->Lsb |= (meas2 & 0xF); // Set low nibble of LSB.
}

/**
 * @brief  Append a sample containing up to two measurands onto the circular buffer.
 *
 * @param meas1 Measurand 1 e.g. temperature.
 * @param meas2 Measurand 2 e.g. relative humidity.
 *
 * @returns 1 if the cursor has moved from the end to the start and data are being overwritten.
 * Otherwise 0.
 */
int sample_push(int meas1, int meas2)
{
  pairbufstate_t nextstate;
  md5len_t md5length;
  int cursorpos;

  if (nv.version[1] == TEMPONLY)
  {
      meas2 = -1;
  }

  if ((state == pair0_both) && (lenpairs != 0))
  {
      demi_movecursor();
  }

  OctState_t demistate = demi_getstate();

  switch(state)
      {
      case pair0_both:
          loadboth(&pairbuf[0], meas1, meas2);
          loadboth(&pairbuf[1], 0, 0);
          if (demistate != firstloop)
          {
              lenpairs -= PAIRS_PER_DEMI;
          }
          if (demistate == loopingaround)
          {
            sample_updatelc();
          }
          lenpairs++;

          pairhist_push(pairbuf[0]);

          if (nv.version[1] == TEMPONLY)
          {
              nextstate = pair0_reading1;
          }
          else
          {
              nextstate = pair1_both;
          }
          break;

      case pair0_reading1:
          loadm2(&pairbuf[0], meas1);
          pairhist_ovr(pairbuf[0]);
          nextstate = pair1_both;
          break;

      case pair1_both:
          loadboth(&pairbuf[1], meas1, meas2);
          lenpairs++;

          pairhist_push(pairbuf[1]);

          if (nv.version[1] == TEMPONLY)
          {
              nextstate = pair1_reading1;
          }
          else
          {
              nextstate = pair0_both;
          }
          break;

      case pair1_reading1:
          loadm2(&pairbuf[1], meas1);
          pairhist_ovr(pairbuf[1]);
          nextstate = pair0_both;
          break;
      }

      cursorpos = demi_getendmarkerpos();


      md5length = pairhist_md5(lenpairs, nv.usehmac, status.loopcount, status.resetsalltime, status.batv_resetcause, cursorpos);

      // 2 samples (6 bytes) per 8 base64 bytes.
      Base64encode(demib64, (char *)pairbuf, sizeof(pairbuf));
      // 9 bytes per 12 base64 bytes.
      Base64encode(endstop.md5lenb64, (char *)&md5length, sizeof(md5length));

      makeendstop(0);

      demi_write(Demi0, demib64);
      demi_write(Demi1, &endstop.md5lenb64[0]);
      demi_write(Demi2, &endstop.md5lenb64[8]);
      demi_commit4();

      state = nextstate;

      return (demistate == loopingaround);
}
