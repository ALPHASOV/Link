
/****************************************************************************
// 文件名      GPT.c
//----------------------------------------------------------------------------
// 处理器:	Infineon XC2267M-104F80
//
// 编译器:	Keil 2.1
//
//
// 描述:	定时器(GPT)、中断初始化、中断服务程序.
****************************************************************************/

#include "GPT.h"

/****************************************************************************
// 过程:	void GPT_vInit(void) 
//
//----------------------------------------------------------------------------
// 描述:	初始化.
//		包括:定时器(GPT)、中断初始化
//----------------------------------------------------------------------------
// 返回值:	无.
//
//----------------------------------------------------------------------------
// 参数:	无.
//
****************************************************************************/

void GPT_vInit(void)
{
  ///  -----------------------------------------------------------------------
  ///  Configuration of Timer Block Prescaler 1:
  ///  -----------------------------------------------------------------------
  GPT12E_KSCCFG  =  0x0003;      // Module Enable

  _nop_();  // one cycle delay 

  _nop_();  // one cycle delay 

  ///  -----------------------------------------------------------------------
  ///  Configuration of the GPT Core Timer 3:
  ///  -----------------------------------------------------------------------
  ///  - timer 3 works in timer mode
  ///  - external up/down control is disabled
  ///  - prescaler factor is 8
  ///  - up/down control bit is reset
  ///  - alternate output function T3OUT (P7.0) is disabled
  ///  - timer 3 output toggle latch (T3OTL) is set to 0

  GPT12E_T3CON   =  0x0000;      // load timer 3 control register
  GPT12E_T3      =  0xFC18;      // load timer 3 register

  ///  -----------------------------------------------------------------------
  ///  Configuration of the used GPT Interrupts:
  ///  -----------------------------------------------------------------------
  ///  timer 3 service request node configuration:
  ///  - timer 3 interrupt priority level (ILVL) = 15
  ///  - timer 3 interrupt group level (GLVL) = 0
  ///  - timer 3 group priority extension (GPX) = 0

  GPT12E_T3IC    =  0x007C;     

  ///  Use PEC channel 4 for GPT T3 INT:
  ///  - normal interrupt
  ///  - pointers are not modified
  ///  - transfer a word
  ///  - service End of PEC interrrupt by a EOP interrupt node is disabled
  ///  - channel link mode is disabled

  PECC4          =  0x0000;      // load PECC4 control register


  GPT12E_T3CON_T3R  =  1;        // set timer 3 run bit


} //  End of function vInit


/****************************************************************************
// 过程:	void GPT_viTmr3(void) 
//
//----------------------------------------------------------------------------
// 描述:	定时器3中断服务程序.每100us中断1次
//----------------------------------------------------------------------------
// 返回值:	无.
//
//----------------------------------------------------------------------------
// 参数:	无.
//
****************************************************************************/

void GPT_viTmr3(void) interrupt T3INT
{
  // USER CODE BEGIN (Tmr3,2)
	GPT12E_T3 = 0xFC18;
	TimeSharing();

} //  End of function GPT_viTmr3

