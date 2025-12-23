//****************************************************************************
// @Module        MultiCAN Module (CAN)
// @Filename      CAN.h
// @Project       PCM_OLED.dav
//----------------------------------------------------------------------------
// @Controller    Infineon XC2267M-104F80
//
// @Compiler      Keil
//
// @Codegenerator 2.1
//
// @Description   This file contains all function prototypes and macros for 
//                the CAN module.
//
//----------------------------------------------------------------------------
// @Date          2018/5/18 11:27:20
//
//****************************************************************************


#ifndef _CAN_H_
#define _CAN_H_
#include "Type.h"



#define NECNTL_BASE ((uword volatile far *) 0x200214)
#define NECNTH_BASE ((uword volatile far *) 0x200216)

// USER CODE BEGIN (CAN_Header,3)

// USER CODE END


//****************************************************************************
// @Defines
//****************************************************************************

 // Panel Busy Flag
 #define CAN_PANCTR_BUSY       0x0100

 // Message Object Status Register
 #define MOSTAT_RXPND          0x0001
 #define MOSTAT_TXPND          0x0002
 #define MOSTAT_NEWDAT         0x0008
 #define MOSTAT_MSGLST         0x0010
 #define MOSTAT_RST_MNR        0x0019
 #define MOSTAT_RST_NT         0x000A


 // Structure for a single MultiCAN object
 // A total of 255 such object structures exists


//****************************************************************************
// @Typedefs
//****************************************************************************

 ///  -------------------------------------------------------------------------
 ///  @Definition of a structure for the CAN data
 ///  -------------------------------------------------------------------------

 // The following data type serves as a software message object. Each access to
 // a hardware message object has to be made by forward a pointer to a software
 // message object (MCAN_SWObj). The data type has the following fields:
 //

//****************************************************************************
// @Prototypes Of Global Functions
//****************************************************************************
#define	Uergent			0x08000000
#define	Switch_OnOff	0x0C000000
#define	Arg_Set_Check	0x10000000
#define ExTransmit		0x16000000


extern ulong UergentID,SwitchOnOffID,ArgSetCheckID,ExTransmitID;

void SetListCommand(uword ValueH, uword ValueL);

void CAN_vInit(void);

#define CAN_HWOBJ ((stCanObj volatile far*) 0x201000)
extern ulong MyNod_AB, MainNod_AB;
#define CAN_SEND_Conf 0xAA
#define CAN_RECEIVE_Conf 0x55
typedef struct {
	ubyte MsgNo;
	ubyte RS;			//CAN_RECEIVE_Conf--receive,CAN_SEND_Conf--send
	ubyte Priority;		//P-bit4~2,R-bit1,DP-bit0
	ubyte Nod;			//0-CAN A/B,1~6-CAN 1/2
	ulong Mask;			//掩码,共29位,低16位固定为0xFFFF.
} CAN_CONF;

