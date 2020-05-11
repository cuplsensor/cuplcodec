#ifndef _DEMI_H_
#define _DEMI_H_

typedef enum OctState {
  firstloop,
  loopingaround,
  overwriting
} OctState_t;

/* Demi stores information on which demi indices are loaded into memory. */
int demi_init(const int startblk, const int lenblks); // Initialise demi index to 0.
int demi_commit4(void); // Commit 4 demis from buffer to the NTAG.
int demi_commit2(void);
int demi_write(int offset, char * demidata); // Offset must be 0, 1 or 2.
int demi_movecursor(void);
void demi_restore(void);
OctState_t demi_getstate(void);
int demi_getendmarkerpos(void);


#endif
