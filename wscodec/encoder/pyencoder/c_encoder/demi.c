#include "eep.h"
#include "demi.h"
#include "defs.h"

#define DEMI_TO_BLK(demi)   (_startblk + (demi >> 1))       /*!< Maps a demi to its EEPROM block. */
#define IS_ODD(x)           ((x & 0x01) > 0)                /*!< Returns 1 if x is ODD and 0 if x is EVEN. */


static int _endblk = 0;     /*!< Last EEPROM block in the circular buffer. */
static int _startblk = 0;   /*!< First EEPROM block in the circular buffer. */
static int _cursorblk;      /*!< Cursor in terms of 16-byte EEPROM blocks. Must be >= #_startblk and <= #_endblk. */
static int _nextblk;        /*!< Index of the next EEPROM block after the cursor block. The buffer is circular, so it can be < #_cursorblk. */

static int _enddemi = 0;    /*!< Largest possible value of _cursordemi. Always an odd integer. */
static int _cursordemi = 0; /*!< Cursor in terms of 8-byte demis. Must be >= 0 and <= #_enddemi. */

/*!
 * @brief Copy 4 demis from EEPROM into RAM.
 *
 * This is 2 demis from #_cursorblk and 2 demis from the block after it #_nextblk.
 * If #_cursorblk is at the end of the buffer, then #_nextblk will be at the start. This
 * makes the buffer circular.
 *
 */
static void demi_read4(void)
{
  // Read 2 demis from EEPROM block _cursorblk into RAM buffer location 0.
  eep_read(_cursorblk, 0);
  // Read 2 demis from EEPROM block _nextblk into RAM buffer location 1.
  eep_read(_nextblk, 1);
}

/*!
 * @brief Right shift the RAM buffer by 2 demis and append 2 demis read from the #_nextblk.
 *
 * First: RAM buffer is right shifted by one block, overwriting the previous cursor block with the new cursor block.
 * Second: New contents of #_nextblk are copied out of EEPROM into the vacant RAM buffer block.
 *
 * The right shift saves a slow and unnecessary read of #_cursorblk from EEPROM.
 */
static void demi_shift2read2(void)
{
  // Shift RAM buffer right by 2 demis by copying location 1 into location 0.
  eep_swap(1, 0);
  // Read 2 demis from EEPROM block _nextblk into RAM buffer location 1.
  eep_read(_nextblk, 1);
}

/*!
 * @brief Copy 4 demis from RAM to EEPROM.
 *
 */
void demi_commit4(void)
{
  // Write 2 demis from RAM buffer location 0 to _cursorblk.
  eep_write(_cursorblk, 0);
  // Write 2 demis from RAM buffer location 1 to _nextblk.
  eep_write(_nextblk, 1);
  eep_waitwritedone();
}

/*!
 * @brief Write the last 2 demis from RAM to the EEPROM.
 *
 * Some functions only need to modify the last 2 demis so this saves time and energy over writing 4.
 *
 */
void demi_commit2(void)
{
  // Write 2 demis from RAM buffer location 1 into _nextblk.
  eep_write(_nextblk, 1);
  eep_waitwritedone();
}

/*!
 * @brief Initialise the EEPROM circular buffer.
 *
 * Reads the first 4 demis in RAM.
 *
 * @param startblk EEPROM block to start the circular buffer.
 * @param lenblks Length of circular buffer in EEPROM blocks.
 */
void demi_init(const int startblk, const int lenblks)
{
  int lendemis;

  _startblk = startblk;
  _endblk = startblk+lenblks-1;

  _cursorblk = startblk;
  _nextblk = _cursorblk + 1;

  // Calculate the number of demis.
  lendemis = lenblks * DEMIS_PER_BLK;
  _enddemi =  lendemis - 1;

  _cursordemi = 0;
}

/*!
 * @brief Overwrite one demi in the RAM buffer.
 *
 * The function to modify the RAM buffer eep_cp() requires a byte index relative to #_cursorblk.
 *
 * - When #_cursordemi is EVEN, nothing is needs to be done because it lies on a block boundary.
 * - When #_cursordemi is ODD then it is offset from the block boundary by one demi. Therefore one is added to offsetdemis.
 *
 * @param offset Demi index to overwrite, relative to _cursordemi. Must be 0, 1 or 2.
 * @param demidata Pointer to an 8 byte array of new demi data.
 */
int demi_write(int offsetdemis, char * demidata)
{
  int offsetbytes;

  if (IS_ODD(_cursordemi))
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

/*!
 * @brief Update RAM buffer to contain the 4 demis after _cursordemi.
 *
 * This function must be called each time the cursor position is changed.
 *
 * When #_cursordemi is 0 it is assumed that the RAM buffer is empty, so all 4 demis are read.
 * When #_cursordemi is not 0, it is assumed that the RAM buffer has been populated before. It is also assumed that
 * #_cursordemi has only moved once since the previous time this function was called. Therefore it is not necessary to read
 * 4 more demis out of the EEPROM.  
 */
void demi_readcursor(void)
{
  // Determine if a read is needed.
  if (_cursordemi == 0)
  {
    demi_read4();
  }
  else if (!IS_ODD(_cursordemi))
  {
    demi_shift2read2();
  }
}


int demi_getendmarkerpos(void)
{
    // When cursordemi is ODD, the end marker byte is 8 bytes further back.
    return (_nextblk - _startblk)*DEMIS_PER_BLK*BYTES_PER_DEMI + ENDMARKER_OFFSET_IN_ENDSTOP_1 + IS_ODD(_cursordemi)*BYTES_PER_DEMI;
}
