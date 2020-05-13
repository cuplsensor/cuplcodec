#ifndef _DEMI_H_
#define _DEMI_H_

#define DEMI0 0
#define DEMI1 1
#define DEMI2 2

typedef enum OctState {
  firstloop,
  loopingaround,
  overwriting
} OctState_t;

typedef enum {
  ds_consecutive,
  ds_looparound,
  ds_newloop
} DemiState_t;

/* Demi stores information on which demi indices are loaded into memory. */
int demi_init(const int startblk, const int lenblks); // Initialise demi index to 0.
int demi_commit4(void); // Commit 4 demis from buffer to the NTAG.
int demi_commit2(void);
int demi_write(int offsetdemis, char * demidata); // offsetdemis must be 0, 1 or 2.
DemiState_t demi_movecursor(void);
int demi_getendmarkerpos(void);


#endif
