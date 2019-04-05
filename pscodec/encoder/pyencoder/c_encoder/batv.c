/*
 * batv.c
 *
 *  Created on: 6 Jan 2018
 *      Author: malcolm
 */

#include "driverlib.h"
#include "batv.h"

volatile int adcvoltage = 0;

static void adc_enable()
{
    //Initialize the ADC Module
    /*
     * Base Address for the ADC Module
     * Use internal ADC bit as sample/hold signal to start conversion
     * USE MODOSC 5MHZ Digital Oscillator as clock source
     * Use default clock divider of 1
     */
    ADC_init(ADC_BASE,
             ADC_SAMPLEHOLDSOURCE_SC,
             ADC_CLOCKSOURCE_ADCOSC,
             ADC_CLOCKDIVIDER_1);

    ADC_enable(ADC_BASE);

    /*
     * Base Address for the ADC Module
     * Sample/hold for 16 clock cycles
     * Do not enable Multiple Sampling
     */
    ADC_setupSamplingTimer(ADC_BASE,
                           ADC_CYCLEHOLD_16_CYCLES,
                           ADC_MULTIPLESAMPLESDISABLE);

    //Configure Memory Buffer
    /*
     * Base Address for the ADC Module
     * Use input A7
     * Use positive reference of Internally generated Vref
     * Use negative reference of AVss
     */
    ADC_configureMemory(ADC_BASE,
                        ADC_INPUT_REFVOLTAGE,
                        ADC_VREFPOS_AVCC,
                        ADC_VREFNEG_AVSS);

    ADC_clearInterrupt(ADC_BASE,
                       ADC_COMPLETED_INTERRUPT);

    //Enable Memory Buffer interrupt
    ADC_enableInterrupt(ADC_BASE,
                        ADC_COMPLETED_INTERRUPT);

    //Configure internal reference
    //If ref voltage no ready, WAIT
    while (PMM_REFGEN_NOTREADY ==
            PMM_getVariableReferenceVoltageStatus()) ;

    //Internal Reference ON
    PMM_enableInternalReference();
}

static void adc_disable()
{
    ADC_disable(ADC_BASE);

    //Disable Memory Buffer interrupt
    ADC_disableInterrupt(ADC_BASE,
                        ADC_COMPLETED_INTERRUPT);

    //Internal Reference OFF
    PMM_disableInternalReference();
}


int batv_measure()
{
    adc_enable();

    //Enable and Start the conversion
    //in Single-Channel, Single Conversion Mode
    ADC_startConversion(ADC_BASE, ADC_SINGLECHANNEL);

    //LPM0, ADC_ISR will force exit
    __bis_SR_register(CPUOFF + GIE);

    adc_disable();

    return adcvoltage;
}

//******************************************************************************
//
//This is the ADC interrupt vector service routine.
//
//******************************************************************************
#if defined(__TI_COMPILER_VERSION__) || defined(__IAR_SYSTEMS_ICC__)
#pragma vector=ADC_VECTOR
__interrupt
#elif defined(__GNUC__)
__attribute__((interrupt(ADC_VECTOR)))
#endif
void ADC_ISR (void)
{
    uint32_t adcresult;
    switch (__even_in_range(ADCIV,12)){
        case  0: break; //No interrupt
        case  2: break; //conversion result overflow
        case  4: break; //conversion time overflow
        case  6: break; //ADCHI
        case  8: break; //ADCLO
        case 10: break; //ADCIN
        case 12:        //ADCIFG0
            //Automatically clears ADCIFG0 by reading memory buffer
            //ADCMEM = A0 > 0.5V?
            adcresult = ADC_getResults(ADC_BASE);
            //adcresult = ((uint32_t)1024 * (uint32_t)1500)/adcresult;
            adcvoltage = (int)adcresult >> 2; // Convert 10 bit value (1024) to 8 bits.

            //Clear CPUOFF bit from 0(SR)
            //Breakpoint here and watch ADC_Result
            __bic_SR_register_on_exit(CPUOFF);
            break;
        default: break;
    }
}
