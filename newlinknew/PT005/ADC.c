/****************************************************************************
// 文件名      ADC.c
//----------------------------------------------------------------------------
// 处理器:	Infineon XC2267M-104F80
//
// 编译器:	Keil 2.1
//
//
// 描述:	包含ADC1初始化功能.
****************************************************************************/

#include "ADC.h"

/****************************************************************************
// 过程:	void ADC_vInit(void) 
//
//----------------------------------------------------------------------------
// 描述:		  This is the initialization function of the ADC function 
//                library. It is assumed that the SFRs used by this library 
//                are in reset state. 
//                
//                Following SFR fields will be initialized:
//                GLOBCTR  - Global Control
//                RSPR0    - Priority and Arbitration Register
//                ASENR    - Arbitration slot enable register
//                CHCTRx   - Channel Control Register x
//                RCRx     - Result Control Register x
//                KSCFG    - Module configuration Register
//                INPCR    - Input class Registers
//                CHINPRx  - Channel Interrupt register
//                EVINPRx  - Event Interrupt register
//                SYNCTR   - Synchronisation control register
//                LCBRx    - Limit check boundary register
//                PISEL    - Port input selection
//                QMR0     - Sequential 0 mode register
//                CRMR1    - Parallel mode register
//                QMR2     - Sequential 2 mode register
//----------------------------------------------------------------------------
// 返回值:	无.
//
//----------------------------------------------------------------------------
// 参数:	无.
//
****************************************************************************/


