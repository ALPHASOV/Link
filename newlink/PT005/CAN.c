//****************************************************************************
// @Module        MultiCAN Module (CAN)
// @Filename      CAN.c
// @Project       PCM_OLED.dav
//----------------------------------------------------------------------------
// @Controller    Infineon XC2267M-104F80
//
// @Compiler      Keil
//
// @Codegenerator 2.1
//
// @Description   This file contains functions that use the CAN module.
//
//----------------------------------------------------------------------------
//
//****************************************************************************





#include "CAN.H"


static ubyte ubFIFOWritePtr[236];
static ubyte ubFIFOReadPtr[236];


void delay_us(uword t)	//约1us
{
	uword i,j;
	for(i = t; i > 0; i--)
	{
									//			MOV     R4,#?t
									//			JMPR    cc_NZ,$END
		for(j = 98; j > 0; j--);	//$i_start:	MOV     R2,#182	
									//$j_start: SUB     R2,#1
									//          JMPR    cc_NZ,$j_start
									//          SUB     R4,#1
									//          JMPR    cc_NZ,$i_start
									//$END:

	}
}
void delay_ms(uword t)	//约1ms
{
	uword i;
	ulong j;
	for(i = t; i > 0; i--)
	{
		for(j = 99995; j > 0; j--);
	}
}

void SetListCommand(uword ValueH, uword ValueL)
{
	CAN_PANCTRH = ValueH; 
	CAN_PANCTRL = ValueL; 
	while(CAN_PANCTRL & CAN_PANCTR_BUSY)
	{
		;
	}
}
/******************************设置接收消息格式**********************************/

void SetMessageArg(void)
{
uword volatile far *CAN_MOCTRnH,*CAN_MOCTRnL;
uword volatile far *CAN_MOARnH,*CAN_MOARnL;
uword volatile far *CAN_MOAMRnH,*CAN_MOAMRnL;
uword volatile far *CAN_MOIPRnH,*CAN_MOIPRnL;
uword volatile far *CAN_MOFGPRnH,*CAN_MOFGPRnL;
uword volatile far *CAN_MOFCRnH,*CAN_MOFCRnL;
ulong MsgNo_Left;
ubyte i;
	for(i = 0; i < 98; i++)
	{
		MsgNo_Left =  ((ulong) CAN_CONF[i].MsgNo << 5);
		CAN_MOCTRnL = (uword volatile far *)(0x20101C + MsgNo_Left);	//CAN_MOCTRnL: from 0x20101C + CAN_CONF[i].MsgNo *0x20
		CAN_MOCTRnH = (uword volatile far *)(0x20101E + MsgNo_Left);	//CAN_MOCTRnH: CAN_MOCTRnL + 2

		CAN_MOARnL = (uword volatile far *)(0x201018 + MsgNo_Left);		//CAN_MOARnL: from 0x201018 + CAN_CONF[i].MsgNo *0x20
		CAN_MOARnH = (uword volatile far *)(0x20101A + MsgNo_Left);		//CAN_MOARnH: CAN_MOARnL + 2

		CAN_MOAMRnL = (uword volatile far *)(0x20100C + MsgNo_Left);	//CAN_MOAMRnL: from 0x20100C + CAN_CONF[i].MsgNo *0x20
		CAN_MOAMRnH = (uword volatile far *)(0x20100E + MsgNo_Left);	//CAN_MOAMRnH: CAN_MOAMRnL + 2

		CAN_MOIPRnL = (uword volatile far *)(0x201008 + MsgNo_Left);	//CAN_MOIPRnL: from 0x201008 + CAN_CONF[i].MsgNo *0x20
		CAN_MOIPRnH = (uword volatile far *)(0x20100A + MsgNo_Left);	//CAN_MOIPRnH: CAN_MOIPRnL + 2

		CAN_MOFGPRnL = (uword volatile far *)(0x201004 + MsgNo_Left);	//CAN_MOFGPRnL: from 0x201004 + CAN_CONF[i].MsgNo *0x20
		CAN_MOFGPRnH = (uword volatile far *)(0x201006 + MsgNo_Left);	//CAN_MOFGPRnH: CAN_MOFGPRnL + 2

		CAN_MOFCRnL = (uword volatile far *)(0x201000 + MsgNo_Left);	//CAN_MOFCRnL: from 0x201000 + CAN_CONF[i].MsgNo *0x20
		CAN_MOFCRnH = (uword volatile far *)(0x201002 + MsgNo_Left);	//CAN_MOFCRnH: CAN_MOFCRnL + 2

		//发送/接收选择
		if(CAN_SEND_Conf == CAN_CONF[i].RS) //SR:CAN_SEND_Conf-send
		{
			*CAN_MOCTRnH = (uword)0x0AA8;        // 0x0AA8:发送;
		}
		else	// RS:CAN_RECEIVE_Conf-Receive
		{
			*CAN_MOCTRnH = (uword)0x00A0;        // 0x00A0:接收;
		}
		*CAN_MOCTRnL = (uword)0x0000;        // load MO1 control register low

		//设置ID:优先级P(bit28~26:0~7)、R(bit25)、DP(bit24)、PF(bit23~16)、接收地址(bit15~8)、发送地址(bit7~0);

		*CAN_MOARnH = 0x6000 + ((uword)CAN_CONF[i].Priority << 8);         // load MO1 arbitration register high
		if(CAN_SEND_Conf == CAN_CONF[i].RS) //SR:CAN_SEND_Conf-Send
		{
			if(CAN_CONF[i].Nod)	//CAN1/2
			{
				*CAN_MOARnL = (((uword)CAN_CONF[i].Nod) << 8) + MyNod_12;         // load MO1 arbitration register low
			}
			else	//CANA/B
			{
				*CAN_MOARnL = (uword)((MainNod_AB << 8) + MyNod_AB);         // load MO1 arbitration register low
			}
		}
		else	// RS:CAN_RECEIVE_Conf-Receive
		{
			if(CAN_CONF[i].Nod)	//CAN1/2
			{
				*CAN_MOARnL = (uword)((MyNod_12 << 8) + CAN_CONF[i].Nod);         // load MO1 arbitration register low
			}
			else
			{
				*CAN_MOARnL = (uword)((MyNod_AB << 8) + MainNod_AB);         // load MO1 arbitration register low
			}
		}


	  ///  设置掩码:0x1FFFFFFF--29位ID中，0--可以与设置不同；1--必须与设置相同

		*CAN_MOAMRnH = (uword)0x2000 + (uword)((CAN_CONF[i].Mask >> 16 ) & 0x1FFF);        // load MO1 acceptance mask register high
		*CAN_MOAMRnL = (uword)(CAN_CONF[i].Mask & 0xFFFF);        // load MO1 acceptance mask register low

	  ///  设置对应消息号:

		*CAN_MOIPRnH = (uword)0x0000;        // load MO1 interrupt pointer register high
		*CAN_MOIPRnL = (uword)CAN_CONF[i].MsgNo << 8;        // load MO1 interrupt pointer register low

	  ///  设置堆栈指针:
	  ///  - current select pointer : (MsgNo * 4) + 0x0D
	  ///  - object select pointer : (MsgNo * 4) + 0x0A
		*CAN_MOFGPRnH = ((uword)((CAN_CONF[i].MsgNo * 4) + 0x0A) << 8) + (uword)CAN_CONF[i].MsgNo * 4 + 0x0D;       // load MO1 FIFO/gateway pointer register high 
	  ///  - bottom pointer : (MsgNo * 4) + 0x0D
	  ///  - top pointer : (MsgNo * 4) + 0x0A
		*CAN_MOFGPRnL = ((uword)((CAN_CONF[i].MsgNo * 4) + 0x0A) << 8) + (uword)CAN_CONF[i].MsgNo * 4 + 0x0D;       // load MO1 FIFO/gateway pointer register low


	  ///  发送/接收设置:
	  ///  - this object is a RECEIVE FIFO BASE OBJECT
	  ///  - 8 valid data bytes

		*CAN_MOFCRnH = (uword)0x0800;        // load MO1 function control register high
		//
		if(CAN_SEND_Conf == CAN_CONF[i].RS) //SR:CAN_SEND_Conf-send
		{
			*CAN_MOFCRnL = (uword)0x0002;        // 0x0002:发送;
		}
		else	// RS:CAN_RECEIVE_Conf-Receive
		{
			*CAN_MOFCRnL = (uword)0x0001;        // 0x0001:接收;
		}
	}
	UergentID = (ulong)Uergent + (MyNod_AB << 8) + MainNod_AB;
	SwitchOnOffID = (ulong)Switch_OnOff + (MyNod_AB << 8) + MainNod_AB;
	ArgSetCheckID = (ulong)Arg_Set_Check + (MyNod_AB << 8) + MainNod_AB;
	ExTransmitID = (ulong)ExTransmit + (MyNod_AB << 8) + MainNod_AB;
}