CAN_CONF Can_Init[98] ={
	{0x00,CAN_RECEIVE_Conf,0x08,0x00,0x1FFFFFFF},	//msg 0~3:紧急关机
	{0x01,CAN_RECEIVE_Conf,0x0C,0x00,0x1FFFFFFF},	//开关指令
	{0x02,CAN_RECEIVE_Conf,0x10,0x00,0x1FFFFFFF},	//参数配置/查询指令
	{0x03,CAN_RECEIVE_Conf,0x16,0x00,0x1F00FFFF},	//转发指令
	{0x04,CAN_RECEIVE_Conf,0x08,0x00,0x1FFFFFFF},	//msg 4~7
	{0x05,CAN_RECEIVE_Conf,0x0C,0x00,0x1FFFFFFF},
	{0x06,CAN_RECEIVE_Conf,0x10,0x00,0x1FFFFFFF},
	{0x07,CAN_RECEIVE_Conf,0x16,0x00,0x1F00FFFF},

	{0x1E,CAN_RECEIVE_Conf,0x0E,0x01,0x1FFFFFFF},	//msg 30~35:ERTU1程控制应答
	{0x1F,CAN_RECEIVE_Conf,0x0E,0x02,0x1FFFFFFF},	//ERTU2程控制应答
	{0x20,CAN_RECEIVE_Conf,0x0E,0x03,0x1FFFFFFF},	//ERTU3程控制应答
	{0x21,CAN_RECEIVE_Conf,0x12,0x04,0x1FFFFFFF},	//MRTU1参数配置应答
	{0x22,CAN_RECEIVE_Conf,0x12,0x05,0x1FFFFFFF},	//MRTU2参数配置应答
	{0x23,CAN_RECEIVE_Conf,0x12,0x06,0x1FFFFFFF},	//MRTU3参数配置应答
	{0x28,CAN_RECEIVE_Conf,0x0E,0x01,0x1FFFFFFF},	//msg 40~45
	{0x29,CAN_RECEIVE_Conf,0x0E,0x02,0x1FFFFFFF},
	{0x2A,CAN_RECEIVE_Conf,0x0E,0x03,0x1FFFFFFF},
	{0x2B,CAN_RECEIVE_Conf,0x12,0x04,0x1FFFFFFF},
	{0x2C,CAN_RECEIVE_Conf,0x12,0x05,0x1FFFFFFF},
	{0x2D,CAN_RECEIVE_Conf,0x12,0x06,0x1FFFFFFF},

	{0x32,CAN_RECEIVE_Conf,0x14,0x01,0x1FFFFFFF},	//msg 50~55:RTU1自检应答
	{0x33,CAN_RECEIVE_Conf,0x14,0x02,0x1FFFFFFF},	//RTU2自检应答
	{0x34,CAN_RECEIVE_Conf,0x14,0x03,0x1FFFFFFF},	//RTU3自检应答
	{0x35,CAN_RECEIVE_Conf,0x14,0x04,0x1FFFFFFF},	//RTU4自检应答
	{0x36,CAN_RECEIVE_Conf,0x14,0x05,0x1FFFFFFF},	//RTU5自检应答
	{0x37,CAN_RECEIVE_Conf,0x14,0x06,0x1FFFFFFF},	//RTU6自检应答
	{0x3C,CAN_RECEIVE_Conf,0x14,0x01,0x1FFFFFFF},	//msg 60~65
	{0x3D,CAN_RECEIVE_Conf,0x14,0x02,0x1FFFFFFF},
	{0x3E,CAN_RECEIVE_Conf,0x14,0x03,0x1FFFFFFF},
	{0x3F,CAN_RECEIVE_Conf,0x14,0x04,0x1FFFFFFF},
	{0x40,CAN_RECEIVE_Conf,0x14,0x05,0x1FFFFFFF},
	{0x41,CAN_RECEIVE_Conf,0x14,0x06,0x1FFFFFFF},

	{0x46,CAN_RECEIVE_Conf,0x18,0x01,0x1FFFFFFF},	//msg 70~72:ERTU1心跳
	{0x46,CAN_RECEIVE_Conf,0x18,0x02,0x1FFFFFFF},	//ERTU2心跳
	{0x46,CAN_RECEIVE_Conf,0x18,0x03,0x1FFFFFFF},	//ERTU3心跳
	{0x4B,CAN_RECEIVE_Conf,0x18,0x01,0x1FFFFFFF},	//msg 75~77
	{0x4C,CAN_RECEIVE_Conf,0x18,0x02,0x1FFFFFFF},
	{0x4D,CAN_RECEIVE_Conf,0x18,0x03,0x1FFFFFFF},

	{0x50,CAN_RECEIVE_Conf,0x1C,0x01,0x1FFFFFFF},	//msg 80~85:RTU1状态1
	{0x51,CAN_RECEIVE_Conf,0x1C,0x02,0x1FFFFFFF},	//RTU2状态1
	{0x52,CAN_RECEIVE_Conf,0x1C,0x03,0x1FFFFFFF},	//RTU3状态1
	{0x53,CAN_RECEIVE_Conf,0x1C,0x04,0x1FFFFFFF},	//RTU4状态1
	{0x54,CAN_RECEIVE_Conf,0x1C,0x05,0x1FFFFFFF},	//RTU5状态1
	{0x55,CAN_RECEIVE_Conf,0x1C,0x06,0x1FFFFFFF},	//RTU6状态1
	{0x5A,CAN_RECEIVE_Conf,0x1C,0x01,0x1FFFFFFF},	//msg 90~95:
	{0x5B,CAN_RECEIVE_Conf,0x1C,0x02,0x1FFFFFFF},
	{0x5C,CAN_RECEIVE_Conf,0x1C,0x03,0x1FFFFFFF},
	{0x5D,CAN_RECEIVE_Conf,0x1C,0x04,0x1FFFFFFF},
	{0x5E,CAN_RECEIVE_Conf,0x1C,0x05,0x1FFFFFFF},
	{0x5F,CAN_RECEIVE_Conf,0x1C,0x06,0x1FFFFFFF},

	{0x56,CAN_RECEIVE_Conf,0x1C,0x01,0x1FFFFFFF},	//msg 86~88:ERTU1状态2
	{0x57,CAN_RECEIVE_Conf,0x1C,0x02,0x1FFFFFFF},	//ERTU2状态2
	{0x58,CAN_RECEIVE_Conf,0x1C,0x03,0x1FFFFFFF},	//ERTU3状态2
	{0x60,CAN_RECEIVE_Conf,0x1C,0x01,0x1FFFFFFF},	//msg 96~98:
	{0x61,CAN_RECEIVE_Conf,0x1C,0x02,0x1FFFFFFF},
	{0x62,CAN_RECEIVE_Conf,0x1C,0x03,0x1FFFFFFF},

	{0x82,CAN_SEND_Conf,0x08,0x00,0x1FFFFFFF},	//msg 130~139:紧急关机应答
	{0x83,CAN_SEND_Conf,0x0C,0x00,0x1FFFFFFF},	//开关指令应答
	{0x84,CAN_SEND_Conf,0x10,0x00,0x1FFFFFFF},	//参数配置/查询应答
	{0x85,CAN_SEND_Conf,0x16,0x00,0x1D00FFFF},	//转发指令应答
	{0x86,CAN_SEND_Conf,0x18,0x00,0x1FFFFFFF},	//测控心跳
	{0x87,CAN_SEND_Conf,0x1C,0x00,0x1FFFFFFF},	//测控状态1
	{0x88,CAN_SEND_Conf,0x1C,0x00,0x1FFFFFFF},	//测控状态1
//	{0x89,CAN_SEND_Conf,0x08,0x00,0x1FFFFFFF},	//
	{0x8A,CAN_SEND_Conf,0x1E,0x00,0x1F00FFFF},	//转发RTU测控状态1
	{0x8B,CAN_SEND_Conf,0x1E,0x00,0x1F00FFFF},	//转发ERTU测控状态2
	{0x8C,CAN_SEND_Conf,0x08,0x00,0x1FFFFFFF},	//msg 140~149:
	{0x8D,CAN_SEND_Conf,0x0C,0x00,0x1FFFFFFF},
	{0x8E,CAN_SEND_Conf,0x10,0x00,0x1FFFFFFF},
	{0x8F,CAN_SEND_Conf,0x16,0x00,0x1D00FFFF},
	{0x90,CAN_SEND_Conf,0x18,0x00,0x1FFFFFFF},
	{0x91,CAN_SEND_Conf,0x1C,0x00,0x1FFFFFFF},
	{0x92,CAN_SEND_Conf,0x1C,0x00,0x1FFFFFFF},
//	{0x93,CAN_SEND_Conf,0x08,0x00,0x1FFFFFFF},
	{0x94,CAN_SEND_Conf,0x1E,0x00,0x1F00FFFF},
	{0x95,CAN_SEND_Conf,0x1E,0x00,0x1F00FFFF},

	{0x96,CAN_SEND_Conf,0x0E,0x01,0x1FFFFFFF},	//msg 150~155:转发ERTU1过程控制指令
	{0x97,CAN_SEND_Conf,0x0E,0x02,0x1FFFFFFF},	//转发ERTU2过程控制指令
	{0x98,CAN_SEND_Conf,0x0E,0x03,0x1FFFFFFF},	//转发ERTU3过程控制指令
	{0x99,CAN_SEND_Conf,0x12,0x04,0x1FFFFFFF},	//转发MRTU1参数配置指令
	{0x9A,CAN_SEND_Conf,0x12,0x05,0x1FFFFFFF},	//转发MRTU2参数配置指令
	{0x9B,CAN_SEND_Conf,0x12,0x06,0x1FFFFFFF},	//转发MRTU3参数配置指令
	{0xA0,CAN_SEND_Conf,0x0E,0x01,0x1FFFFFFF},	//msg 160~165:
	{0xA1,CAN_SEND_Conf,0x0E,0x02,0x1FFFFFFF},
	{0xA2,CAN_SEND_Conf,0x0E,0x03,0x1FFFFFFF},
	{0xA3,CAN_SEND_Conf,0x12,0x04,0x1FFFFFFF},
	{0xA4,CAN_SEND_Conf,0x12,0x05,0x1FFFFFFF},
	{0xA5,CAN_SEND_Conf,0x12,0x06,0x1FFFFFFF},

	{0xAA,CAN_SEND_Conf,0x14,0x01,0x1FFFFFFF},	//msg 170~175:RTU1自检
	{0xAB,CAN_SEND_Conf,0x14,0x02,0x1FFFFFFF},	//RTU2自检
	{0xAC,CAN_SEND_Conf,0x14,0x03,0x1FFFFFFF},	//RTU3自检
	{0xAD,CAN_SEND_Conf,0x14,0x04,0x1FFFFFFF},	//RTU4自检
	{0xAE,CAN_SEND_Conf,0x14,0x05,0x1FFFFFFF},	//RTU5自检
	{0xAF,CAN_SEND_Conf,0x14,0x06,0x1FFFFFFF},	//RTU6自检
	{0xB4,CAN_SEND_Conf,0x14,0x01,0x1FFFFFFF},	//msg 180~155:
	{0xB5,CAN_SEND_Conf,0x14,0x02,0x1FFFFFFF},
	{0xB6,CAN_SEND_Conf,0x14,0x03,0x1FFFFFFF},
	{0xB7,CAN_SEND_Conf,0x14,0x04,0x1FFFFFFF},
	{0xB8,CAN_SEND_Conf,0x14,0x05,0x1FFFFFFF},
	{0xB9,CAN_SEND_Conf,0x14,0x06,0x1FFFFFFF}
};
void SetMessageArg(uword MsgNo);
ubyte CAN_ubWriteFIFO(ubyte ubObjNr, stCAN_SWObj *pstObj);
ubyte CAN_ubReadFIFO(ubyte ubObjNr, stCAN_SWObj *pstObj);

#endif  // ifndef _CAN_H_