void ADC_vInit(void)
{

  ///  -----------------------------------------------------------------------
  ///  初始化ADC0:
  ///  -----------------------------------------------------------------------
  ADC0_KSCFG     =  0x0003;      // load ADC0 kernel configuration register

  ///  - the ADC module clock is enabled
  ///  - the ADC module clock = 80.00 MHz

  _nop_();  // one cycle delay 

  _nop_();  // one cycle delay 

  
  ///  -----------------------------------------------------------------------
  ///  Configure global control register:
  ///  -----------------------------------------------------------------------
  ///  --- Conversion Timing -----------------
  ///  - conversion time (CTC)    = 00.85 us

  ///  _Analog clock is 1/4th of module clock and digital clock is 1/1 times 
  ///  of module clock

  ///  - the permanent arbitration mode is selected
  ADC1_GLOBCTR   =  0x0003;      // load global control register

  ///  -----------------------------------------------------------------------
  ///  Configuration of Arbitration Slot enable register and also the Source 
  ///  Priority register:
  ///  -----------------------------------------------------------------------
  ///  - Arbitration Slot 0 is enabled

  ///  - Arbitration Slot 1 is enabled

  ///  - Arbitration Slot 2 is enabled

  ///  - the priority of request source 0 is low
  ///  - the wait-for-start mode is selected for source 0
  ///  - the priority of request source 1 is low
  ///  - the wait-for-start mode is selected for source 1
  ///  - the priority of request source 2 is low
  ///  - the wait-for-start mode is selected for source 2
  ADC1_ASENR     =  0x0007;      // load Arbitration Slot enable register

  ADC1_RSPR0     =  0x0000;      // load Priority and Arbitration register

  ///  -----------------------------------------------------------------------
  ///  Configuration of Channel Control Registers:
  ///  -----------------------------------------------------------------------
  ///  Configuration of Channel 0/2/4/5/6
  ///  - the result register1 is selected
  ///  - the limit check 0 is selected

  ///  - the reference voltage selected is Standard Voltage (Varef)

  ///  - the input class selected is Input Class 0

  ///  - LCBR0 is selected as upper boundary

  ///  - LCBR1 is selected as lower boundary

  ADC1_CHCTR0    =  0x0004;      // load channel control register
  ADC1_CHCTR2    =  0x2004;      // load channel control register
  ADC1_CHCTR4    =  0x4004;      // load channel control register
  ADC1_CHCTR5    =  0x5004;      // load channel control register
  ADC1_CHCTR6    =  0x6004;      // load channel control register

  ///  -----------------------------------------------------------------------
  ///  Configuration of Sample Time and Resolution:
  ///  -----------------------------------------------------------------------

  ///  10 bit resolution selected

  ADC1_INPCR0    =  0x0000;      // load input class0 register

  ///  10 bit resolution selected

  ADC1_INPCR1    =  0x0000;      // load input class1 register

  ///  -----------------------------------------------------------------------
  ///  Configuration of Result Control Registers:
  ///  -----------------------------------------------------------------------
  ///  Configuration of Result Control Register
  ///  - the data reduction filter is disabled
  ///  - the event interrupt is disabled
  ///  - the wait-for-read mode is disabled

  ///  - the FIFO functionality is disabled

  ADC1_RCR0      =  0x0000;      // load result control register 0

  ADC1_RCR1      =  0x0000;      // load result control register 1

  ADC1_RCR2      =  0x0000;      // load result control register 2

  ADC1_RCR3      =  0x0000;      // load result control register 3

  ADC1_RCR4      =  0x0000;      // load result control register 4

  ADC1_RCR5      =  0x0000;      // load result control register 5

  ADC1_RCR6      =  0x0000;      // load result control register 6

  ADC1_RCR7      =  0x0000;      // load result control register 7

  ///  -----------------------------------------------------------------------
  ///  Configuration of Channel Interrupt Node Pointer Register:
  ///  -----------------------------------------------------------------------
  ///  - the SR0 line become activated if channel 0 interrupt is generated

  ///  - the SR0 line become activated if channel 2 interrupt is generated
  ///  - the SR0 line become activated if channel 4 interrupt is generated

  ///  - the SR0 line become activated if channel 5 interrupt is generated

  ///  - the SR0 line become activated if channel 6 interrupt is generated


  ADC1_CHINPR0   =  0x0000;      // load channel interrupt node pointer 
                                 // register

  ADC1_CHINPR4   =  0x0000;      // load channel interrupt node pointer 
                                 // register

  ADC1_CHINPR8   =  0x0000;      // load channel interrupt node pointer 
                                 // register

  ADC1_CHINPR12  =  0x0000;      // load channel interrupt node pointer 
                                 // register
  ///  -----------------------------------------------------------------------
  ///  Configuration of Event Interrupt Node Pointer Register for Source 
  ///  Interrupts:
  ///  -----------------------------------------------------------------------
  ///  - the SR 0 line become activated if the event 0 interrupt is generated
  ///  - the SR 0 line become activated if the event 1 interrupt is generated
  ///  - the SR 0 line become activated if the event 2 interrupt is generated

  ADC1_EVINPR0   =  0x0000;      // load event interrupt set flag register 

  ADC1_EVINPR8   =  0x0000;      // load event interrupt set flag register 

  ADC1_EVINPR12  =  0x0000;      // load event interrupt set flag register 

  ///  -----------------------------------------------------------------------
  ///  Configuration of Service Request Nodes 0 - 3 :
  ///  -----------------------------------------------------------------------

  ///  -----------------------------------------------------------------------
  ///  Configuration of Limit Check Boundary:
  ///  -----------------------------------------------------------------------

  ADC1_LCBR0     =  0x0198;      // load limit check boundary register 0

  ADC1_LCBR1     =  0x0E64;      // load limit check boundary register 1

  ADC1_LCBR2     =  0x0554;      // load limit check boundary register 2

  ADC1_LCBR3     =  0x0AA8;      // load limit check boundary register 3

  ///  -----------------------------------------------------------------------
  ///  Configuration of Gating source and External Trigger Control:
  ///  -----------------------------------------------------------------------
  ///  - No Gating source selected for Arbitration Source


  ADC1_RSIR0     =  0x0000;      // load external trigger control register 
                                 // for Request Source 0
  ADC1_RSIR1     =  0x0000;      // load external trigger control register 
                                 // for Request Source 1
  ADC1_RSIR2     =  0x0000;      // load external trigger control register 
                                 // for Request Source 2

  ///  -----------------------------------------------------------------------
  ///  Configuration of Conversion Queue Mode Register:Sequential Source 0
  ///  -----------------------------------------------------------------------
  ///  - the gating line is permanently Enabled
  ///  - the external trigger is disabled

  ADC1_QMR0      =  0x0001;      // load queue mode register

  ///  -----------------------------------------------------------------------
  ///  Configuration of Conversion Queue Mode Register:Sequential Source 2
  ///  -----------------------------------------------------------------------
  ///  - the gating line is permanently Enabled
  ///  - the external trigger is disabled

  ADC1_QMR2      =  0x0001;      // load queue mode register

  ///  -----------------------------------------------------------------------
  ///  Configuration of Conversion Request Mode Registers:Parallel Source 
  ///  -----------------------------------------------------------------------
  ///  - the gating line is permanently Enabled
  ///  - the external trigger is disabled
  ///  - the source interrupt is disabled
  ///  - the autoscan functionality is disabled

  ADC1_CRMR1     =  0x0001;      // load conversion request mode register 1

  ///  -----------------------------------------------------------------------
  ///  Configuration of Synchronisation Registers:
  ///  -----------------------------------------------------------------------
  ///  - ADC1 is master 
  ADC1_SYNCTR   |=  0x0010;      // Synchronisation register

  P15_DIDIS      =  0x75;      // Port 15 Digital input disable register,enable0/2/4/5/6

  ADC1_GLOBCTR  |=  0x0300;      // turn on Analog part

  ///  -----------------------------------------------------------------------
  ///  Configuration of ADC0 kernel configuration register:
  ///  -----------------------------------------------------------------------
  ADC0_KSCFG     =  0x0003;      // load ADC0 kernel configuration register

  ///  - the ADC module clock is enabled
  ///  - the ADC module clock = 80.00 MHz
  ///   

  _nop_();  // one cycle delay 

  _nop_();  // one cycle delay 

  ///  -----------------------------------------------------------------------
  ///  Configure global control register:
  ///  -----------------------------------------------------------------------
  ///  --- Conversion Timing -----------------
  ///  - conversion time (CTC)    = 00.85 us

  ///  _Analog clock is 1/4th of module clock and digital clock is 1/1 times 
  ///  of module clock

  ///  - the permanent arbitration mode is selected
  ADC0_GLOBCTR   =  0x0003;      // load global control register

  ///  -----------------------------------------------------------------------
  ///  Configuration of Arbitration Slot enable register and also the Source 
  ///  Priority register:
  ///  -----------------------------------------------------------------------
  ///  - Arbitration Slot 0 is enabled

  ///  - Arbitration Slot 1 is enabled

  ///  - Arbitration Slot 2 is enabled

  ///  - the priority of request source 0 is low
  ///  - the wait-for-start mode is selected for source 0
  ///  - the priority of request source 1 is low
  ///  - the wait-for-start mode is selected for source 1
  ///  - the priority of request source 2 is low
  ///  - the wait-for-start mode is selected for source 2
  ADC0_ASENR     =  0x0007;      // load Arbitration Slot enable register

  ADC0_RSPR0     =  0x0000;      // load Priority and Arbitration register

  ///  -----------------------------------------------------------------------
  ///  Configuration of Channel Control Registers:
  ///  -----------------------------------------------------------------------
  ///  Configuration of Channel 8
  ///  - the result register0 is selected
  ///  - the limit check 0 is selected

  ///  - the reference voltage selected is Standard Voltage (Varef)

  ///  - the input class selected is Input Class 0

  ///  - LCBR0 is selected as upper boundary

  ///  - LCBR1 is selected as lower boundary
  ADC0_CHCTR0    =  0x0004;      // load channel control register
  ADC0_CHCTR2    =  0x2004;      // load channel control register
  ADC0_CHCTR3    =  0x3004;      // load channel control register
  ADC0_CHCTR4    =  0x4004;      // load channel control register
  ADC0_CHCTR5    =  0x5004;      // load channel control register
  ///  -----------------------------------------------------------------------
  ///  Configuration of Sample Time and Resolution:
  ///  -----------------------------------------------------------------------

  ///  10 bit resolution selected

  ADC0_INPCR0    =  0x0000;      // load input class0 register


  ADC0_INPCR1    =  0x0000;      // load input class1 register

  ///  -----------------------------------------------------------------------
  ///  Configuration of Result Control Registers:
  ///  -----------------------------------------------------------------------
  ///  Configuration of Result Control Register 0
  ///  - the data reduction filter is disabled
  ///  - the event interrupt is disabled
  ///  - the wait-for-read mode is disabled

  ///  - the FIFO functionality is disabled

  ADC0_RCR0      =  0x0000;      // load result control register 0

  ADC0_RCR1      =  0x0000;      // load result control register 1

  ADC0_RCR2      =  0x0000;      // load result control register 2

  ADC0_RCR3      =  0x0000;      // load result control register 3

  ADC0_RCR4      =  0x0000;      // load result control register 4

  ADC0_RCR5      =  0x0000;      // load result control register 5

  ADC0_RCR6      =  0x0000;      // load result control register 6

  ADC0_RCR7      =  0x0000;      // load result control register 7

  ///  -----------------------------------------------------------------------
  ///  Configuration of Channel Interrupt Node Pointer Register:
  ///  -----------------------------------------------------------------------
  ADC0_CHINPR0   =  0x0000;      // load channel interrupt node pointer 
                                 // register

  ADC0_CHINPR4   =  0x0000;      // load channel interrupt node pointer 
                                 // register

  ///  - the SR0 line become activated if channel 8 interrupt is generated

  ADC0_CHINPR8   =  0x0000;      // load channel interrupt node pointer 
                                 // register

  ADC0_CHINPR12  =  0x0000;      // load channel interrupt node pointer 
                                 // register

  ///  -----------------------------------------------------------------------
  ///  Configuration of Event Interrupt Node Pointer Register for Source 
  ///  Interrupts:
  ///  -----------------------------------------------------------------------
  ///  - the SR 0 line become activated if the event 0 interrupt is generated
  ///  - the SR 0 line become activated if the event 1 interrupt is generated
  ///  - the SR 0 line become activated if the event 2 interrupt is generated

  ADC0_EVINPR0   =  0x0000;      // load event interrupt set flag register 


  ADC0_EVINPR8   =  0x0000;      // load event interrupt set flag register 


  ADC0_EVINPR12  =  0x0000;      // load event interrupt set flag register 

  ///  -----------------------------------------------------------------------
  ///  Configuration of Service Request Nodes 0 - 3 :
  ///  -----------------------------------------------------------------------

  ///  -----------------------------------------------------------------------
  ///  Configuration of Limit Check Boundary:
  ///  -----------------------------------------------------------------------

  ADC0_LCBR0     =  0x0198;      // load limit check boundary register 0

  ADC0_LCBR1     =  0x0E64;      // load limit check boundary register 1

  ADC0_LCBR2     =  0x0554;      // load limit check boundary register 2

  ADC0_LCBR3     =  0x0AA8;      // load limit check boundary register 3

  ///  -----------------------------------------------------------------------
  ///  Configuration of Gating source and External Trigger Control:
  ///  -----------------------------------------------------------------------
  ///  - No Gating source selected for Arbitration Source


  ADC0_RSIR0     =  0x0000;      // load external trigger control register 
                                 // for Request Source 0
  ADC0_RSIR1     =  0x0000;      // load external trigger control register 
                                 // for Request Source 1
  ADC0_RSIR2     =  0x0000;      // load external trigger control register 
                                 // for Request Source 2

  ///  -----------------------------------------------------------------------
  ///  Configuration of Conversion Queue Mode Register:Sequential Source 0
  ///  -----------------------------------------------------------------------
  ///  - the gating line is permanently Enabled
  ///  - the external trigger is disabled

  ADC0_QMR0      =  0x0001;      // load queue mode register

  ///  -----------------------------------------------------------------------
  ///  Configuration of Conversion Queue Mode Register:Sequential Source 2
  ///  -----------------------------------------------------------------------
  ///  - the gating line is permanently Enabled
  ///  - the external trigger is disabled

  ADC0_QMR2      =  0x0001;      // load queue mode register

  ///  -----------------------------------------------------------------------
  ///  Configuration of Conversion Request Mode Registers:Parallel Source 
  ///  -----------------------------------------------------------------------
  ///  - the gating line is permanently Enabled
  ///  - the external trigger is disabled
  ///  - the source interrupt is disabled
  ///  - the autoscan functionality is disabled

  ADC0_CRMR1     =  0x0001;      // load conversion request mode register 1

  ///  -----------------------------------------------------------------------
  ///  Configuration of Synchronisation Registers:
  ///  -----------------------------------------------------------------------
  ///  - ADC0 is master 
  ADC0_SYNCTR   |=  0x0010;      // Synchronisation register

  P5_DIDIS       =   0x3D;      // Port 5 Digital input disable register,0/2/3/4/5 enable

  ADC0_GLOBCTR  |=  0x0300;      // turn on Analog part


} //  End of function ADC_vInit