//****************************************************************************
// @Function      void CAN_vInit(void) 
//
//----------------------------------------------------------------------------
// @Description   This is the initialization function of the CAN function 
//                library. It is assumed that the SFRs used by this library 
//                are in reset state. 
//
//----------------------------------------------------------------------------
// @Returnvalue   None
//
//----------------------------------------------------------------------------
// @Parameters    None
//
//----------------------------------------------------------------------------
// @Date          2018/5/18
//
//****************************************************************************

// USER CODE BEGIN (Init,1)

// USER CODE END

void CAN_vInit(void)
{
ushort i;

	// USER CODE BEGIN (Init,2)

	// USER CODE END

	///  -----------------------------------------------------------------------
	///  Configuration of Kernel State Configuration Register:
	///  -----------------------------------------------------------------------
	///  - Enable the CAN module(MODEN)
	///  - Enable Bit Protection for MODEN

	MCAN_KSCCFG  =  0x0003;      // load Kernel State Configuration Register

	_nop_();  // one cycle delay 

	_nop_();  // one cycle delay 


	///  -----------------------------------------------------------------------
	///  Configuration of the Module Clock:
	///  -----------------------------------------------------------------------
	///  - the CAN module clock = 40.00 MHz
	///  - Normal divider mode selected

	CAN_FDRL     =  0x43FE;      // load Fractional Divider Register

	///  -----------------------------------------------------------------------
	///  Panel Control
	///  -----------------------------------------------------------------------
	///  - wait until Panel has finished the initialisation

	while(CAN_PANCTRL & CAN_PANCTR_BUSY)	// wait until Panel has finished 
	{ 
		;// the initialisation
	}                         

	///  -----------------------------------------------------------------------
	///  Configuration of CAN Node 0:
	///  -----------------------------------------------------------------------

	///  General Configuration of the Node 0:
	///  - set INIT and CCE

	CAN_NCR0     =  0x0041;      // load NODE 0 control register[15-0]

	///  - load NODE 0 interrupt pointer register

	CAN_NIPR0    =  0x0000;      // load NIPR0_LECINP, ALINP, CFCINP and TRINP

	///  Configuration of the used CAN Port Pins:
	///  - Loop-back mode is disabled
	///  - P2.6 is used for CAN0 Receive input(RXDC0D)
	///  - P2.5 is used for CAN0 Transmit output(TXDC0E)

	P2_IOCR05 = 0x00A0;    //set direction register
	CAN_NPCR0    =  0x0003;      // load node0 port control register


	///  Configuration of the Node 0 Baud Rate:
	///  - required baud rate = 250.000 kbaud
	///  - real baud rate     = 250.000 kbaud
	///  - sample point       = 60.00 %
	///  - there are 5 time quanta before sample point
	///  - there are 4 time quanta after sample point
	///  - the (re)synchronization jump width is 2 time quanta

	CAN_NBTR0L   =  0x344F;      // load NBTR0_DIV8, TSEG2, TSEG1, SJW and BRP

	///  Configuration of the Node 0 Error Counter:
	///  - the error warning threshold value (warning level) is 96

	CAN_NECNT0H = 0x0060;        // load NECNT0_EWRNLVL register
	CAN_NECNT0L = 0x0000;       

	///  Configuration of the Frame Counter:
	///  - Frame Counter Mode: the counter is incremented upon the reception 
	///    and transmission of frames
	///  - frame counter: 0x0000

	CAN_NFCR0H = 0x0000;         // load NFCR0_CFCOV, CFCIE, CFMOD, CFSEL
	CAN_NFCR0L = 0x0000;         // load NFCR0_CFC

	///  -----------------------------------------------------------------------
	///  Configuration of CAN Node 1:
	///  -----------------------------------------------------------------------

	///  General Configuration of the Node 1:
	///  - set INIT and CCE

	CAN_NCR1     =  0x0041;      // load NODE 1 control register[15-0]

	///  - load NODE 1 interrupt pointer register

	CAN_NIPR1    =  0x0000;      // load NIPR1_LECINP, ALINP, CFCINP and TRINP

	///  Configuration of the used CAN Port Pins:
	///  - Loop-back mode is disabled
	///  - P2.4 is used for CAN1 Receive input(RXDC1A)
	///  - P2.2 is used for CAN1 Transmit output(TXDC1B)

	P2_IOCR02 = 0x0090;    //set direction register
	CAN_NPCR1    =  0x0000;      // load node1 port control register


	///  Configuration of the Node 1 Baud Rate:
	///  - required baud rate = 250.000 kbaud
	///  - real baud rate     = 250.000 kbaud
	///  - sample point       = 60.00 %
	///  - there are 5 time quanta before sample point
	///  - there are 4 time quanta after sample point
	///  - the (re)synchronization jump width is 2 time quanta

	CAN_NBTR1L   =  0x344F;      // load NBTR1_DIV8, TSEG2, TSEG1, SJW and BRP

	///  Configuration of the Node 1 Error Counter:
	///  - the error warning threshold value (warning level) is 96

	CAN_NECNT1H = 0x0060;        // load NECNT1_EWRNLVL register
	CAN_NECNT1L = 0x0000;       

	///  Configuration of the Frame Counter:
	///  - Frame Counter Mode: the counter is incremented upon the reception 
	///    and transmission of frames
	///  - frame counter: 0x0000

	CAN_NFCR1H = 0x0000;         // load NFCR1_CFCOV, CFCIE, CFMOD, CFSEL
	CAN_NFCR1L = 0x0000;         // load NFCR1_CFC

	///  -----------------------------------------------------------------------
	///  Configuration of CAN Node 2:
	///  -----------------------------------------------------------------------

	///  General Configuration of the Node 2:
	///  - set INIT and CCE

	CAN_NCR2     =  0x0041;      // load NODE 2 control register[15-0]

	///  - load NODE 2 interrupt pointer register

	CAN_NIPR2    =  0x0000;      // load NIPR2_LECINP, ALINP, CFCINP and TRINP

	///  Configuration of the used CAN Port Pins:
	///  - Loop-back mode is disabled
	///  - P4.3 is used for CAN2 Receive inputA(RXDC2A)
	///  - P4.2 is used for CAN2 Transmit output(TXDC2B)

	P4_IOCR02 = 0x00A0;    //set direction register
	CAN_NPCR2    =  0x0000;      // load node2 port control register


	///  Configuration of the Node 2 Baud Rate:
	///  - required baud rate = 250.000 kbaud
	///  - real baud rate     = 250.000 kbaud
	///  - sample point       = 60.00 %
	///  - there are 5 time quanta before sample point
	///  - there are 4 time quanta after sample point
	///  - the (re)synchronization jump width is 2 time quanta

	CAN_NBTR2L   =  0x344F;      // load NBTR2_DIV8, TSEG2, TSEG1, SJW and BRP

	///  Configuration of the Node 2 Error Counter:
	///  - the error warning threshold value (warning level) is 96

	CAN_NECNT2H = 0x0060;        // load NECNT2_EWRNLVL register
	CAN_NECNT2L = 0x0000;       

	///  Configuration of the Frame Counter:
	///  - Frame Counter Mode: the counter is incremented upon the reception 
	///    and transmission of frames
	///  - frame counter: 0x0000

	CAN_NFCR2H = 0x0000;         // load NFCR2_CFCOV, CFCIE, CFMOD, CFSEL
	CAN_NFCR2L = 0x0000;         // load NFCR2_CFC

	///  -----------------------------------------------------------------------
	///  Configuration of CAN Node 3:
	///  -----------------------------------------------------------------------

	///  General Configuration of the Node 3:
	///  - set INIT and CCE

	CAN_NCR3     =  0x0041;      // load NODE 3 control register[15-0]

	///  - load NODE 3 interrupt pointer register

	CAN_NIPR3    =  0x0000;      // load NIPR3_LECINP, ALINP, CFCINP and TRINP

	///  Configuration of the used CAN Port Pins:
	///  - Loop-back mode is disabled
	///  - P10.14 is used for CAN3 Receive input(RXDC3C)
	///  - P10.13 is used for CAN3 Transmit Output(TXDC3C)

	P10_IOCR13 = 0x00A0;    //set direction register
	CAN_NPCR3    =  0x0002;      // load node3 port control register


	///  Configuration of the Node 3 Baud Rate:
	///  - required baud rate = 250.000 kbaud
	///  - real baud rate     = 250.000 kbaud
	///  - sample point       = 60.00 %
	///  - there are 5 time quanta before sample point
	///  - there are 4 time quanta after sample point
	///  - the (re)synchronization jump width is 2 time quanta

	CAN_NBTR3L   =  0x344F;      // load NBTR3_DIV8, TSEG2, TSEG1, SJW and BRP

	///  Configuration of the Node 3 Error Counter:
	///  - the error warning threshold value (warning level) is 96

	CAN_NECNT3H = 0x0060;        // load NECNT3_EWRNLVL register
	CAN_NECNT3L = 0x0000;       

	///  Configuration of the Frame Counter:
	///  - Frame Counter Mode: the counter is incremented upon the reception 
	///    and transmission of frames
	///  - frame counter: 0x0000

	CAN_NFCR3H = 0x0000;         // load NFCR3_CFCOV, CFCIE, CFMOD, CFSEL
	CAN_NFCR3L = 0x0000;         // load NFCR3_CFC

	///  -----------------------------------------------------------------------
	///  Configuration of CAN Node 4:
	///  -----------------------------------------------------------------------

	///  General Configuration of the Node 4:
	///  - set INIT and CCE

//	CAN_NCR4     =  0x0041;      // load NODE 4 control register[15-0]

	///  -----------------------------------------------------------------------
	///  Configuration of CAN Node 5:
	///  -----------------------------------------------------------------------

	///  General Configuration of the Node 5:
	///  - set INIT and CCE

//	CAN_NCR5     =  0x0041;      // load NODE 5 control register[15-0]

	///  -----------------------------------------------------------------------
	///  Configuration of the CAN Message Object List Structure:
	///  -----------------------------------------------------------------------

  ///  Allocate MOs for CAN 1:

    SetListCommand(0x01C7,0x0002);
	SetListCommand(0x0158,0x0002);  // MO88 for list 1 ;in--ERTU3状态2
    SetListCommand(0x01C6,0x0002);
    SetListCommand(0x0157,0x0002);  // MO87 for list 1 ;in--ERTU2状态2
    SetListCommand(0x01C5,0x0002);
    SetListCommand(0x0156,0x0002);  // MO86 for list 1 ;in--ERTU1状态2
    SetListCommand(0x01C4,0x0002);
    SetListCommand(0x0155,0x0002);  // MO85 for list 1 ;in--MRTU3状态1
    SetListCommand(0x01C3,0x0002);
	SetListCommand(0x0154,0x0002);  // MO84 for list 1 ;in--MRTU2状态1
    SetListCommand(0x01C2,0x0002);
    SetListCommand(0x0153,0x0002);  // MO83 for list 1 ;in--MRTU1状态1
    SetListCommand(0x01C1,0x0002);
    SetListCommand(0x0152,0x0002);  // MO82 for list 1 ;in--ERTU3状态1 
    SetListCommand(0x01C0,0x0002);
    SetListCommand(0x0151,0x0002);  // MO81 for list 1 ;in--ERTU2状态1
    SetListCommand(0x01BF,0x0002);
    SetListCommand(0x0150,0x0002);  // MO80 for list 1 ;in--ERTU1状态1
    SetListCommand(0x01BE,0x0002);
	SetListCommand(0x0148,0x0002);  // MO72 for list 1 ;in--ERTU3心跳
	SetListCommand(0x017B,0x0002);
    SetListCommand(0x0147,0x0002);  // MO71 for list 1 ;in--ERTU2心跳
    SetListCommand(0x017A,0x0002);
    SetListCommand(0x0146,0x0002);  // MO70 for list 1 ;in--ERTU1心跳
    SetListCommand(0x01AF,0x0002);  // MO175 for list 1 ;output--MRTU3自检
    SetListCommand(0x0179,0x0002);
	SetListCommand(0x0137,0x0002);  // MO55 for list 1 ;in--MRTU3:自检应答
    SetListCommand(0x01AE,0x0002);  // MO174 for list 1 ;output--MRTU2自检
    SetListCommand(0x0178,0x0002);
 	SetListCommand(0x0136,0x0002);  // MO54 for list 1 ;in--MRTU2:自检应答
    SetListCommand(0x01AD,0x0002);  // MO173 for list 1 ;output--MRTU1自检
    SetListCommand(0x0113,0x0002);
    SetListCommand(0x0135,0x0002);  // MO53 for list 1 ;in--MRTU1:自检应答
    SetListCommand(0x01AC,0x0002);  // MO172 for list 1 ;output--ERTU3自检
    SetListCommand(0x0112,0x0002);
    SetListCommand(0x0134,0x0002);  // MO52 for list 1 ;in--ERTU3:自检应答
    SetListCommand(0x01AB,0x0002);  // MO171 for list 1 ;output--ERTU2自检
    SetListCommand(0x0111,0x0002);
    SetListCommand(0x0133,0x0002);  // MO51 for list 1 ;in--ERTU2:自检应答
    SetListCommand(0x01AA,0x0002);  // MO170 for list 1 ;output--ERTU1自检
    SetListCommand(0x0110,0x0002);
    SetListCommand(0x0132,0x0002);  // MO50 for list 1 ;in--ERTU1:自检应答
    SetListCommand(0x019B,0x0002);  // MO155 for list 1 ;output--MRTU3参数配置指令
    SetListCommand(0x010F,0x0002);
	SetListCommand(0x0123,0x0002);  // MO35 for list 1 ;in--MRTU3参数配置应答
    SetListCommand(0x019A,0x0002);  // MO154 for list 1 ;output--MRTU2参数配置指令
    SetListCommand(0x010E,0x0002);
	SetListCommand(0x0122,0x0002);  // MO34 for list 1 ;in--MRTU2参数配置应答
    SetListCommand(0x0199,0x0002);  // MO153 for list 1 ;output--MRTU1参数配置指令
    SetListCommand(0x010D,0x0002);
    SetListCommand(0x0121,0x0002);  // MO33 for list 1 ;in--MRTU1参数配置应答
    SetListCommand(0x0198,0x0002);  // MO152 for list 1 ;output--ERTU3过程控制指令
    SetListCommand(0x010C,0x0002);
    SetListCommand(0x0120,0x0002);  // MO32 for list 1 ;in--ERTU3过程控制应答 
 	SetListCommand(0x0197,0x0002);  // MO151 for list 1 ;output--ERTU2过程控制指令
	SetListCommand(0x010B,0x0002);
	SetListCommand(0x011F,0x0002);  // MO31 for list 1 ;in--ERTU2过程控制应答
    SetListCommand(0x0196,0x0002);  // MO150 for list 1 ;output--ERTU1过程控制指令
    SetListCommand(0x010A,0x0002);
    SetListCommand(0x011E,0x0002);  // MO30 for list 1 ;in--ERTU1过程控制应答
  ///  Allocate MOs for CAN 2:
    SetListCommand(0x02D1,0x0002);
	SetListCommand(0x0262,0x0002);  // MO98 for list 2 ;in--ERTU3状态2
    SetListCommand(0x02D0,0x0002);
    SetListCommand(0x0261,0x0002);  // MO97 for list 2 ;in--ERTU2状态2
    SetListCommand(0x02CF,0x0002);
    SetListCommand(0x0260,0x0002);  // MO96 for list 2 ;in--ERTU1状态2
    SetListCommand(0x02CE,0x0002);
    SetListCommand(0x025F,0x0002);  // MO95 for list 2 ;in--MRTU3状态1
    SetListCommand(0x02CD,0x0002);
	SetListCommand(0x025E,0x0002);  // MO94 for list 2 ;in--MRTU2状态1
    SetListCommand(0x02CC,0x0002);
    SetListCommand(0x025D,0x0002);  // MO93 for list 2 ;in--MRTU1状态1
    SetListCommand(0x02CB,0x0002);
    SetListCommand(0x025C,0x0002);  // MO92 for list 2 ;in--ERTU3状态1 
    SetListCommand(0x02CA,0x0002);
    SetListCommand(0x025B,0x0002);  // MO91 for list 2 ;in--ERTU3状态1
    SetListCommand(0x02C9,0x0002);
    SetListCommand(0x025A,0x0002);  // MO90 for list 2 ;in--ERTU1状态1
    SetListCommand(0x02C8,0x0002);
	SetListCommand(0x024D,0x0002);  // MO77 for list 2 ;in--ERTU3心跳
	SetListCommand(0x027F,0x0002);
    SetListCommand(0x024C,0x0002);  // MO76 for list 2 ;in--ERTU2心跳
    SetListCommand(0x027E,0x0002);
    SetListCommand(0x024B,0x0002);  // MO75 for list 2 ;in--ERTU1心跳
    SetListCommand(0x02B9,0x0002);  // MO185 for list 2 ;output--MRTU3自检
    SetListCommand(0x027D,0x0002);
 	SetListCommand(0x0241,0x0002);  // MO65 for list 2 ;in--MRTU3:自检应答
    SetListCommand(0x02B8,0x0002);  // MO184 for list 2 ;output--MRTU2自检
    SetListCommand(0x027C,0x0002);
 	SetListCommand(0x0240,0x0002);  // MO64 for list 2 ;in--MRTU2:自检应答
    SetListCommand(0x02B7,0x0002);  // MO183 for list 2 ;output--MRTU1自检
    SetListCommand(0x021D,0x0002);
    SetListCommand(0x023F,0x0002);  // MO63 for list 2 ;in--MRTU1:自检应答
    SetListCommand(0x02B6,0x0002);  // MO182 for list 2 ;output--ERTU3自检
    SetListCommand(0x021C,0x0002);
    SetListCommand(0x023E,0x0002);  // MO62 for list 2 ;in--ERTU3:自检应答
    SetListCommand(0x02B5,0x0002);  // MO181 for list 2 ;output--ERTU2自检
    SetListCommand(0x021B,0x0002);
    SetListCommand(0x023D,0x0002);  // MO61 for list 2 ;in--ERTU2:自检应答
    SetListCommand(0x02B4,0x0002);  // MO180 for list 2 ;output--ERTU1自检
	SetListCommand(0x021A,0x0002);
    SetListCommand(0x023C,0x0002);  // MO60 for list 2 ;in--ERTU1:自检应答
    SetListCommand(0x02A5,0x0002);  // MO165 for list 2 ;output--MRTU3参数配置指令
    SetListCommand(0x0219,0x0002);
 	SetListCommand(0x022D,0x0002);  // MO45 for list 2 ;in--MRTU3: 转发指令（MRTU参数配置）应答
    SetListCommand(0x02A4,0x0002);  // MO164 for list 2 ;output--MRTU2参数配置指令
    SetListCommand(0x0218,0x0002);
	SetListCommand(0x022C,0x0002);  // MO44 for list 2 ;in--MRTU2: 转发指令（MRTU参数配置）应答
    SetListCommand(0x02A3,0x0002);  // MO163 for list 2 ;output--MRTU1参数配置指令
    SetListCommand(0x0217,0x0002);
    SetListCommand(0x022B,0x0002);  // MO43 for list 2 ;in--MRTU1: 转发指令（MRTU参数配置）应答
    SetListCommand(0x02A2,0x0002);  // MO162 for list 2 ;output--ERTU3过程控制指令
	SetListCommand(0x0216,0x0002);
    SetListCommand(0x022A,0x0002);  // MO42 for list 2 ;in--ERTU3: 转发指令（ERTU过程控制）应答
	SetListCommand(0x02A1,0x0002);  // MO161 for list 2 ;output--ERTU2过程控制指令
    SetListCommand(0x0215,0x0002);
	SetListCommand(0x0229,0x0002);  // MO41 for list 2 ;in--ERTU2: 转发指令（ERTU过程控制）应答
    SetListCommand(0x02A0,0x0002);  // MO160 for list 2 ;output--ERTU1过程控制指令
    SetListCommand(0x0214,0x0002);
    SetListCommand(0x0228,0x0002);  // MO40 for list 2 ;in--ERTU1: 转发指令（ERTU过程控制）应答
	
	
	///  Allocate MOs for CAN A:

    SetListCommand(0x038B,0x0002);  // MO139 for list A ;out--转发RTU测控状态2
    SetListCommand(0x038A,0x0002);  // MO138 for list A ;out--转发RTU测控状态1
    SetListCommand(0x03DB,0x0002);
    SetListCommand(0x0388,0x0002);  // MO136 for list A ;out--测控状态2
    SetListCommand(0x03DA,0x0002);
    SetListCommand(0x0387,0x0002);  // MO135 for list A ;out--测控状态1
    SetListCommand(0x03D9,0x0002);
    SetListCommand(0x0386,0x0002);  // MO134 for list A ;out--测控心跳
    SetListCommand(0x03D8,0x0002);
	SetListCommand(0x0385,0x0002);  // MO133 for list A ;out--转发指令应答
    SetListCommand(0x03D7,0x0002);
    SetListCommand(0x03D6,0x0002);
    SetListCommand(0x03D5,0x0002);
    SetListCommand(0x03D4,0x0002);
 	SetListCommand(0x0303,0x0002);  // MO3 for list A ;in--转发指令
    SetListCommand(0x0384,0x0002);  // MO132 for list A ;out--参数配置/查询应答
	SetListCommand(0x03D3,0x0002);
    SetListCommand(0x03D2,0x0002);
    SetListCommand(0x036D,0x0002);
    SetListCommand(0x036C,0x0002);
	SetListCommand(0x0302,0x0002);  // MO2 for list A ;in--参数配置/查询指令
    SetListCommand(0x0383,0x0002);  // MO131 for list A ;out--开关指令应答
	SetListCommand(0x036B,0x0002);
    SetListCommand(0x036A,0x0002);
	SetListCommand(0x0369,0x0002);
    SetListCommand(0x0368,0x0002);
	SetListCommand(0x0301,0x0002);  // MO1 for list A ;in--开关指令
    SetListCommand(0x0382,0x0002);  // MO130 for list A ;out--紧急关机应答
    SetListCommand(0x0367,0x0002);
    SetListCommand(0x0366,0x0002);
	SetListCommand(0x0365,0x0002);
    SetListCommand(0x0364,0x0002);
    SetListCommand(0x0300,0x0002);  // MO0 for list A ;in--紧急关机

  ///  Allocate MOs for CAN B:

    SetListCommand(0x0495,0x0002);  // MO149 for list B ;out--转发RTU测控状态2
    SetListCommand(0x0494,0x0002);  // MO148 for list B ;out--转发RTU测控状态1
    SetListCommand(0x04E5,0x0002);
	SetListCommand(0x0492,0x0002);  // MO146 for list B ;out--测控状态2
    SetListCommand(0x04E4,0x0002);
    SetListCommand(0x0491,0x0002);  // MO145 for list B ;out--测控状态1
    SetListCommand(0x04E3,0x0002);
    SetListCommand(0x0490,0x0002);  // MO144 for list B ;out--测控心跳
    SetListCommand(0x04E2,0x0002);
	SetListCommand(0x048F,0x0002);  // MO143 for list B ;out--转发指令应答
    SetListCommand(0x04E1,0x0002);
    SetListCommand(0x04E0,0x0002);
    SetListCommand(0x04DF,0x0002);
    SetListCommand(0x04DE,0x0002); 
	SetListCommand(0x0407,0x0002);  // MO7 for list B ;in--转发指令
    SetListCommand(0x048E,0x0002);  // MO142 for list B ;out--参数配置/查询应答
    SetListCommand(0x04DD,0x0002);
    SetListCommand(0x04DC,0x0002);
    SetListCommand(0x0477,0x0002);
    SetListCommand(0x0476,0x0002);
	SetListCommand(0x0406,0x0002);  // MO6 for list B ;in--参数配置/查询指令
    SetListCommand(0x048D,0x0002);  // MO141 for list B ;out--开关指令应答
    SetListCommand(0x0475,0x0002);
    SetListCommand(0x0474,0x0002);
    SetListCommand(0x0473,0x0002);
    SetListCommand(0x0472,0x0002);
	SetListCommand(0x0405,0x0002);  // MO5 for list B ;in--开关指令
    SetListCommand(0x048C,0x0002);  // MO140 for list B ;out--紧急关机应答
    SetListCommand(0x0471,0x0002);
    SetListCommand(0x0470,0x0002);
    SetListCommand(0x046F,0x0002);
    SetListCommand(0x046E,0x0002);
    SetListCommand(0x0404,0x0002);  // MO4 for list B ;in--紧急关机

	SetMessageArg();


  ///  -----------------------------------------------------------------------
  ///  Initialization of the FIFO Pointer:
  ///  -----------------------------------------------------------------------

  for (i = 0; i < 236; i++)
  {
    ubFIFOWritePtr[i] = (ubyte)(CAN_HWOBJ[i].uwMOFGPRL & 0x00FF);
    ubFIFOReadPtr[i]  = (ubyte)(CAN_HWOBJ[i].uwMOFGPRL & 0x00FF);
  }

  //   -----------------------------------------------------------------------
  //   Start the CAN Nodes:
  //   -----------------------------------------------------------------------

  ///  - ------------- CAN_NCR0 ----------------------------------------------

    CAN_NCR0 &= ~ (uword) 0x0041; // reset INIT and CCE
  ///  - ------------- CAN_NCR1 ----------------------------------------------

    CAN_NCR1 &= ~ (uword) 0x0041; // reset INIT and CCE
  ///  - ------------- CAN_NCR2 ----------------------------------------------

    CAN_NCR2 &= ~ (uword) 0x0041; // reset INIT and CCE
  ///  - ------------- CAN_NCR3 ----------------------------------------------

    CAN_NCR3 &= ~ (uword) 0x0041; // reset INIT and CCE

	delay_us(100);


} //  End of function CAN_vInit
//****************************************************************************
// @Function      ubyte CAN_ubWriteFIFO(ubyte ubObjNr, stCAN_SWObj *pstObj) 
//
//----------------------------------------------------------------------------
// @Description   This function sets up the next free TRANSMIT message object 
//                which is part of a FIFO. This includes the 8 data bytes, 
//                the identifier (11- or 29-bit) and the data number (0-8 
//                bytes). The direction bit (DIR) and the EDE-bit can not be 
//                changed. The acceptance mask register and the Frame Counter 
//                remains unchanged. This function checks whether the choosen 
//                message object is still executing a transmit request, or if 
//                the object can be accessed exclusively. 
//                The structure of the SW message object is defined in the 
//                header file CAN.h (see CAN_SWObj).
//                Note: 
//                This function can only used for TRANSMIT objects which are 
//                configured for FIFO base functionality. 
//
//----------------------------------------------------------------------------
// @Returnvalue   0: message object is busy (a transfer is active); 1: the 
//                message object was configured and the transmite is 
//                requested; 2: this is not a FIFO base object
//
//----------------------------------------------------------------------------
// @Parameters    ubObjNr: 
//                Number of the FIFO base object
// @Parameters    *pstObj: 
//                Pointer on a message object
//
//
//****************************************************************************

