#include "sample.h"
#include "octet.h"
#include "ndef.h"
#include "smplhist.h"
#include "prng.h"
#include "defs.h"
#include "batv.h"
#include "base64.h"
#include "nvtype.h"
#include <stdint.h>

#define LOWBAT_BIT       0x01
#define SCANTIMEOUT_BIT  0x02

#define TEMPRH          '1'
#define TEMPONLY        '2'

typedef enum {
    first_tick,
    first_tock,
    final_tick,
    final_tock
} urlstate;


typedef struct status
{
    uint16_t loopcount;
    uint16_t status;
    uint16_t batvoltage;
} stat_t;

typedef struct endstop
{
  char md5lenb64[12];
  char markerb64[4];
} endstop_t;

static char encodedoctet[8];
static sdchars_t samplebuf[2];
static unsigned int lensmpls = 0;
static urlstate state;
static stat_t urlstatus = {0};
static endstop_t endstop;
static bool _temponly;
extern nv_t nv;

static void sample_updatelc(void)
{
  char statusb64[9];

  urlstatus.loopcount += 1;
  //urlstatus.status = stat_get(&err);
  urlstatus.batvoltage = batv_measure();

  Base64encode(statusb64, (const char *)&urlstatus, sizeof(urlstatus));
  ndef_writepreamble(BUFLEN_BLKS, statusb64);
  octet_restore();
}

void sample_init(unsigned int stat, bool err, bool temponly)
{
  char statusb64[9];
  int startblk;
  int buflenblks;
  char ver;

  urlstatus.loopcount = 0;
  urlstatus.status = stat;
  urlstatus.batvoltage = batv_measure();
  Base64encode(statusb64, (const char *)&urlstatus, sizeof(urlstatus));

  lensmpls = 0;
  state = first_tick;

  if (err == true)
  {
      buflenblks = 0;
  }
  else
  {
      buflenblks = BUFLEN_BLKS;
  }

  _temponly = temponly;

  if (_temponly == true)
  {
    ver = TEMPONLY;
  }
  else
  {
    ver = TEMPRH;
  }

  ndef_writeblankurl(buflenblks, statusb64, &startblk, ver);
  octet_init(startblk, buflenblks);
  prng_init(nv.randstate);

}

static void makemarker(unsigned int minutes, char * endmarker)
{
    unsigned int minutesixb;
    unsigned int randomtenb;

    minutesixb = minutes & 0x3F; // Select lower 6 bits of the minutes field.
    randomtenb = 5; //prng_getrandom(10);

    *(endmarker) = minutesixb + ((randomtenb & 0x03)<<6);
    *(endmarker + 1) = randomtenb >> 2;
}

static void makeendstop(unsigned int minutes)
{
    char endmarker[2];
    makemarker(minutes, endmarker);
    Base64encode(endstop.markerb64, endmarker, sizeof(endmarker));
    // Change padding byte.
    endstop.markerb64[3] = '~';
}

void sample_updateendstop(unsigned int minutes)
{
    makeendstop(minutes);
    octet_write(Octet2, &endstop.md5lenb64[8]);
    octet_commit2();
}

static void loadboth(sdchars_t *sample, int meas1, int meas2)
{
    sample->m1Msb = ((meas1 >> 4) & 0xFF);
    sample->m2Msb = ((meas2 >> 4) & 0xFF);
    sample->Lsb = ((meas1 & 0xF) << 4) | (meas2 & 0xF);
}

static void loadm2(sdchars_t *sample, int meas2)
{
    sample->m2Msb = ((meas2 >> 4) & 0xFF);
    sample->Lsb &= ~0x0F; // Clear low nibble of LSB.
    sample->Lsb |= (meas2 & 0xF); // Set low nibble of LSB.
}

/*!
 * \fn sample_push
 * \brief Append a sample containing up to two measurands onto the circular buffer.
 *
 * \param meas1 measurand 1 e.g. temperature.
 * \param meas2 measurand 2 e.g. relative humidity.
 *
 * \returns 1 if the cursor has moved from the end to the start and data are being overwritten.
 * Otherwise 0.
 */
int sample_push(int meas1, int meas2)
{
  urlstate nextstate;
  md5len_t md5length;

  if (_temponly == true)
  {
      meas2 = -1;
  }

  if ((state == first_tick) && (lensmpls != 0))
  {
      octet_movecursor();
  }

  OctState_t octetstate = octet_getstate();

  switch(state)
      {
      case first_tick:
          loadboth(&samplebuf[0], meas1, meas2);
          loadboth(&samplebuf[1], 0, 0);
          if (octetstate != firstloop)
          {
              lensmpls -= SAMPLES_PER_OCTET;
          }
          if (octetstate == loopingaround)
          {
            sample_updatelc();
          }
          lensmpls++;

          smplhist_push(samplebuf[0]);

          if (_temponly)
          {
              nextstate = first_tock;
          }
          else
          {
              nextstate = final_tick;
          }
          break;

      case first_tock:
          loadm2(&samplebuf[0], meas1);
          smplhist_ovr(samplebuf[0]);
          nextstate = final_tick;
          break;

      case final_tick:
          loadboth(&samplebuf[1], meas1, meas2);
          lensmpls++;

          smplhist_push(samplebuf[1]);

          if (_temponly)
          {
              nextstate = final_tock;
          }
          else
          {
              nextstate = first_tick;
          }
          break;

      case final_tock:
          loadm2(&samplebuf[1], meas1);
          smplhist_ovr(samplebuf[1]);
          nextstate = first_tick;
          break;
      }

      md5length = smplhist_md5(lensmpls, true);

      // 3 samples (6 bytes) per 8 base64 bytes.
      Base64encode(encodedoctet, (char *)samplebuf, sizeof(samplebuf));
      // 9 bytes per 12 base64 bytes.
      Base64encode(endstop.md5lenb64, (char *)&md5length, sizeof(md5length));

      makeendstop(0);

      octet_write(Octet0, encodedoctet);
      octet_write(Octet1, &endstop.md5lenb64[0]);
      octet_write(Octet2, &endstop.md5lenb64[8]);
      octet_commit4();

      state = nextstate;

      return (octetstate == loopingaround);
}
