#include "eep.h"
#include "demi.h"
#include "defs.h"

#define DEMI_TO_BLK(demi) (_startblk + (demi >> 1))
//#define IS_ODD(x)           ((x & 0x01) > 0)

static int _endblk = 0;
static int _startblk = 0;
static int _cursorblk;
static int _nextblk;

static int _enddemi = 0;
static int _cursordemi = 0;

/*!
 * @brief Copy 4 demis from EEPROM into RAM.
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
static void demi_read4()
{
  // Read 2 demis from EEPROM block _cursorblk into RAM buffer location 0.
  eep_read(_cursorblk, 0);
  // Read 2 demis from EEPROM block _nextblk into RAM buffer location 1.
  eep_read(_nextblk, 1);
}


/*!
 * @brief Copy 4 demis from RAM to EEPROM.
 *
 * @returns 0
 */
int demi_commit4(void)
{
  // Write 2 demis from RAM buffer location 0 to _cursorblk.
  eep_write(_cursorblk, 0);
  // Write 2 demis from RAM buffer location 1 to _nextblk.
  eep_write(_nextblk, 1);
  eep_waitwritedone();

  return 0;
}

/*!
 * @brief Write the last 2 demis from RAM to the EEPROM.
 *
 * Some functions only need to modify the last 2 demis so this saves time and energy over writing 4.
 * @returns 0
 */
int demi_commit2(void)
{
  // Write 2 demis from RAM buffer location 1 into _nextblk.
  eep_write(_nextblk, 1);
  eep_waitwritedone();

  return 0;
}

/*!
 * @brief Initialise the EEPROM circular buffer.
 *
 * Reads the first 4 demis in RAM.
 *
 * @param startblk EEPROM block to start the circular buffer.
 * @param lenblks Length of circular buffer in EEPROM blocks.
 */
int demi_init(const int startblk, const int lenblks)
{
  int lendemis;
  _startblk = startblk;
  _endblk = startblk+lenblks-1;

  _cursorblk = startblk;
  _nextblk = _cursorblk + 1;

  // Calculate the number of demis.
  lendemis = lenblks*DEMIS_PER_BLK;
  _enddemi =  lendemis - 1;
  _cursordemi = 0;

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
 * @param offset Demi index to overwrite, relative to _cursordemi. Must be 0, 1 or 2.
 * @param demidata Pointer to an 8 byte array of new demi data.
 */
int demi_write(int offsetdemis, char * demidata)
{
  int offsetbytes;

  // If _cursordemi is odd, then offsetdemis is at 1.
  // If _cursordemi is even, then offsetdemis is at 0.
  if (_cursordemi)
  {
    // ODD. offsetdemis range is 1,2,3
    offsetdemis += 1;
  }

  // Convert offset from the block start in demis to offset in bytes.
  offsetbytes = offsetdemis * BYTES_PER_DEMI;

  // Copy demi to the buffer
  return eep_cp(&offsetbytes, demidata, BYTES_PER_DEMI);
}

// Move _cursordemi forward by 1.
DemiState_t demi_movecursor(void)
{
    DemiState_t demistate = ds_consecutive;

  // Increment _cursordemi
  if (_cursordemi == _enddemi)
  {
    _cursordemi = 0;
    demistate = ds_newloop; // new loop started
  }
  else
  {
    _cursordemi = _cursordemi + 1;
  }

  _cursorblk = DEMI_TO_BLK(_cursordemi);
  if (_cursorblk == _endblk)
  {
    _nextblk = _startblk;
    demistate = ds_looparound;
  }
  else
  {
    _nextblk = _cursorblk + 1;
  }

  return demistate;
}

void demi_readcursor(void)
{

}

int demi_getendmarkerpos(void)
{
    // When cursordemi is ODD, the end marker byte is 8 bytes further back.
    return (_nextblk - _startblk)*DEMIS_PER_BLK*BYTES_PER_DEMI + ENDMARKER_OFFSET_IN_ENDSTOP_1 + (_cursordemi & 0x01)*BYTES_PER_DEMI;
}