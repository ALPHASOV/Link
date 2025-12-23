
/****************************************************************************
// 文件名      Main.c
//----------------------------------------------------------------------------
// 处理器:	Infineon XC2267M-104F80
//
// 编译器:	Keil 2.1
//
//
// 描述:	主程序及初始化函数入口.
****************************************************************************/
#include "Main.h"
//****************************************************************************
// @Function      void main(void) 
//
//----------------------------------------------------------------------------
// @Description   This is the main function.
//
//----------------------------------------------------------------------------
// @Returnvalue   None
//
//----------------------------------------------------------------------------
// @Parameters    None
//
//----------------------------------------------------------------------------
//
//****************************************************************************
void main()
{
	uword volatile far * VPtr;
	uword BusOff_Status;
	ubyte channel,cnt_adc,No_adc;
	ubyte idel;
	PSW_IEN        =  0;   //禁止中断       
	vInit();	//系统初始化
	ReStore_Para_Init();	//AD系数初始化
	PSW_IEN        =  1;    //开中断          
	__asm {ENWDT};	//使能看门狗
	channel = 0;
	cnt_adc = 0;
	while(1)
	{
		_srvwdt_();		//喂狗
		if(0xAA == Sync_Start)
		{
			idel = CAN_AB_Cmd();			//通过CANAB接收来自于主控的指令,周期1ms
			if(0 == idel)
			{
				idel = CAN_AB_TM();			//通过CANAB向主控发送心跳、遥测1、遥测2
			}
			if(0 == idel)
			{
				idel = CAN_12_TM();			//通过CAN12接收心跳、遥测1、遥测2，转发给主控
			}
			if(0 == idel)
			{
				idel = CAN_12_AnsCmd();		//通过CAN12接收RTU转发指令回令,延迟15ms,
			}
			if(0 == idel)
			{
				idel = CAN_12_SelfTest();		//发送/接收自检
			}
			if(0 == idel)
			{
				idel = Get_IOstate();		//读取外设温度保护传感器
			}			
			if(0 == idel) 
			{
				if(0xAA == TaskAD.Status)
				{
					Adc_Read(cnt_adc ++);//启动AD转换，读取转换结果
					if(MAX_READ_CNT <= cnt_adc)	//达到指定采集次数
					{
						TaskAD.Status = 0x11;
						cnt_adc = 0;
					}
				}
				else if(0x11 == TaskAD.Status)
				{
					ADC_Filter();
					TaskAD.Status = 0x22;
					No_adc = 0;
				}
				else if(0x22 == TaskAD.Status)
				{
					Get_AD_Value(No_adc ++);
					if(ADC_TOTAL <= No_adc)
					{
						TaskAD.Status = 0x55;
					}
				}
				else	//总线离线状态判断,CAN1/CAN2/CANA/CANB:CAN_NSR$channel
				{
					VPtr = (uword volatile far *) (CAN_NSCR[channel] + 0x00000004);	//get CAN_NSRn adr.
					BusOff_Status = * VPtr & 0x0080;
					if(BusOff_Status)	//CAN_NSRn.7 == 1
					{
						VPtr = (uword volatile far *) CAN_NSCR[channel];	//get CAN_NCRn adr.
						*VPtr &= (uword) 0xFFBE;	//CANBus-off, 等待恢复,CAN_NCR$channel
						delay_us(100);
					}
					channel ++;
					channel &= 3;
				}
			}
			Sync_Start = 0x55;
		}
	}

} //  End of function main


/****************************************************************************
// 过程:	void vInit(void) 
//
//----------------------------------------------------------------------------
// 描述:	初始化.
//		包括:系统时钟、I/O口、SPI、定时器、ADC、CAN总线、中断
//----------------------------------------------------------------------------
// 返回值:	无.
//
//----------------------------------------------------------------------------
// 参数:	无.
//
****************************************************************************/

void vInit(void)
{

	vUnlockProtecReg();     // 允许修改保护寄存器

	vChangeFreq();          // 选定外部晶振,倍频

	IO_vInit();		//   初始化I/O口

	GPT_vInit();	//   定时器(GPT1/GPT2)、中断初始化 


	ADC_vInit();	//   模数转换器初始化(ADC0、ADC1)

	CAN_vInit();	//   initializes the MultiCAN Module (CAN)


	WDT_vInit();	//   看门狗初始化(WDT)

	vLockProtecReg();	// 禁止修改保护寄存器
}