ubyte CAN_ubWriteFIFO(ubyte ubObjNr, stCAN_SWObj *pstObj)
{
  ubyte i,j;
  ubyte ubReturn = 2;

  if((CAN_HWOBJ[ubObjNr].uwMOFCRL & 0x000F) == 0x0002)    // if transmit FIFO base object 
  {
    j = ubFIFOWritePtr[ubObjNr];

    ubReturn = 0;
    if((CAN_HWOBJ[j].uwMOCTRL & 0x0100) == 0x0000)        // if reset TXRQ 
    {
      if(j == ((CAN_HWOBJ[ubObjNr].uwMOFGPRL & 0xFF00) >> 8))      // last MO in a list
      {
        // WritePtr = BOT of the base object
        ubFIFOWritePtr[ubObjNr] = (ubyte)(CAN_HWOBJ[ubObjNr].uwMOFGPRL & 0x00FF);
      }
      else
      {
        // WritePtr = PNEXT of the current selected slave
        ubFIFOWritePtr[ubObjNr] = (ubyte)((CAN_HWOBJ[j].uwMOCTRH & 0xFF00) >> 8);
      }

      CAN_HWOBJ[j].uwMOCTRL = (uword)0x0008;                     // reset NEWDAT 

      CAN_HWOBJ[j].uwMOARH  &= ~(uword)0x1FFF;

      if(CAN_HWOBJ[j].uwMOARH & 0x2000)                   // extended identifier
      {
        CAN_HWOBJ[j].uwMOARH |= (uword)((pstObj->ulID >> 16) & 0x1FFF);
        CAN_HWOBJ[j].uwMOARL = (uword)(pstObj->ulID & 0xFFFF);
      }
      else                                                // if standard identifier
      {
        CAN_HWOBJ[j].uwMOARH |= (uword)((pstObj->ulID & 0x07FF) << 2);
        CAN_HWOBJ[j].uwMOARL = (uword)0x0000;
      }
	  if(7 <= (pstObj->ubMOCfg & 0x0F))
	  {
		  pstObj->ubMOCfg &= (ubyte)0xF0;
		  pstObj->ubMOCfg |= (ubyte)0x08;
	  }
	  else
	  {
		  pstObj->ubMOCfg ++;
		  pstObj->ubMOCfg &= (ubyte)0xFE;
	  }
		
      CAN_HWOBJ[j].uwMOFCRH &= ~(uword)0x0F00;
      CAN_HWOBJ[j].uwMOFCRH |= ((uword)(pstObj->ubMOCfg & 0x0F) << 8);

      for(i = 0; i < (pstObj->ubMOCfg & 0x0E); i++)
      {
        CAN_HWOBJ[j].ubData[i] = pstObj->ubData[i];
      }

      CAN_HWOBJ[j].uwMOCTRH  = (uword)0x0128;              // set TXRQ, NEWDAT, MSGVAL 

      ubReturn = 1;
    }
  }
  return(ubReturn);

} //  End of function CAN_ubWriteFIFO


