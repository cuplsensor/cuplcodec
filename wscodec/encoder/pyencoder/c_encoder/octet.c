#include "eep.h"
#include "octet.h"
#include "defs.h"

#define OCTET_TO_BLK(octet) (_startblk + (octet >> 1))
#define MAX_CURSOROCTET  (_lenoctets - 1)


static int _endblk = 0;
static int _startblk = 0;

static int _cursorblk;
static int _nextblk;

static int _lenoctets = 0;
static int _cursoroctet = 0;
static OctState_t _octetstate = firstloop;

/*!
 * @brief Read 4 octets (32 bytes) from EEPROM into RAM starting from the cursor block.
 *
 * This is 2 octets from the cursor block and 2 octets from the block after it (_nextblk).
 * If cursor block is at the end of the buffer, then _nextblk will be at the start. This
 * makes the buffer circular.
 *
 * Static variables :cpp:member:_cursorblk and _nextblk are updated by this function.
 *
 * @param cursorblk EEPROM block number where the cursor is located.
 * @returns looparound 1 if a read has looped around from the end to the beginning of the buffer. 0 otherwise.
 */
static int octet_read4(const int cursorblk)
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

void octet_restore(void)
{
  octet_read4(_cursorblk);
}

/*!
 * @brief Initialise a circular buffer of 8-byte octets.
 *
 * Sets counters to intial values and calls ::octet_read4 to read the first 4
 * octets into RAM.
 *
 * @param startblk EEPROM block to start the circular buffer.
 * @param lenblks Length of circular buffer in EEPROM blocks.
 */
int octet_init(const int startblk, const int lenblks)
{
  _startblk = startblk;
  _endblk = startblk+lenblks-1;

  _cursorblk = startblk;
  _nextblk = _cursorblk + 1;

  // Calculate the number of octets.
  _lenoctets = lenblks*OCTETS_PER_BLK;
  _cursoroctet = 0;
  _octetstate = firstloop;

  octet_read4(startblk);

  return 0;
}

/*!
 * @brief Write 4 octets from RAM to the EEPROM.
 *
 * 2 octets are written from RAM buffer location 0 into the EEPROM block ::_cursorblk.
 * 2 octets are written from RAM buffer location 1 into the EEPROM block ::_nextblk.
 * @returns 0
 */
int octet_commit4(void)
{
  eep_write(_cursorblk, 0);
  eep_write(_nextblk, 1);
  eep_waitwritedone();

  return 0;
}

/*!
 * @brief Write the last 2 octets from RAM to the EEPROM.
 *
 * 2 octets are written from RAM buffer location 1 into the EEPROM block _nextblk.
 * Some functions only need to modify the last 2 octets so this saves time and energy over writing 4.
 * @returns 0
 */
int octet_commit2(void)
{
  eep_write(_nextblk, 1);
  eep_waitwritedone();

  return 0;
}

/*!
 * @brief Overwrite one octet in the RAM buffer.
 *
 * This function takes octetindex as relative to _cursoroctet.
 * The function to modify the RAM buffer ::eep_cp requires an index relative to ::_cursorblk (it has no concept of octets).
 * There are 2 8-byte octets per 16-byte block.
 * If cursoroctet is even, nothing is needs to be done because it lies on a block boundary.
 * If cursoroctet is odd then it is offset from the block boundary by one octet. Therefore one is added to octetindex.
 *
 * @param octetindex Octet index to overwrite, relative to _cursoroctet. Must be 0, 1 or 2.
 * @param octetdata Pointer to an 8 byte array of new octet data.
 */
int octet_write(OctInd_t octetindex, char * octetdata)
{
  int errflag = 1;
  int octetstart;
  int octindex = (int)octetindex;
  // If cursoroctet is odd, then octetstart is at 1.
  // If cursoroctet is even, then octetstart is at 0.
  // Octet index must be 0, 1 or 2.
  if ((_cursoroctet & 0x01) > 0)
  {
    // ODD. octetindex range is 1,2,3
    octindex += 1;
  }

  errflag = 0;
  octetstart = octindex * BYTES_PER_OCTET;
  // Copy data to the buffer
  errflag = eep_cp(&octetstart, octetdata, BYTES_PER_OCTET);

  return errflag;
}

// Move cursor forward by 1. Add overwriting and looping around as parameters.
int octet_movecursor(void)
{
  int cursorblk;
  int looparound = 0;

  // Increment _cursoroctet
  if (_cursoroctet == MAX_CURSOROCTET)
  {
    _cursoroctet = 0;
  }
  else
  {
    _cursoroctet = _cursoroctet + 1;
  }

  // Determine if a read is needed.
  cursorblk = OCTET_TO_BLK(_cursoroctet);
  if (cursorblk != _cursorblk)
  {
    // Perform a read.
    // Only raise the looparound flag once per loop,
    // when the last octet will be written to the first octet of the first block.
    looparound = octet_read4(cursorblk);
  }

  switch(_octetstate)
  {
    case firstloop:
    if (looparound == 1)
    {
      _octetstate = loopingaround;
    }
    break;
    case loopingaround:
    _octetstate = overwriting;
    break;
    case overwriting:
    if (looparound == 1)
    {
      _octetstate = loopingaround;
    }
    break;
  }

  return 0;
}

int octet_getendmarkerpos(void)
{
    // When cursoroctet is ODD, the end marker byte is 8 bytes further back.
    return (_nextblk - _startblk)*OCTETS_PER_BLK*BYTES_PER_OCTET + ENDMARKER_OFFSET_IN_ENDSTOP_1 + (_cursoroctet & 0x01)*BYTES_PER_OCTET;
}

OctState_t octet_getstate(void)
{
  return _octetstate;
}
