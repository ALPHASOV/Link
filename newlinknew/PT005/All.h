#ifndef _All_H_
#define _All_H_
#include "Type.h"


#define MAX_READ_CNT 10	//每周期每通道AD转换次数
#define ADC_TOTAL 10	//允许使用最多AD通道数 <= 10
#define IO_TOTAL 10		//温控设备数<=10

extern ubyte CAN_ubWriteFIFO(ubyte ubObjNr, stCAN_SWObj *pstObj);
extern ubyte CAN_ubReadFIFO(ubyte ubObjNr, stCAN_SWObj *pstObj);
extern ubyte Gpio_Ctrl(ubyte Gpio_select,ubyte on_off);

void ReStore_Para_Init(void);
//Can message
void TransmitHandle(Can_Message *TransMessage, CanSentDest Dest);
//GPIO Ctrl



void CMD_ArgSetCheck_Ctrl(stCAN_SWObj *ExtObj);
ubyte CmdTransmit(stCAN_SWObj *ExtObj);

uword P15_Mask = 0x0005;
uword P5_Mask = 0x0000;
ubyte i_ch;
void Adc_Read(uword cnt);
void ADC_Filter(void);
void Get_AD_Value(ubyte No);


ubyte Get_Stat(ubyte ch);
//////****FRAM****//////

#define ADC_Head_Addr	0x100
#define	ADC_Start_Addr	0x0200
#define ADC_Length		0x40


//铁电操作码含义

#define WORD_WREN		0x0202		//使能写锁存器
#define WORD_RREN		0x0101		//使能读锁存器


#define MAX_ADDRESS 0x7FFF	//铁电最大地址
void I2C_Read_Enable(uword);
void I2C_Write_Enable(void);
ubyte FRAM_Write(uword Address,ubyte *Fdata,ubyte DataLen);
ubyte FRAM_Read(uword Address,ubyte *Fdata,ubyte DataLen);
sbyte Read_ADC_Head(void);
void Write_ADC_Head(void);
void Write_ADC_BHead(void);

ubyte Store_Para_Init(void);

void I2CWrite(ubyte command);
ubyte I2CRead(void);

void TimeSharing(void);

#define MAX_HBCNT 6	//内网段接收心跳数


/*CAN*/





ADC_Lib ADC_Ptr[ADC_TOTAL];
uword ADC_RCR[ADC_TOTAL] = {0xE1B0,0xE1B4,0xE1B8,0xE1BA,0xE1BC,0xE0B0,0xE0B4,0xE0B6,0xE0B8,0xE0BA};	//AD1:0、2、4、5、6;AD0:0、2、3、4、5状态
uword ADC_RESR[ADC_TOTAL] = {0xE140,0xE144,0xE148,0xE14A,0xE14C,0xE040,0xE044,0xE046,0xE048,0xE04A};	//AD1:0、2、4、5、6;AD0:0、2、3、4、5数据
INTtoUINT farVolt1;
INTtoUINT farVolt2;

/*IO*/
PORTIN PORTIN_Ptr[IO_TOTAL];


ulong MyNod_AB = 0x000000DC, MainNod_AB = 0x0000000C;
#define MyNod_12	0x000000FC
#define SubNod_12_Start	0x00000001;

ulong timingCnt = 0;


extern ubyte Gpio_on_off;

#define CMD_Toatl 4

#define	Uergent			0x08000000
#define	Switch_OnOff	0x0C000000
#define	Arg_Set_Check	0x10000000
#define ExTransmit		0x16000000
#define Ex_PRO_Ctrl		0x0E000000
#define Ex_Arg_Set		0x12000000
#define Heartbeat		0x18000000
#define Telemetry		0x1C000000
#define SelfTest		0x14000000

#define	Uergent_Length			0x02
#define	Switch_OnOff_Length		0x04
#define	Arg_Set_Check_Length	0x08
#define ExTransmit_Length		0x08

ubyte Sync_Start;

ulong UergentID,SwitchOnOffID,ArgSetCheckID,ExTransmitID;

ubyte Ctrl_Uergent = 255;			//CANAB接收紧急关断消息序号
ubyte Ctrl_SwitchOnOff	= 255;	//CANAB接收的开关指令消息序号
ubyte Ctrl_ArgSetCheck	= 255;	//CANB接收的参数配置查询指令序号
ubyte Ctrl_ExTransmit	= 255;	//CANB接收的转发指令消息序号
ubyte Ctrl_AnswerNo[6] = {255,255,255,255,255,255};

#define SilentTime 5000	//静默时间500ms
TaskManage	ChangeNod = {0,0};

#define Task1msDelay	10	//1ms任务周期
TaskManage Task1ms = {0,0};	//初始状态：0；时序：0

#define TaskIODelay 500		//I:50ms任务周期
TaskManage TaskIO = {0,1}
uword TM2_Status = 0;

#define TaskADDelay 4000	//AD:400ms任务周期
TaskManage TaskAD = {0,2}

#define Task1sDelay		10000	//1s任务周期
TaskManage Task1s = {0,Task1sDelay};	//初始状态：0；时序：0

ubyte TaskRHBeatNo[3] = {255,255,255};
#define HB_Overflow_Time 30000				//3秒内至少收到1次心跳或状态1为在线，否则为离线
uword HB_count[MAX_HBCNT] = {0,0,0,0,0,0};




#define Task15msDelay 151	//15.1ms接收转发应答任务延时
TaskManage Task15ms[6] = {{0,0},{0,0},{0,0},{0,0},{0,0},{0,0}};

#define HBitSDelay 10000	//发送心跳、遥测周期
TaskManage TaskSHBeat = {0,7};	
TaskManage TaskSTM1 = {0,17};
TaskManage TaskSTM2 = {0,27};

#define HBitRDelay 5000	//接收心跳、遥测周期
PeridManage TaskRHBeat[3] = {{0,255,107},{0,255,207},{0,255,307}};	//接收ERTU心跳周期任务记时	
PeridManage TaskRTM1[MAX_HBCNT] = {{0,255,117},{0,255,217},{0,255,317},{0,255,407},{0,255,417},{0,255,427}};	//接收RTU遥测1周期任务记时
PeridManage TaskRTM2[3] = {{0,255,127},{0,255,227},{0,255,327}};	//接收ERTU遥测2周期任务记时
#define SelfTestDelay 200	//自检应答延时
TaskManage TaskSSLT[MAX_HBCNT] = {{0,0},{0,0},{0,0},{0,0},{0,0},{0,0}};	//启动发送自检记时
PeridManage TaskRSLT[MAX_HBCNT] = {{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0}};	//等待接收自检记时
ubyte SelfStatus = 0;

ubyte Get_IOstate(void);
ubyte CAN_AB_Cmd(void);
ubyte CAN_12_AnsCmd(void);
ubyte CAN_12_SelfTest(void);
ubyte CAN_AB_TM(void);
ubyte HBTM_Number = 0;
ubyte CAN_12_TM(void);
#endif //end ndef _All_H_