//****************************************************************************
// 函数:     ubyte CAN_ubReadFIFO(ubyte ubObjNr, stCAN_SWObj *pstObj) 
//
//----------------------------------------------------------------------------
// 描述:          This function reads the next RECEIVE message object which 
//                is part of a . It checks whether the selected RECEIVE 
//                OBJECT has received a new message. If so the forwarded SW 
//                message object is filled with the content of the HW message 
//                object and the functions returns the value "1". The 
//                structure of the SW message object is defined in the header 
//                file CAN.h (see CAN_SWObj).
//                Note: 
//                This function can only used for RECEIVE objects which are 
//                configured for FIFO base functionality. 
//                Be sure that no interrupt is enabled for the FIFO objects. 
//
//----------------------------------------------------------------------------
// @Returnvalue   0: the message object has not received a new message; 1: 
//                the message object has received a new message; 2: this is 
//                not a FIFO base object; 3: a previous message was lost; 4: 
//                the received message is corrupted; 5:the length of received
//                message is not equal to claim;
//----------------------------------------------------------------------------
// @Parameters    ubObjNr: 
//                Number of the FIFO base object
// @Parameters    *pstObj: 
//                Pointer on a message object to be filled by this function
//
//****************************************************************************

ubyte CAN_ubReadFIFO(ubyte ubObjNr, stCAN_SWObj *pstObj)
{
	ubyte i,j;
	ubyte ubReturn;
	ubyte ubDLC;
	

	if((CAN_HWOBJ[ubObjNr].uwMOFCRL & 0x000F) == 0x0001)    // if receive FIFO base object 
	{
		j = ubFIFOReadPtr[ubObjNr];

		if(CAN_HWOBJ[j].uwMOCTRL & 0x0008)                    // if NEWDAT 
		{
			CAN_HWOBJ[j].uwMOCTRL = 0x0008;                     // clear NEWDAT

			if(j == ((CAN_HWOBJ[ubObjNr].uwMOFGPRL & 0xFF00) >> 8))      // last MO in a list
			{
			// ReadPtr = BOT of the base object
				ubFIFOReadPtr[ubObjNr] = (ubyte)(CAN_HWOBJ[ubObjNr].uwMOFGPRL & 0x00FF);
			}
			else
			{
			// ReadPtr = PNEXT of the current selected slave
				ubFIFOReadPtr[ubObjNr] = (ubyte)((CAN_HWOBJ[j].uwMOCTRH & 0xFF00) >> 8);
			}

			// check if the previous message was lost 
			if(CAN_HWOBJ[j].uwMOCTRL & 0x0010)                  // if set MSGLST 
			{
				CAN_HWOBJ[j].uwMOCTRL = 0x0010;                   // reset MSGLST 
				ubReturn = 3;
			}
			else
			{
				ubDLC = pstObj->ubMOCfg & 0x0F;		//get reading length required
				if(7 <= ubDLC)
				{
					ubDLC = 8;
				}
				else
				{
					ubDLC ++;
					ubDLC &= 0x0E;
				}
				pstObj->ubMOCfg = (ubyte)((CAN_HWOBJ[j].uwMOFCRH >> 8) & 0x000F ); //MOFCRnH[11-8] DLC

				for(i = 0; i < (ubDLC > pstObj->ubMOCfg ? ubDLC : pstObj->ubMOCfg); i++)	//read  all date 
				{
					pstObj->ubData[i] = CAN_HWOBJ[j].ubData[i];
				}
				pstObj->ubMOCfg |= (ubyte)((CAN_HWOBJ[j].uwMOCTRL & 0x0800) >> 7);// set DIR if transmit object

				if(CAN_HWOBJ[j].uwMOARH & 0x2000)             // if extended identifier
				{
					pstObj->ulID = (((ulong)(CAN_HWOBJ[j].uwMOARH & 0x1FFF))<<16) + CAN_HWOBJ[j].uwMOARL;

					pstObj->ubMOCfg = pstObj->ubMOCfg | 0x20;         // set IDE
				}
				else                                                // standard identifier
				{
					pstObj->ulID = (CAN_HWOBJ[j].uwMOARH & 0x1FFF) >> 2;
				}

				pstObj->uwCounter = CAN_HWOBJ[j].uwMOIPRH;

				// check if the message was corrupted 
				if(CAN_HWOBJ[j].uwMOCTRL & 0x0008)                  // if NEWDAT 
				{
					CAN_HWOBJ[j].uwMOCTRL = 0x0008;                   // clear NEWDAT
					ubReturn = 4;
				}
				else if(ubDLC == (pstObj->ubMOCfg & 0x0F))
				{
					ubReturn = 1;
				}
				else
				{
					ubReturn = 5;
				}
			}
		}
		else
		{
			ubReturn = 0;
		}
	}
	else
	{
		ubReturn = 2;
	}
	return(ubReturn);

} //  End of function CAN_ubReadFIFO

