
/* Fallback definitions for environments without the standard headers. */
#if defined(__has_include)
#  if __has_include(<stdint.h>)
#    include <stdint.h>
#  else
typedef unsigned char uint8_t;
typedef unsigned short uint16_t;
typedef unsigned int uint32_t;
#  endif
#  if __has_include(<stddef.h>)
#    include <stddef.h>
#  else
typedef unsigned long long size_t;
#  endif
#  if __has_include(<stdbool.h>)
#    include <stdbool.h>
#  else
typedef int bool;
#    define true 1
#    define false 0
#  endif
#else
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#endif

/* --------------------------------------------------------------
 *  MMIO base and register offsets (must match the top‑module)
 * -------------------------------------------------------------- */
#define MAC_BASE        0x80000000U
#define MAC_A_REG       ((volatile uint32_t *)(MAC_BASE + 0x00))
#define MAC_B_REG       ((volatile uint32_t *)(MAC_BASE + 0x04))
#define MAC_C_REG       ((volatile uint32_t *)(MAC_BASE + 0x08))
#define MAC_START_REG   ((volatile uint32_t *)(MAC_BASE + 0x0C))
#define MAC_STATUS_REG  ((volatile uint32_t *)(MAC_BASE + 0x14))

/* --------------------------------------------------------------
 *  Helper macros – write an 8‑bit/16-bit value to the 32‑bit MMIO register
 * -------------------------------------------------------------- */
#define WRITE_MAC_REG(reg, val)    (*(reg) = ((val) & 0xFFU))
#define WRITE_MAC_REG_16(reg, val) (*(reg) = ((val) & 0xFFFFU))

/* --------------------------------------------------------------
 *  Compute one FC layer.
 *
 *  Parameters
 *      weights   – pointer to the weight vector (uint8_t[])
 *      activations – pointer to the activation vector (uint8_t[])
 *      n        – number of multiply‑accumulate operations (size of vectors)
 *      result   – pointer where the 16‑bit accumulated result will be stored
 *
 *  Returns 0 on success, non‑zero on error (e.g., MAC fault).
 * -------------------------------------------------------------- */
int fc_layer_compute(const uint8_t *weights,
                     const uint8_t *activations,
                     size_t n,
                     uint16_t *result)
{
    uint16_t acc = 0;                     // 16‑bit accumulator (C term)
    bool     fault = false;

    for (size_t i = 0; i < n; ++i) {
        /* ------------------------------------------------------
         *  1) Load the next weight and activation from memory.
         * ------------------------------------------------------ */
        uint8_t w = weights[i];
        uint8_t a = activations[i];

        /* ------------------------------------------------------
         *  2) Program the MAC for this MAC operation:
         *        A = weight   (8‑bit)
         *        B = activation (8‑bit)
         *        C = current accumulator (16‑bit)
         * ------------------------------------------------------ */
        WRITE_MAC_REG(MAC_A_REG,  w);
        WRITE_MAC_REG(MAC_B_REG,  a);
        WRITE_MAC_REG_16(MAC_C_REG, acc);   // Pass full 16-bit accumulator
        
        /* ------------------------------------------------------
         *  3) Fire the MAC (one‑cycle start pulse)
         * ------------------------------------------------------ */
        WRITE_MAC_REG(MAC_START_REG, 0x01U);   // set bit0 → start pulse

        /* ------------------------------------------------------
         *  4) Wait for the MAC to finish.
         *    The status register bit‑1 (valid) becomes 1 when the
         *    computation is done.  We also watch bit‑0 (fault).
         * ------------------------------------------------------ */
        while (1) {
            uint32_t status = *MAC_STATUS_REG;
            if (status & 0x02)          // valid bit set → result ready
                break;
            if (status & 0x01) {        // fault bit set → hardware error
                fault = true;
                break;
            }
        }

        if (fault) {
            /* --------------------------------------------------
             *  The MAC reported a fault – abort the layer.
             * -------------------------------------------------- */
            return -1;
        }

        /* ------------------------------------------------------
         *  5) Read the 16‑bit result (bits 15:0 of the MAC output
         *     register).  The MAC result register is 16‑bit wide,
         *     bits 15:0 hold the sum.
         * ------------------------------------------------------ */
        acc = (uint16_t)(*MAC_C_REG & 0xFFFFU);       // Update accumulator for the next loop iteration
        *result = acc;                                // Store the current accumulated result
    }

    return 0;   // success
}