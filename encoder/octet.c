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

// Read 4 octets from cursor block.
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

  eep_read(_cursorblk, 0);
  eep_read(_nextblk, 1);

  return looparound;
}

void octet_restore(void)
{
  octet_read4(_cursorblk);
}

// Initialise a circular buffer of octets between startblk and endblk.
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

int octet_commit4(void)
{
  eep_write(_cursorblk, 0);
  eep_write(_nextblk, 1);
  eep_waitwritedone();

  return 0;
}

int octet_commit2(void)
{
  eep_write(_nextblk, 1);
  eep_waitwritedone();

  return 0;
}

// Octet index is relative to cursoroctet.
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

OctState_t octet_getstate(void)
{
  return _octetstate;
}
