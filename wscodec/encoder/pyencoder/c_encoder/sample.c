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

#define BATV_RESETCAUSE(BATV, RSTC) ((BATV << 8) | (RSTC & 0xFF)) /*!< Macro for creating a 16-bit batv_resetcause value from 8-bit CODEC_FEAT_30 and CODEC_SPEC_16 values. */

typedef enum {
    initial,
    pair0_both,         /*!< Write pair0 */
    pair0_reading1,     /*!< Overwrite reading1 of pair0 */
    pair1_both,         /*!< Write pair1 */
    pair1_reading1      /*!< Overwrite reading1 of pair1 */
} pairbufstate_t;       /*!< Indicates which reading(s) in the \link pairbuf are being written.*/

typedef struct
{
    uint16_t loopcount;         /*!< Number of times the last demi in the circular buffer endstop has wrapped from the end to the beginning. */
    uint16_t resetsalltime;     /*!< 2-byte status. Bits are set according to stat_bits.h */
    uint16_t batv_resetcause;   /*!< Battery voltage in mV */
} stat_t;

typedef struct
{
  char hashnb64[12];   /*!< MD5 length field containing a base64 encoded ::hashn_t. */
  char markerb64[4];    /*!< End-stop marker comprised of base64 encoded minutes since the previous sample and ::ENDSTOP_BYTE */
} endstop_t;

typedef struct
{
  char elapsedLSB;      /*!< Minutes elapsed since previous sample (Least Significant Byte). */
  char elapsedMSB;      /*!< Minutes elapsed since previous sample (Most Signficant Byte). */
} endmarker_t;

static unsigned int overwriting;
static char demi[8];                /*!< Stores two pairs from \link pairbuf, after base64 encoding */
static pair_t pairbuf[2];           /*!< Stores two unencoded 3-byte pairs. */
static unsigned int npairs = 0;   /*!< Number of base64 encoded pairs in the circular buffer, starting from the endstop and counting backwards. */
static pairbufstate_t state;        /*!< Pair buffer write state. */
static endstop_t endstop;           /*!< The 16 byte end stop. */
extern nv_t nv;                     /*!< Externally defined parameters stored in non-volatile memory. */

#ifndef NOT_CFFI
stat_t status = {0};                /*!< Structure to hold unencoded status data. */
#else
static stat_t status = {0};         /*!< Structure to hold unencoded status data. */
#endif


/*!
 * @brief Update loop counter and battery voltage in the preamble status field.
 *
 * Calls a function to measure battery voltage, increases loopcount and clears the battery reset field.
 * These data are base64 encoded and written to EEPROM. ndef_writepreamble overwrites the bufferred circular buffer
 * blocks so these must be read again after with demi_restore.
 */
static void incr_loopcounter(void)
{
  char statusb64[9];
  uint16_t batv = batv_measure();                           // Measure battery voltage

  status.loopcount += 1;                                   // Increase loopcount by 1.
  status.batv_resetcause = BATV_RESETCAUSE(batv, 0);       // Clear reset cause because there has not been a reset recently.

  Base64encode(statusb64, (const char *)&status, sizeof(status)); // Base64 encode status. CHECK THIS.
  ndef_writepreamble(BUFLEN_BLKS, statusb64);               // Write URL in EEPROM up to the start of the circular buffer.
}

/**
 * @brief Update the endmarker of the endstop with elapsed time in minutes.
 *
 * @param minutes: Minutes elapsed since the previous sample.
 */
static void set_elapsed(unsigned int minutes)
{
    endmarker_t marker;

    marker.elapsedLSB = minutes & 0xFF; // Lower 8 bits of the minutes field.
    marker.elapsedMSB = minutes >> 8;   // Upper 8 bits of the minutes field.

    Base64encode(endstop.markerb64, (char *)&marker, sizeof(marker));
    endstop.markerb64[3] = ENDSTOP_BYTE;    // Change padding byte.
}

