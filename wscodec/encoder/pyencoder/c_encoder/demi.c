#include "eep.h"
#include "demi.h"
#include "defs.h"

#define DEMI_TO_BLK(demi) (_startblk + (demi >> 1))
#define MAX_CURSORDEMI  (_lendemis - 1)


static int _endblk = 0;
static int _startblk = 0;

static int _cursorblk;
static int _nextblk;

static int _lendemis = 0;
static int _cursordemi = 0;
static OctState_t _demistate = firstloop;

/*!
 * @brief Read 4 demis (32 bytes) from EEPROM into RAM starting from the cursor block.
 *
 * This is 2 demis from the cursor block and 2 demis from the block after it (_nextblk).
 * If cursor block is at the end of the buffer, then _nextblk will be at the start. This
 * makes the buffer circular.
 *
 * Static variables ::_cursorblk and _nextblk are updated by this function.
 *
 * @param cursorblk EEPROM block number where the cursor is located.
 * @returns looparound 1 if a read has looped around from the end to the beginning of the buffer. 0 otherwise.
 */
static int demi_read4(const int cursorblk)
{
  int looparound = 0;

  if (cursorblk == _endblk)
  {
    _cursorblk = cursorblk;
    _nextblk = _startblk;
    looparound = 1;
  }
  else
  {
    _cursorblk = cursorblk;
    _nextblk = _cursorblk + 1;
  }

  // Read the contents of EEPROM block _cursorblk into RAM buffer location 0.
  eep_read(_cursorblk, 0);
  // Read the contents of EEPROM block _nextblk into RAM buffer location 1.
  eep_read(_nextblk, 1);

  return looparound;
}

void demi_restore(void)
{
  demi_read4(_cursorblk);
}

/*!
 * @brief Initialise a circular buffer of 8-byte demis.
 *
 * Sets counters to intial values and calls ::demi_read4 to read the first 4
 * demis into RAM.
 *
 * @param startblk EEPROM block to start the circular buffer.
 * @param lenblks Length of circular buffer in EEPROM blocks.
 */
int demi_init(const int startblk, const int lenblks)
{
  _startblk = startblk;
  _endblk = startblk+lenblks-1;

  _cursorblk = startblk;
  _nextblk = _cursorblk + 1;

  // Calculate the number of demis.
  _lendemis = lenblks*DEMIS_PER_BLK;
  _cursordemi = 0;
  _demistate = firstloop;

  demi_read4(startblk);

  return 0;
}

/*!
 * @brief Write 4 demis from RAM to the EEPROM.
 *
 * 2 demis are written from RAM buffer location 0 into the EEPROM block ::_cursorblk.
 * 2 demis are written from RAM buffer location 1 into the EEPROM block ::_nextblk.
 * @returns 0
 */
int demi_commit4(void)
{
  eep_write(_cursorblk, 0);
  eep_write(_nextblk, 1);
  eep_waitwritedone();

  return 0;
}

/*!
 * @brief Write the last 2 demis from RAM to the EEPROM.
 *
 * 2 demis are written from RAM buffer location 1 into the EEPROM block _nextblk.
 * Some functions only need to modify the last 2 demis so this saves time and energy over writing 4.
 * @returns 0
 */
int demi_commit2(void)
{
  eep_write(_nextblk, 1);
  eep_waitwritedone();

  return 0;
}

/*!
 * @brief Overwrite one demi in the RAM buffer. demi::demi_read4()
 *
 * This function takes demiindex as relative to _cursordemi.
 * The function to modify the RAM buffer ::eep_cp requires an index relative to \link ::_cursorblk \endlink (it has no concept of demis).
 * There are 2 8-byte demis per 16-byte block.
 * If cursordemi is even, nothing is needs to be done because it lies on a block boundary.
 * If cursordemi is odd then it is offset from the block boundary by one demi. Therefore one is added to demiindex.
 *
 * @param demiindex Demi index to overwrite, relative to _cursordemi. Must be 0, 1 or 2.
 * @param demidata Pointer to an 8 byte array of new demi data.
 */
int demi_write(OctInd_t demiindex, char * demidata)
{
  int errflag = 1;
  int demistart;
  int octindex = (int)demiindex;
  // If cursordemi is odd, then demistart is at 1.
  // If cursordemi is even, then demistart is at 0.
  // Demi index must be 0, 1 or 2.
  if ((_cursordemi & 0x01) > 0)
  {
    // ODD. demiindex range is 1,2,3
    octindex += 1;
  }

  errflag = 0;
  demistart = octindex * BYTES_PER_DEMI;
  // Copy data to the buffer
  errflag = eep_cp(&demistart, demidata, BYTES_PER_DEMI);

  return errflag;
}

// Move cursor forward by 1. Add overwriting and looping around as parameters.
int demi_movecursor(void)
{
  int cursorblk;
  int looparound = 0;

  // Increment _cursordemi
  if (_cursordemi == MAX_CURSORDEMI)
  {
    _cursordemi = 0;
  }
  else
  {
    _cursordemi = _cursordemi + 1;
  }

  // Determine if a read is needed.
  cursorblk = DEMI_TO_BLK(_cursordemi);
  if (cursorblk != _cursorblk)
  {
    // Perform a read.
    // Only raise the looparound flag once per loop,
    // when the last demi will be written to the first demi of the first block.
    looparound = demi_read4(cursorblk);
  }

  switch(_demistate)
  {
    case firstloop:
    if (looparound == 1)
    {
      _demistate = loopingaround;
    }
    break;
    case loopingaround:
    _demistate = overwriting;
    break;
    case overwriting:
    if (looparound == 1)
    {
      _demistate = loopingaround;
    }
    break;
  }

  return 0;
}

int demi_getendmarkerpos(void)
{
    // When cursordemi is ODD, the end marker byte is 8 bytes further back.
    return (_nextblk - _startblk)*DEMIS_PER_BLK*BYTES_PER_DEMI + ENDMARKER_OFFSET_IN_ENDSTOP_1 + (_cursordemi & 0x01)*BYTES_PER_DEMI;
}

OctState_t demi_getstate(void)
{
  return _demistate;
}
