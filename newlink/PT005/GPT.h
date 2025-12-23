//****************************************************************************
// @Module        General Purpose Timer Unit (GPT)
// @Filename      GPT.h
// @Project       PCM_OLED.dav
//----------------------------------------------------------------------------
// @Controller    Infineon XC2267M-104F80
//
// @Compiler      Keil
//
// @Codegenerator 2.1
//
// @Description   This file contains all function prototypes and macros for 
//                the GPT module.
//
//****************************************************************************


#ifndef _GPT_H_
#define _GPT_H_

#include "XC22xxMREGS.H"

//****************************************************************************
// @Prototypes Of Global Functions
//****************************************************************************

void GPT_vInit(void);
ubyte Gpio_Ctrl(ubyte Gpio_select,ubyte on_off);

//****************************************************************************
// Interrupt Vectors
//****************************************************************************

#define T3INT 0x21

ubyte Gpio_on_off = 0;
extern void TimeSharing(void);

#endif  // ifndef _GPT_H_
