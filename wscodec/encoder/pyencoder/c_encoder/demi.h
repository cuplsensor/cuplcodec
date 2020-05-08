#ifndef _DEMI_H_
#define _DEMI_H_

typedef enum OctInd {
  Demi0 = 0,
  Demi1 = 1,
  Demi2 = 2
} OctInd_t;

typedef enum OctState {
  firstloop,
  loopingaround,
  overwriting
} OctState_t;

/* Demi stores information on which demi indices are loaded into memory. */
int demi_init(const int startblk, const int lenblks); // Initialise demi index to 0.
int demi_commit4(void); // Commit 4 demis from buffer to the NTAG.
// Writes an demi into the buffer. Fails if demiindex is not present in memory.
// static demi_isinbuffer(const int demiindex)
int demi_commit2(void);
int demi_write(OctInd_t demiindex, char * demidata); // Demi pos is 0, 1, 2, 3.
// Returns 1 if looping around. Make this one static.
// Gets the next demi index. Calls read4 if the next demi is not in the first
// 2 buffer entries.
int demi_movecursor(void);
void demi_restore(void);
OctState_t demi_getstate(void);
int demi_getendmarkerpos(void);

// write, write, write, commit4, getnext
// read4, write, write, write, commit4, write, write, write, commit4,

#endif
