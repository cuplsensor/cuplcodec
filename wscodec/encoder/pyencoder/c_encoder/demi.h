/*!
 * @file demi.h
 * @brief Writes to a circular buffer of 8-byte demis. This is stored in an NFC readable EEPROM e.g. the
 * <a href="https://www.nxp.com/docs/en/data-sheet/NT3H2111_2211.pdf">NXP NT3H2111</a>.
 *
 * An EEPROM block is 16 bytes long. Demi is short for demi-block; it is 8 bytes long.
 * A majority of transactions write 3 demis:
 * - Demi0: Two base64 encoded pairs (::pair_t) comprised of 4x sensor readings.
 * - Demis1 and 2: Circular buffer endstop (::endstop_t).
 *
 * Demis are written to an EEPROM location given by #_cursordemi:
 * - Even values of #_cursordemi start at byte 0 of an EEPROM block.
 * - Odd values of #_cursordemi start at byte 8 of an EEPROM block.
 * A demi always fits completely into one EEPROM block, it never stradles two.
 *
 * The function demi_movecursor() adds 1 to #_cursordemi or resets it to 0 if the end of the circular buffer #_enddemi has been reached.
 *
 * There is no need to move the cursor after every write; the same 3 demis can be overwritten.
 * If only one of the two available pairs in Demi0 changes at a time, the cursor is only moved after both have
 * been produced. This applies if the format specifies OnePairPerSample (see CODEC_FEAT_42).
 *
 * Sometimes only one demi needs to be overwritten: Demi2 contains minutes elapsed since the previous sample (::markerb64).
 * This is overwritten every minute between samples. For this only one EEPROM block needs to be modified with demi_commit2(). This saves power,
 * because writing to an I2C EEPROM is slow.
 *
 * When all 3 demis are modified, 4 demis (two EEPROM blocks) must be written with demi_commit4().
 *
 * Whilst the code allows for 1,2 or 3 demis to be edited locally, the EEPROM must be read and written in multiples of 2 demis i.e.
 * one block at a time. Two blocks of EEPROM are buffered at all times. This buffer must be updated:
 * - After the cursor is moved to a new location with demi_movecursor() or demi_init().
 * - Before any write operations with demi_write()
 *
 * This preserves data in the extra demi, which will either be after demi2 or before demi0.
 * The buffer update is done with demi_readcursor(). It deduces which EEPROM blocks to copy into the local buffer based on #_cursordemi.
 */

#ifndef _DEMI_H_
#define _DEMI_H_

#define DEMI0 0             /*!< Write first demi after the cursor. */
#define DEMI1 1             /*!< Write second demi after cursor. */
#define DEMI2 2             /*!< Write third demi after the cursor. */

/**
 *  Structure to describe the state of the EEPROM circular buffer.
 */
typedef enum DemiState {
  ds_consecutive,           /*!< #_cursorblk is not 0 and #_nextblk is located at the next EEPROM block. */
  ds_looparound,            /*!< #_cursorblk is at the end of the circular buffer and #_nextblk is at the beginning. Data are overwritten from the first time this occurs. */
  ds_newloop                /*!< #_cursorblk is 0 and #_nextblk is 1. A new loop of the circular buffer has started. */
} DemiState_t;

/// Have doxygen ignore this
/// @cond
void demi_init(const int startblk, const int lenblks);
void demi_commit4(void);
void demi_commit2(void);
int demi_write(int offsetdemis, char * demidata);
DemiState_t demi_movecursor(void);
void demi_readcursor(void);
int demi_getendmarkerpos(void);
/// @endcond

#endif
