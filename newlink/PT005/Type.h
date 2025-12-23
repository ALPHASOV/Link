#ifndef _TYPE_H_
#define _TYPE_H_

#include <Intrins.h>

#include  "XC22xxMREGS.H"


typedef enum {

	SynCtrl_Uergent,			//紧急关断应答
	SynCtrl_PDCtrl,				//开关控制指令应答
	SynCtrl_ArgSCCtrl,			//参数配置查询指令应答
	SynCtrl_ExTransmitCtrl,		//转发指令应答
	SynCtrl_ExTransmitsub,		//向RTU转发指令
	SynCtrl_HeartBeat,		//测控心跳
	SynCtrl_Telemetry1,		//测控状态1
	SynCtrl_Telemetry2,		//测控状态2
	SynRTU_HeartBeat,		//ERTU心跳
	SynRTU_Telemetry1,		//RTU状态1
	SynRTU_Telemetry2,		//ERTU状态2
	SynCtrl_SelfTest			//向RTU发自检指令
} CanSentDest;

// Type for SCS error
typedef enum {
  SCS_ERROR_NO_ERROR = 0,        // no error
  SCS_ERROR_TO_OSC_HP_PLLV,      // timeout for high precision oscillator PLLV
  SCS_ERROR_OFW_ATTEMPTS_OSC_HP, // overflow of attempts for high precision oscillator
  SCS_ERROR_TO_OSCSELST,         // timeout for PLLSTAT_OSCSELST
  SCS_ERROR_TO_K1DIV,            // timeout for K1 divider setting
  SCS_ERROR_TO_K2DIV,            // timeout for K2 divider setting
  SCS_ERROR_TO_PDIV,             // timeout for P divider setting
  SCS_ERROR_TO_NDIV,             // timeout for N divider setting
  SCS_ERROR_TO_VCOBYST,          // timeout for VCO bypass switching
  SCS_ERROR_TO_VCO_LOCK,         // timeout for VCO lock
  SCS_ERROR_VCO_UNLOCKED,        // VCO is unlocked
  SCS_ERROR_TO_FSR_BUSY,         // timeout for FSR busy
  SCS_ERROR_TO_GSCSTAT,          // timeout for GSCSTAT
  SCS_ERROR_TO_SEQAEN,           // timeout for SEQAEN
  SCS_ERROR_TO_SEQBEN,           // timeout for SEQBEN
  SCS_ERROR_TO_PSMSTAT,          // timeout for PSMSTAT
  SCS_ERROR_PVC,                 // error PVC
  SCS_ERROR_TO_LSTSEQ,           // timeout for LSTSEQ
  SCS_ERROR_NO_STANDBY           // standby mode not entered
} Scs_ErrorType;
#define MAX_READ_CNT 10		//每周期每通道AD转换次数

/********AD********/
typedef struct {
	/*存储内容*/
	ubyte	sn;						//通道编号
	ubyte	state;					// 是否被使用:1/0 --使用/未使用
	ubyte	para_mode;				//代表物理量类型: 0/1/2 --电压/电流/其它
	ubyte	Status;					//是否标注
	sword	Max_Val;   				//物理量最大值
	sword	Min_Val;   				//*物理量最小值
	sword   K;				//增益 * 1000
	sword   B;  			//偏移量 * 1000
	sword   K1;				//增益 * 1000
	sword   B1;				//偏移量 * 1000
	sword   K2;				//增益 * 1000
	sword   B2;  			//偏移量 * 1000
	uword	store_addr; 			//结构体存储地址
	uword	store_addr1; 			//结构体存储地址
	uword	store_addr2; 			//结构体存储地址
	uword	ReadV[MAX_READ_CNT];	//AD结果寄存器数值
	uword	FilterV;				//AD滤波后数值*8
	sword	PH_Val;  				//所代表物理量值
} ADC_Lib;

typedef union {
	ubyte ch[2];
	sword i;
} INTtoUINT;

/********IO********/
typedef struct {
	ubyte sn;				/*通道编号,0x40*/
	ubyte state;			/*1/0 是/否被使用,0x41*/
	ubyte Port_In_State;	/*0/1状态*/
	ubyte Final_State;		/*0/1 开关量滤波后最终状态*/
	uword delay_cnt;		/*防抖动延时次数,0x42*/
	uword Port_In_cnt;		/*防抖动计数*/
} PORTIN;
/********************************************
***************CAN INFO*********************
/********************************************/
typedef struct {
	ubyte MsgNo;		//message number
	ubyte RS;			//send or receive
	ubyte Priority;		//P-bit4~2,R-bit1,DP-bit0
	ubyte Nod;			//0-CAN A/B,else RTU1~6 nod-CAN 1/2
	ulong Mask;			//掩码,共29位,低16位固定为0xFFFF
} CAN_CONF;
typedef struct {
	ulong ID;				//ID
	ubyte MIDE;
	ubyte IDE;				//扩展位标识，1：扩展帧；0：标准帧
	ubyte DIR;
	ubyte DLC;				//数据长度代码
	ubyte RTR;				//远程发送请求位，1：请求远程发送；0：无请求
	ubyte CanData[8];	//CAN数据0
} Can_Message;


 // ubMOCfg: contains 
 // 'Data Lenght Code(DLC)', --must be even,and 0 <= DLC <= 8
 // 'Identifier Extension bit(IDE) - if 0 standard frame, else 1 extended frame', 
 // 'Message Direction(DIR) - if 0 receive Object, else 1 transmit Object'
 // 'Acceptance Mask bit(MIDE) - if 0 receives both, else 1 receives matching IDE'
 //
 //         7     6      5     4     3     2     1     0
 //      |-----------------------------------------------|
 //      | 0   | MIDE | IDE | DIR |          DLC         |
 //      |-----------------------------------------------|
 //
 // ulID:is four bytes long and contains either the 11-bit identifier or the 29-bit identifier
 //
 // ulMask: is four bytes long and contains either the 11-bit mask or the 29-bit mask
 //
 // ubData[8]: 8 bytes containing the data of a frame
 //
 // uwCounter: is two bytes long and contains the counter value

typedef struct {
     ubyte ubMOCfg;    // message object configuration
     ulong ulID;       // standard (11-bit)/extended (29-bit) identifier
     ulong ulMask;     // standard (11-bit)/extended (29-bit) mask
     ubyte ubData[8];  // 8-bit data bytes
     uword uwCounter;  // frame counter(MOIPRnH[15-0])
 } stCAN_SWObj;

typedef struct {
   uword  uwMOFCRL;    // Function Control Register Low
   uword  uwMOFCRH;    // Function Control Register High
   uword  uwMOFGPRL;   // FIFO/Gateway Pointer Register Low
   uword  uwMOFGPRH;   // FIFO/Gateway Pointer Register High
   uword  uwMOIPRL;    // Interrupt Pointer Register Low
   uword  uwMOIPRH;    // Interrupt Pointer Register High
   uword  uwMOAMRL;    // Acceptance Mask Register Low
   uword  uwMOAMRH;    // Acceptance Mask Register High
   ubyte  ubData[8];   // Message Data 0..7
   uword  uwMOARL;     // Arbitration Register Low
   uword  uwMOARH;     // Arbitration Register High
   uword  uwMOCTRL;    // Control Register Low
   uword  uwMOCTRH;    // Control Register High
} stCanObj;

typedef struct {
	ubyte Status;
	uword TimeCount;
} TaskManage;
typedef struct {
	ubyte Status;
	ubyte No;
	uword TimeCount;
} PeridManage;

#endif  // ifndef _TYPE_H_
