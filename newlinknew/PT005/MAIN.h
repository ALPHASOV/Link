/****************************************************************************
// 文件名      Main.h
//----------------------------------------------------------------------------
// 处理器:	Infineon XC2267M-104F80
//
// 编译器:	Keil 2.1
//
//
// 描述:	包含所有函数原型及 Main.c 用到的宏定义.
****************************************************************************/


#ifndef _MAIN_H_
#define _MAIN_H_
//****************************************************************************
// 定义
//****************************************************************************
#define KEIL
#include "Type.h"
#define MAX_READ_CNT 10		//每周期每通道AD转换次数


void vInit(void);
void vUnlockProtecReg(void);
void vLockProtecReg(void);
void vChangeFreq(void);
void WDT_vInit(void);



extern void IO_vInit(void);
extern void GPT_vInit(void);
extern void ADC_vInit(void);
extern void CAN_vInit(void);
extern void ReStore_Para_Init(void);
extern void delay_us(uword t);
extern void delay_ms(uword t);

extern ubyte CAN_AB_Cmd(void);
extern ubyte CAN_12_AnsCmd(void);
extern ubyte CAN_AB_TM(void);
extern ubyte CAN_12_TM(void);
extern ubyte CAN_12_SelfTest(void);


extern Scs_ErrorType Scs_GoFromBaseModeToNormalMode(void);
extern INLINE void Scs_EnableHighPrecOsc(uword);
extern void Scs_InitTimer(void);



extern ubyte Sync_Start;
extern TaskManage TaskAD;
extern void Adc_Read(uword cnt);
extern void ADC_Filter(void);

extern void Get_AD_Value(ubyte No);

ulong CAN_NSCR[4] = {0x200200,0x200300,0x200400,0x200500};	//定义{CAN_NCR0,CAN_NCR1,CAN_NCR2,CAN_NCR3},{CAN_NSR0,CAN_NSR1,CAN_NSR2,CAN_NSR3} = {CAN_NCR0+4,CAN_NCR1+4,CAN_NCR2+4,CAN_NCSR3+4};
#endif  // ifndef _MAIN_H_
