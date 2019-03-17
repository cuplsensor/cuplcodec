#ifndef _OCTET_H_
#define _OCTET_H_

typedef enum OctInd {
  Octet0 = 0,
  Octet1 = 1,
  Octet2 = 2
} OctInd_t;

typedef enum OctState {
  firstloop,
  loopingaround,
  overwriting
} OctState_t;

/* Octet stores information on which octet indices are loaded into memory. */
int octet_init(const int startblk, const int lenblks); // Initialise octet index to 0.
int octet_commit4(void); // Commit 4 octets from buffer to the NTAG.
// Writes an octet into the buffer. Fails if octetindex is not present in memory.
// static octet_isinbuffer(const int octetindex)
int octet_commit2(void);
int octet_write(OctInd_t octetindex, char * octetdata); // Octet pos is 0, 1, 2, 3.
// Returns 1 if looping around. Make this one static.
// Gets the next octet index. Calls read4 if the next octet is not in the first
// 2 buffer entries.
int octet_movecursor(void);
void octet_restore(void);
OctState_t octet_getstate(void);
int octet_getcursorpos(void);

// write, write, write, commit4, getnext
// read4, write, write, write, commit4, write, write, write, commit4,

#endif