/**
 * @brief Write one pair
 *
 * @param pair: Pointer to the pair that will be modified.
 * @param rd0: Reading 0 (12 bits).
 * @param rd1: Reading 1 (12 bits).
 */
static void set_pair(pair_t *pair, int rd0, int rd1)
{
    pair->rd0Msb = ((rd0 >> 4) & 0xFF);
    pair->rd1Msb = ((rd1 >> 4) & 0xFF);
    pair->Lsb   = ((rd0 & 0xF) << 4) | (rd1 & 0xF);
}

/**
 * @brief Overwrite reading1 in a pair
 * This is used when the format stipulates one reading per pair (see \link CODEC_FEAT_42).
 *
 * @param pair: Pointer to the pair that will be modified.
 * @param rd1: Reading 1 (12 bits).
 */
static void set_rd1(pair_t *pair, int rd1)
{
    pair->rd1Msb  = ((rd1 >> 4) & 0xFF);
    pair->Lsb   &= ~0x0F;           // Clear low nibble of LSB.
    pair->Lsb   |= (rd1 & 0xF);     // Set low nibble of LSB.
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

  overwriting = 0;
  status.loopcount = 0;
  status.resetsalltime = nv.resetsalltime;
  status.batv_resetcause = BATV_RESETCAUSE(batv, resetcause);
  Base64encode(statusb64, (const char *)&status, sizeof(status));

  npairs = 0;
  state = initial;

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
 * @brief Update the base64 encoded endstop and write it to the tag.
 *
 * @param minutes: Minutes elapsed since the previous sample.
 */
void cbuf_setelapsed(unsigned int minutes)
{
    set_elapsed(minutes);
    demi_write(DEMI2, &endstop.hashnb64[8]);
    demi_commit2();
}

/**
 * @brief  Push a sample containing up to two readings onto the circular buffer.
 *
 * @param rd0 First reading in the sample e.g. temperature.
 * @param rd1 Second reading in the sample (optional) e.g. relative humidity.
 *
 * @returns 1 if the cursor has moved from the end to the start and data are being overwritten.
 * Otherwise 0.
 */
int cbuf_pushsample(int rd0, int rd1)
{
  pairbufstate_t nextstate;
  hashn_t hashn;
  int cursorpos;
  DemiState_t demistate;

  if (nv.version[1] == TEMPONLY)
  {
      rd1 = -1;
  }

  switch(state)
      {
      case pair0_both:
          switch(demi_movecursor())
          {
          case ds_looparound:
            overwriting = 1;
            break;
          case ds_newloop:
            incr_loopcounter();
            break;
          default:
            break;
          }
      case initial:
          set_pair(&pairbuf[0], rd0, rd1);
          set_pair(&pairbuf[1], 0, 0);
          npairs = overwriting ? (npairs + 1 - PAIRS_PER_DEMI) : (npairs + 1);
          npairs++;
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
          set_rd1(&pairbuf[0], rd0);
          pairhist_ovr(pairbuf[0]);
          nextstate = pair1_both;
          break;

      case pair1_both:
          set_pair(&pairbuf[1], rd0, rd1);
          npairs++;

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
          set_rd1(&pairbuf[1], rd0);
          pairhist_ovr(pairbuf[1]);
          nextstate = pair0_both;
          break;
      }

      cursorpos = demi_getendmarkerpos();
      hashn = pairhist_hash(npairs, nv.usehmac, status.loopcount, status.resetsalltime, status.batv_resetcause, cursorpos);

      // 2 samples (6 bytes) per 8 base64 bytes.
      Base64encode(demi, (char *)pairbuf, sizeof(pairbuf));
      // 9 bytes per 12 base64 bytes.
      Base64encode(endstop.hashnb64, (char *)&hashn, sizeof(hashn));

      set_elapsed(0);

      demi_write(DEMI0, demi);
      demi_write(DEMI1, &endstop.hashnb64[0]);
      demi_write(DEMI2, &endstop.hashnb64[8]);
      demi_commit4();

      state = nextstate;

      return (demistate == ds_looparound);
}