/****************************************************************************
// 过程:	void vUnlockProtecReg(void) 
//
//----------------------------------------------------------------------------
// 描述:	允许修改保护寄存器.
//
//----------------------------------------------------------------------------
// 返回值:	无.
//
//----------------------------------------------------------------------------
// 参数:	无.
//
****************************************************************************/

void vUnlockProtecReg(void)
{
	uword uwPASSWORD;

	SCU_SLC = 0xAAAA;                   // command 0
	SCU_SLC = 0x5554;                   // command 1

	uwPASSWORD = SCU_SLS & 0x00FF;
	uwPASSWORD = (~uwPASSWORD) & 0x00FF;

	SCU_SLC = 0x9600 | uwPASSWORD;      // command 2
	SCU_SLC = 0x0000;                   // command 3
}

/****************************************************************************
// 过程:	void vLockProtecReg(void) 
//
//----------------------------------------------------------------------------
// 描述:	禁止修改保护寄存器.
//
//----------------------------------------------------------------------------
// 返回值:	无.
//
//----------------------------------------------------------------------------
// 参数:	无.
//
****************************************************************************/

void vLockProtecReg(void)
{
	uword uwPASSWORD;

	SCU_SLC = 0xAAAA;                   // command 0
	SCU_SLC = 0x5554;                   // command 1

	uwPASSWORD = SCU_SLS & 0x00FF;
	uwPASSWORD = (~uwPASSWORD) & 0x00FF;

	SCU_SLC = 0x9600 | uwPASSWORD;      // command 2
	SCU_SLC = 0x1800;                   // command 3; new PASSWOR is 0x00

	uwPASSWORD = SCU_SLS & 0x00FF;
	uwPASSWORD = (~uwPASSWORD) & 0x00FF;
	SCU_SLC = 0x8E00 | uwPASSWORD;      // command 4

}


/****************************************************************************
// 过程:	void vChangeFreq(void) 
//
//----------------------------------------------------------------------------
// 描述:	选择外部晶振(8MHz),时钟频率倍频到80MHZ.
//
//----------------------------------------------------------------------------
// 返回值:	无.
//
//----------------------------------------------------------------------------
// 参数:	无.
//
****************************************************************************/

void vChangeFreq(void)
{
	Scs_ErrorType Error;

	Scs_EnableHighPrecOsc(1U);

	//For application and internal application resets, the complete PLL configuration could be avoided
	//The entry from application resets and internal application reset is covered in the following differentiation
	//in int/ext clock in lock/unlocked state.

	if  ((SCU_PLLSTAT & 0x0004) == 0x0004)       // fR derived from Internal clock
	{
		//Normal startup state during boot and the clock
		//has to be in the next step configured on the external crystal
		//use XTAL/VCO, count XTAL clock

		Scs_InitTimer();       // initialize CCU6 timer T13 for SCS driver

		// perform transition from base mode to normal mode, check for error
		Error = Scs_GoFromBaseModeToNormalMode();
		if(Error)
		{
			for(;;)      // this part of code should not be reached
			{
				NOP();
			}
		}

		if ((SCU_PLLSTAT & 0x1009) == 0x1009)      // fR derived from external crystal clock + VCO is locked
		{
			//usually after an application reset where clock need not be configured again.
			//check K2/P/N values and decide whether these values have to be adapted based on application needs.
			NOP();
			//usually the PLL losss of Lock TRAP schould be enabled here.
		}
		else       //fR derived from external crystal clock + VCO is not locked
		{
			//estimate the K1 value and the current frequency
			//reduce K2/P/N values in steps so that the frequency
			//jumps is limited to 20MHz or factor of 5 whichever is minimum
			NOP();
		}
	}
}
void WDT_vInit(void)
{
	// USER CODE BEGIN (Init,2)

	// USER CODE END

	///  - DISWDT executable only until End Of Init
	///  - the input frequency is Fin / 16384
	///  - period in normal watchdog mode =  819.200 usec
	///  - period in time-out mode =  819.200 usec

	CPUCON1       |=  0x0000;      // CPU Control Register 1
	SCU_WDTREL     =  0xFFFC;      // WDT Reload Register
	SCU_WDTCS     |=  0x0000;      // WDT Control and Status Register

	SCU_INTDIS     =  0x0100;      // Interrupt Disable Register
	SCU_INTNP1     =  0x0000;      // Interrupt Node Pointer 1 Register

}