////////////////////////////////////////////////
////*************GPIO CTRL****************//////
///1-预上电-2、2-SW4-4、3-SW5-5、4-SW6-6、5-SW1-0、6-SW2-1、7-SW3-3
////////////////////////////////////////////////
ubyte Gpio_Ctrl(ubyte Gpio_select,ubyte on_off)
{
	ubyte RetCode = 0xAA;
	if(0xAA == on_off)
	{
		switch(Gpio_select)
		{
			case 0x01:
				if(0x00 == Gpio_on_off)
				{
					IO_vSetPin(IO_P1_2);	//预上电上电
					Gpio_on_off = 0x01;
				}
				else
				{
					RetCode = 0x55;
				}
				break;
			case 0x02:
				if(0x01 == Gpio_on_off)
				{
					IO_vSetPin(IO_P1_4);	//SW4上电
					Gpio_on_off |= 0x02;
				}
				else if(0x00 == Gpio_on_off)
				{
					RetCode = 0x66;
				}
				else
				{
					RetCode = 0x55;
				}
				break;
			case 0x03:
				if((0x03 == Gpio_on_off) || (0x0B == Gpio_on_off))
				{
					IO_vSetPin(IO_P1_5);	//SW5上电
					Gpio_on_off |= 0x04;
				}
				else if(Gpio_on_off < 0x03)
				{
					RetCode = 0x66;
				}
				else
				{
					RetCode = 0x55;
				}
				break;
			case 0x04:
				if((0x03 == Gpio_on_off) || (0x07 == Gpio_on_off))
				{
					IO_vSetPin(IO_P1_6);	//SW6上电
					Gpio_on_off |= 0x08;
				}
				else if(Gpio_on_off < 0x03)
				{
					RetCode = 0x66;
				}
				else
				{
					RetCode = 0x55;
				}
				break;
			case 0x05:
				if((0x0F == (Gpio_on_off & 0x0F)) && (0x00 == (Gpio_on_off & 0x10)))
				{
					IO_vSetPin(IO_P1_0);	//SW1上电
					Gpio_on_off |= 0x10;
				}
				else if(Gpio_on_off < 0x0F)
				{
					RetCode = 0x66;
				}
				else
				{
					RetCode = 0x55;
				}
				break;
			case 0x06:
				if((0x0F == (Gpio_on_off & 0x0F)) && (0x00 == (Gpio_on_off & 0x20)))
				{
					IO_vSetPin(IO_P1_1);	//SW2上电
					Gpio_on_off |= 0x20;
				}
				else if(Gpio_on_off < 0x0F)
				{
					RetCode = 0x66;
				}
				else
				{
					RetCode = 0x55;
				}
				break;
			case 0x07:
				if((0x0F == (Gpio_on_off & 0x0F)) && (0x00 == (Gpio_on_off & 0x40)))
				{
					IO_vSetPin(IO_P1_3);	//SW3上电
					Gpio_on_off |= 0x40;
				}
				else if(Gpio_on_off < 0x0F)
				{
					RetCode = 0x66;
				}
				else
				{
					RetCode = 0x55;
				}
				break;
			default:
				RetCode = 0x77;
				break;
		}
	}
	else if(0x55 == on_off)
	{
		switch(Gpio_select)
		{
			case 0x01:
				if(0x01 == Gpio_on_off)
				{
					IO_vResetPin(IO_P1_2);		//预上电断电
					Gpio_on_off = 0x00;
				}
				else if(Gpio_on_off > 1)
				{
					RetCode = 0x66;
				}
				else
				{
					RetCode = 0x55;
				}
				break;
			case 0x02:
				if(0x03 == Gpio_on_off)
				{
					IO_vResetPin(IO_P1_4);		//SW4断电
					Gpio_on_off = 0x01;
				}
				else if(Gpio_on_off > 3)
				{
					RetCode = 0x66;
				}
				else
				{
					RetCode = 0x55;
				}
				break;
			case 0x03:
				if((0x04 == (Gpio_on_off & 0x04)) && (Gpio_on_off < 0x10))
				{
					IO_vResetPin(IO_P1_5);		//SW5断电
					Gpio_on_off &= 0x0B;
				}
				else if(Gpio_on_off > 0x10)
				{
					RetCode = 0x66;
				}
				else
				{
					RetCode = 0x55;
				}
				break;
			case 0x04:
				if((0x08 == (Gpio_on_off & 0x08)) && (Gpio_on_off < 0x10))
				{
					IO_vResetPin(IO_P1_6);		//SW6断电
					Gpio_on_off &= 0x07;
				}
				else if(Gpio_on_off > 0x10)
				{
					RetCode = 0x66;
				}
				else
				{
					RetCode = 0x55;
				}
				break;
			case 0x05:
				if(0x10 == (Gpio_on_off & 0x10))
				{
					IO_vResetPin(IO_P1_0);		//SW1断电
					Gpio_on_off &= 0x6F;
				}
				else
				{
					RetCode = 0x55;
				}
				break;
			case 0x06:
				if(0x20 == (Gpio_on_off & 0x20))
				{
					IO_vResetPin(IO_P1_1);		//SW2断电
					Gpio_on_off &= 0x5F;
				}
				else
				{
					RetCode = 0x55;
				}
				break;
			case 0x07:
				if(0x40 == (Gpio_on_off & 0x40))
				{
					IO_vResetPin(IO_P1_3);		//SW3断电
					Gpio_on_off &= 0x3F;
				}
				else
				{
					RetCode = 0x55;
				}
				break;
			case 0xFF:
				if(!Gpio_on_off)
				{
					IO_vResetPin(IO_P1_0);
					IO_vResetPin(IO_P1_1);
					IO_vResetPin(IO_P1_3);
					IO_vResetPin(IO_P1_5);
					IO_vResetPin(IO_P1_6);
					IO_vResetPin(IO_P1_4);
					IO_vResetPin(IO_P1_2);
					Gpio_on_off = 0;
				}
				else
				{
					RetCode = 0x55;
				}
				break;
			default:
				RetCode = 0x77;
				break;
		}
	}
	else
	{
		RetCode = 0xFF;
	}
	return(RetCode);
}

