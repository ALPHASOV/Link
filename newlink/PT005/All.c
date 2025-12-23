#include "All.h"

															 
/****************************************************************************
/ 过程:	void FRAM_Write_Enable(void) 
/
/----------------------------------------------------------------------------
/ 描述:	铁电读使能;
/	调用I2C_Read_Enable将数据"使能读锁存器"在时钟P0_2上升沿通过IO_P0_0输出到铁电
/----------------------------------------------------------------------------
/ 返回值:	无
/
/----------------------------------------------------------------------------
/ 参数:	无
/
***************************************************************************/
void I2C_Read_Enable(uword RAddress)
{
	ubyte i;
	IO_vResetPin(IO_P0_3);				//使能片选
	for(i = 0 ; i < 10 ; i++);			//片选至少延时20个指令周期

	I2CWrite((ubyte)((WORD_RREN >> 8) & 0xFF));	//读使能
	I2CWrite((ubyte)(WORD_RREN & 0xFF));
	I2CWrite((ubyte)((RAddress >> 8) & 0xFF));	//设置读首地址
	I2CWrite((ubyte)(RAddress & 0xFF));
}

/****************************************************************************
/ 过程:	void FRAM_Write_Enable(void) 
/
/----------------------------------------------------------------------------
/ 描述:	铁电写使能;
/	调用I2CWrite将数据"使能写锁存器"在时钟P0_2上升沿通过IO_P0_0输出到铁电
/----------------------------------------------------------------------------
/ 返回值:	无
/
/----------------------------------------------------------------------------
/ 参数:	无
/
***************************************************************************/
void I2C_Write_Enable(uword WAddress)
{
	ubyte i;
	IO_vResetPin(IO_P0_3);				//使能片选
	for(i = 0 ; i < 20 ; i++);			//片选至少延时20个指令周期

	I2CWrite((ubyte)((WORD_WREN >> 8) & 0x00FF));	//写使能
	I2CWrite((ubyte)(WORD_WREN & 0x00FF));
	I2CWrite((ubyte)((WAddress >> 8) & 0x00FF));	//设置写首地址
	I2CWrite((ubyte)(WAddress & 0x00FF));
}
/****************************************************************************
/ 过程:	void I2C_RW_Disble(void) 
/
/----------------------------------------------------------------------------
/ 描述:	禁止铁电读写使能;
/	将IO_P0_3设置为高,复位铁电
/----------------------------------------------------------------------------
/ 返回值:	无
/
/----------------------------------------------------------------------------
/ 参数:	无
/
***************************************************************************/

void I2C_RW_Disble(void)
{
	int i;
	IO_vSetPin(IO_P0_3);		//禁止片选
	for(i = 0 ; i < 10 ; i++);	//片选至少延时20个指令周期
}

/****************************************************************************
/ 过程:	void I2CWrite(ubyte command) 
/
/----------------------------------------------------------------------------
/ 描述:	将数据command在时钟P0_2上升沿通过IO_P0_0输出到铁电,高位在前，低位在后
/
/----------------------------------------------------------------------------
/ 返回值:	无
/
/----------------------------------------------------------------------------
/ 参数:	无
/
***************************************************************************/
void I2CWrite(ubyte command)
{
	 ubyte i;

	 for(i = 0 ; i < 8 ; i++ , command << 1)
	 {

		 IO_vSetPin(IO_P0_2);	//时钟上升
		 if((command & 0x80) == 0x80)
		 {
		 	 IO_vSetPin(IO_P0_0);
		 }
		 else
		 {
		 	 IO_vResetPin(IO_P0_0);
		 }
		 IO_vResetPin(IO_P0_2);	//时钟下降
	 }
}
/****************************************************************************
/ 过程:	ubyte I2CRead(void) 
/
/----------------------------------------------------------------------------
/ 描述:	从铁电中读入一个字节数据;
/	在时钟P0_2上升沿通过IO_P0_1输入,高位在前，低位在后
/----------------------------------------------------------------------------
/ 返回值:	ubyte读回数据,
/
/----------------------------------------------------------------------------
/ 参数:	无
/
***************************************************************************/

ubyte I2CRead(void)
{
	 ubyte i;
	 ubyte SSC_Val = 0;

	 for(i = 0 ; i < 8 ; i++)
	 {
		 SSC_Val <<= 1;

		 IO_vSetPin(IO_P0_2);	//时钟上升
		 
		 SSC_Val |= (ubyte)(IO_ubReadPin(IO_P0_1) & 0x1);

		 IO_vResetPin(IO_P0_2);	//时钟下降
	 }
	 return  SSC_Val;
}

/****************************************************************************
/ 函数:	sbyte FRAM_Write(uword Address,ubyte *Fdata,ubyte DataLen) 
/
/----------------------------------------------------------------------------
/ 描述:	向铁电写一帧数据;
/	
/----------------------------------------------------------------------------
/ 返回值:	1:失败;0:成功
/
/----------------------------------------------------------------------------
/ 参数:	
/	Address:写入首地址
/	Fdata:数据缓寸
/	DataLen:数据字节数
***************************************************************************/
ubyte FRAM_Write(uword Address,ubyte *Fdata,ubyte DataLen)
{
	ubyte retcode;
	ubyte *temp_Fdata = Fdata;
	if(Address + DataLen - 1 <= MAX_ADDRESS)
	{
		I2C_Write_Enable(Address);	//铁电写使能
		do
		{
			I2CWrite(*temp_Fdata);		//写入一个字节			
			temp_Fdata++;
			DataLen--;
		}	while(DataLen > 0);		//直到写完一帧数据

		I2C_RW_Disble;				//禁止片选
		retcode = 0;
	}
	else
	{
		retcode = 1;
	}
	return(retcode);
}
/****************************************************************************
/ 函数:	ubyte FRAM_Read(uword Address,ubyte *Fdata,ubyte DataLen) 
/
/----------------------------------------------------------------------------
/ 描述:	从铁电读一帧数据;
/	
/----------------------------------------------------------------------------
/ 返回值:	1:失败;0:成功
/
/----------------------------------------------------------------------------
/ 参数:	
/	Address:读入首地址
/	Fdata:数据缓寸
/	DataLen:数据字节数
***************************************************************************/
ubyte FRAM_Read(uword Address,ubyte *Fdata,ubyte DataLen)
{
	ubyte retcode = 0;
	ubyte *temp_Fdata = Fdata;
	if(Address + DataLen - 1 <= MAX_ADDRESS)
	{
		I2C_Read_Enable(Address);	//铁电读使能
		do
		{
			*temp_Fdata = I2CRead();		//读入一个字节
			temp_Fdata++;
			DataLen--;
		}	while(DataLen > 0);		//直到读完一帧数据
		I2C_RW_Disble;				//禁止片选
		retcode = 0;
	}
	else
	{
		retcode = 1;
	}
	return(retcode);
}
//
////////////////////////////////////////////////
//*************CANA/B 指令处理	****************
////////////////////////////////////////////////

ubyte CAN_AB_Cmd(void)
{
	ubyte MSGcon;
	ubyte i,j;
	ubyte retcode;
	ubyte RecvFlag = 0;
	stCAN_SWObj CanReceived;
	Can_Message Tx_CtrlBack = {0,1,1,1,8,0,{0,0,0,0,0,0,0,0}};	//控制回令
	ubyte cmd_Length[CMD_Toatl] = {Uergent_Length,Switch_OnOff_Length,Arg_Set_Check_Length,ExTransmit_Length};	//命令长度
	if(0xAA == Task1ms.Status)	//每毫秒处理一个指令
	{
		for(i = 0; i < CMD_Toatl; i++)
		{
			for(j = 0; j < 2; j++)
			{
				RecvFlag <<= 4;
				CanReceived.ubMOCfg = cmd_Length[i];
				MSGcon = CAN_ubReadFIFO(i + 4*j, &CanReceived);	//读取指定长度的消息i + 4*j:0/4,1/5,2/6,3/7
				if(MSGcon == 1)//正确收到信息,CANA/B接收信息处理
				{
					RecvFlag |= 0x0A;
					switch(i)
					{
						case 0:		//紧急关断
							if(CanReceived.ulID == UergentID)
							{
								if(CanReceived.ubData[0] != Ctrl_Uergent)	//消息序号不同
								{
									Ctrl_Uergent = CanReceived.ubData[0];
									retcode = Gpio_Ctrl(0xFF,CanReceived.ubData[1]);
								}
								else	//命令重复,	//本次没有需处理事务
								{
									retcode = 0x00;
									RecvFlag &= 0xF0;
								}
							}
							else	//ID错误
							{
								retcode = 0xEE;
							}
							if(retcode)
							{
								Tx_CtrlBack.ID = (ulong)Uergent | (MainNod_AB << 8) | MyNod_AB;
								Tx_CtrlBack.DLC = 4;
								Tx_CtrlBack.CanData[0] = CanReceived.ubData[0];	
								Tx_CtrlBack.CanData[1] = CanReceived.ubData[1];
								Tx_CtrlBack.CanData[2] = 0;
								Tx_CtrlBack.CanData[3] = retcode;
								TransmitHandle(&Tx_CtrlBack,SynCtrl_Uergent);
							}
							break;
						case 1:		//开关指令
							if(CanReceived.ulID == SwitchOnOffID)
							{
								if(CanReceived.ubData[0] != Ctrl_SwitchOnOff)	//消息序号不同
								{
									Ctrl_SwitchOnOff = CanReceived.ubData[0];
									retcode = Gpio_Ctrl(CanReceived.ubData[2],CanReceived.ubData[1]);
								}
								else	//命令重复,	//本次没有需处理事务
								{
									retcode = 0x00;
									RecvFlag &= 0xF0;
								}
							}
							else	//ID错误
							{
								retcode = 0xEE;
							}
							if(0 != retcode)
							{
								Tx_CtrlBack.ID = (ulong)Switch_OnOff | (MainNod_AB << 8) | MyNod_AB;
								Tx_CtrlBack.DLC = 4;
								Tx_CtrlBack.CanData[0] = CanReceived.ubData[0];	
								Tx_CtrlBack.CanData[1] = CanReceived.ubData[1];
								Tx_CtrlBack.CanData[2] = CanReceived.ubData[2];
								Tx_CtrlBack.CanData[3] = retcode;
								TransmitHandle(&Tx_CtrlBack,SynCtrl_PDCtrl);
							}
							break;
						case 2:		//参数配置查询指令
							if(CanReceived.ulID == ArgSetCheckID)
							{
								if(CanReceived.ubData[0] != Ctrl_ArgSetCheck)	//消息序号不同
								{
									Ctrl_ArgSetCheck = CanReceived.ubData[0];
									CMD_ArgSetCheck_Ctrl(&CanReceived);
								}
								else	//命令重复,	//本次没有需处理事务
								{
									RecvFlag &= 0xF0;
								}
							}
							else	//ID错误
							{
								Tx_CtrlBack.ID = (ulong)Arg_Set_Check | (MainNod_AB << 8) | MyNod_AB;
								Tx_CtrlBack.DLC = 8;
								Tx_CtrlBack.CanData[0] = CanReceived.ubData[0];	
								Tx_CtrlBack.CanData[1] = CanReceived.ubData[1];
								Tx_CtrlBack.CanData[2] = CanReceived.ubData[2];
								Tx_CtrlBack.CanData[3] = 0xEE;
								Tx_CtrlBack.CanData[4] = 0x00;
								Tx_CtrlBack.CanData[5] = 0x00;
								Tx_CtrlBack.CanData[6] = 0x00;
								Tx_CtrlBack.CanData[7] = 0x00;
								TransmitHandle(&Tx_CtrlBack,SynCtrl_ArgSCCtrl);
							}
							break;
						case 3:		//转发指令
							if((CanReceived.ulID & 0xFF00FFFF) == ExTransmitID)
							{
								if(CanReceived.ubData[0] != Ctrl_ExTransmit)	//消息序号不同
								{
									Ctrl_ExTransmit = CanReceived.ubData[0];
									retcode = CmdTransmit(&CanReceived);
								}
								else	//命令重复,	//本次没有需处理事务
								{
									retcode = 0x00;
									RecvFlag &= 0xF0;
								}
							}
							else	//ID错误
							{
								retcode = 0xEE;
							}
							if(0 != retcode)
							{
								Tx_CtrlBack.ID = ((ulong)ExTransmit & 0x1C000000) | (MainNod_AB << 8) | MyNod_AB;
								Tx_CtrlBack.DLC = 8;
								Tx_CtrlBack.CanData[0] = CanReceived.ubData[0];	
								Tx_CtrlBack.CanData[1] = CanReceived.ubData[1];
								Tx_CtrlBack.CanData[2] = 0x00;
								Tx_CtrlBack.CanData[3] = retcode;
								Tx_CtrlBack.CanData[4] = 0x00;
								Tx_CtrlBack.CanData[5] = 0x00;
								Tx_CtrlBack.CanData[6] = 0x00;
								Tx_CtrlBack.CanData[7] = 0x00;
								TransmitHandle(&Tx_CtrlBack,SynCtrl_ExTransmitCtrl);
							}
							break;
						default:
							break;
					}
				}
			}
			if(0 != RecvFlag)		//本0.1ms周期被占用,//本次有处理事务
			{
				break;
			}
		}
		Task1ms.Status = 0x00;
	}
	return(RecvFlag);
}

//心跳、状态数据周期上传
ubyte CAN_AB_TM(void)
{
	ubyte i;
	ubyte idel = 0;
	Can_Message Tx_HB_TM = {0,1,1,1,8,0,{0,0,0,0,0,0,0,0}};	//遥测帧
	if(0xAA == TaskSHBeat.Status)	//发送心跳
	{
		Tx_HB_TM.ID = (ulong)Heartbeat | (MainNod_AB << 8) | MyNod_AB;
		Tx_HB_TM.DLC = 2;
		Tx_HB_TM.CanData[0] = HBTM_Number;
		Tx_HB_TM.CanData[1] = 0x00;
		for(i = 0; i < MAX_HBCNT; i++)
		{
			if(HB_count[i] < HB_Overflow_Time)
				Tx_HB_TM.CanData[1] |= (0x01 << i);
		}
		TransmitHandle(&Tx_HB_TM,SynCtrl_HeartBeat);
		TaskSHBeat.Status = 0x00;
		idel = 1;
	}
	if((0xAA == TaskSTM1.Status) && (0 == idel))	//发送状态1
	{
		Tx_HB_TM.ID = (ulong)Telemetry | (MainNod_AB << 8) | MyNod_AB;
		Tx_HB_TM.DLC = 6;
		Tx_HB_TM.CanData[0] = HBTM_Number;
		for(i = 0; i < MAX_HBCNT; i++)
		{
			if(HB_count[i] >= HB_Overflow_Time) 
				SelfStatus &= ~(0x01 << i);
		}
		Tx_HB_TM.CanData[1] = SelfStatus;
		Tx_HB_TM.CanData[2] = farVolt1.ch[0];
		Tx_HB_TM.CanData[3] = farVolt1.ch[1];
		Tx_HB_TM.CanData[4] = farVolt2.ch[0];
		Tx_HB_TM.CanData[5] = farVolt2.ch[1];
		TransmitHandle(&Tx_HB_TM,SynCtrl_Telemetry1);
		TaskSTM1.Status = 0;
		idel = 1;
	}
	if((0xAA == TaskSTM2.Status) && (0 == idel))		//发送状态2
	{
		Tx_HB_TM.ID = ((ulong)Telemetry | 0x1000000) | (MainNod_AB << 8) | MyNod_AB;
		Tx_HB_TM.DLC = 4;
		Tx_HB_TM.CanData[0] = HBTM_Number;
		Tx_HB_TM.CanData[1] = (ubyte)(TM2_Status & 0xFF);
		Tx_HB_TM.CanData[2] = (ubyte)((TM2_Status >> 8) & 0x03);
		Tx_HB_TM.CanData[3] = 0x00;
		TransmitHandle(&Tx_HB_TM,SynCtrl_Telemetry2);
		TaskSTM2.Status = 0;
		HBTM_Number ++;
		idel = 1;
	}
	return(idel);
}


ubyte CAN_12_TM(void)
{
	ubyte MSGcon;
	ulong subID;
	ubyte nbr_flag = 0;				//CAN1/2处理标志
	ubyte i,j,k;
	stCAN_SWObj CanReceived;
	Can_Message Tx_CtrlBack = {0,1,1,1,8,0,{0,0,0,0,0,0,0,0}};

	for(i = 0; i < 3; i++)	//接收ERTU心跳
	{
		if(0xAA == TaskRHBeat[i].Status)	//需要接收ERTU心跳信息
		{
			TaskRHBeat[i].Status = 0;
			nbr_flag = 0x00;	//未正确处理过该消息
			for(j = 0; j < 2; j++)
			{
				nbr_flag <<= 4;
				CanReceived.ubMOCfg = 2;
				MSGcon = CAN_ubReadFIFO(i + 70 + j*5, &CanReceived);	//CAN1/2接收消息处理.如果该消息被正确处理,读空消息队列
				if(1 == MSGcon)	//正确收到消息且该消息未被正确处理
				{
					nbr_flag |= 0x0A;
					subID = (ulong)(Heartbeat | 0x2000000) | (ulong)(MyNod_12 << 8) | (ulong)(i + SubNod_12_Start);
					if(CanReceived.ulID == subID)
					{
						if(CanReceived.ubData[0] != TaskRHBeat[i].No)	//消息序号不同
						{
							if((0xAA == CanReceived.ubData[1]))
							{
								TaskRHBeat[i].No = CanReceived.ubData[0];
								HB_count[i] = 0;
							}
						}
						else
						{
							nbr_flag &= 0xF0;
						}
					}
					else
					{
							nbr_flag &= 0xF0;
					}
				}
			}
			if(nbr_flag)
			{
				break;
			}
		}
	}
	if(!nbr_flag)
	{
		for(i = 0; i < MAX_HBCNT; i++)	//接收RTU状态1
		{
			if(0xAA == TaskRTM1[i].Status)	//需要接收ERTU心跳信息
			{
				TaskRTM1[i].Status = 0;
				nbr_flag = 0x00;	//未正确处理过该消息
				for(j = 0; j < 2; j++)
				{
					nbr_flag <<= 4;
					CanReceived.ubMOCfg = 6;
					MSGcon = CAN_ubReadFIFO(i + 80 + j*10, &CanReceived);	//CAN1/2接收消息处理.如果该消息被正确处理,读空消息队列
					if(1 == MSGcon)	//正确收到消息且该消息未被正确处理
					{
						nbr_flag |= 0x0A;
						subID = (ulong)(Telemetry | 0x2000000) | (ulong)(MyNod_12 << 8) | (ulong)(i + SubNod_12_Start);
						if(CanReceived.ulID == subID)
						{
							if(CanReceived.ubData[0] != TaskRTM1[i].No)	//消息序号不相同
							{
								TaskRTM1[i].No = CanReceived.ubData[0];
								HB_count[i] = 0;
								if(i < 3)
								{
									if((0 == CanReceived.ubData[1]) && (0 == CanReceived.ubData[2]) && (0 == CanReceived.ubData[3]))
									{
										SelfStatus |= (0x01 << i);
									}
									else
									{
										SelfStatus &= ~(0x01 << i);
									}
								}
								else
								{
									if(0 == CanReceived.ubData[1])
									{
										SelfStatus |= (0x01 << i);
									}
									else
									{
										SelfStatus &= ~(0x01 << i);
									}
								}
								subID &= 0x000000FF;
								Tx_CtrlBack.ID = (ulong)(Telemetry | 0x2000000) | (subID << 16) | (MainNod_AB << 8) | MyNod_AB;
								Tx_CtrlBack.DLC = 6;
								for(i = 0; i < Tx_CtrlBack.DLC; i++)
								{
									Tx_CtrlBack.CanData[i] = CanReceived.ubData[i];	
								}
								TransmitHandle(&Tx_CtrlBack,SynRTU_Telemetry1);
							}
							else
							{
								nbr_flag &= 0xF0;
							}
						}
						else
						{
							nbr_flag &= 0xF0;
						}
					}
				}
				if(nbr_flag)
				{
					break;
				}
			}
		}
	}
	if(!nbr_flag)
	{
		for(i = 0; i < 3; i++)	//接收ERTU状态2
		{
			if(0xAA == TaskRTM2[i].Status)	//需要接收ERTU状态2
			{
				TaskRTM2[i].Status = 0x00;
				nbr_flag = 0x00;	//未正确处理过该消息
				for(j = 0; j < 2; j++)
				{
					nbr_flag <<= 4;
					CanReceived.ubMOCfg = 4;
					MSGcon = CAN_ubReadFIFO(i + 86 + j*10, &CanReceived);	//CAN1/2接收消息处理.如果该消息被正确处理,读空消息队列
					if(1 == MSGcon)	//正确收到消息且该消息未被正确处理
					{
						nbr_flag |= 0x0A;
						subID = (ulong)(Telemetry | 0x3000000) | (ulong)(MyNod_12 << 8) | (ulong)(i + SubNod_12_Start);
						if(CanReceived.ulID == subID)
						{
							if(CanReceived.ubData[0] != TaskRTM2[i].No)	//消息序号不同
							{
								TaskRTM2[i].No = CanReceived.ubData[0];
								subID &= 0x000000FF;
								Tx_CtrlBack.ID = (ulong)(Telemetry | 0x3000000) | (subID << 16) | (MainNod_AB << 8) | MyNod_AB;
								Tx_CtrlBack.DLC = 6;
								for(k = 0; k < Tx_CtrlBack.DLC; k++)
								{
									Tx_CtrlBack.CanData[k] = CanReceived.ubData[k];	
								}
								TransmitHandle(&Tx_CtrlBack,SynRTU_Telemetry2);
							}
							else
							{
								nbr_flag &= 0xF0;
							}
						}
						else
						{
							nbr_flag &= 0xF0;
						}
					}
				}
				if(nbr_flag)
				{
					break;
				}
			}
		}
	}
	return(nbr_flag);
}

/***RTU自检命令和应答***/
ubyte CAN_12_SelfTest(void)
{
	ubyte MSGcon;
	ulong subID;
	ubyte idel = 0;
	ubyte i,j;
	stCAN_SWObj CanReceived;
	Can_Message Tx_SelfTest = {0,1,1,1,2,0,{0,0,0,0,0,0,0,0}};	//发送自检
	for(i = 0; i < MAX_HBCNT; i++)	//发送自检
	{
		if(0xAA == TaskSSLT[i].Status)	//需要发送自检
		{
			CanReceived.ubMOCfg = 8;
			(void)CAN_ubReadFIFO(i + 50, &CanReceived);	//CAN1/2接收消息处理.如果该消息被正确处理,读空消息队列
			CanReceived.ubMOCfg = 8;
			(void)CAN_ubReadFIFO(i + 60, &CanReceived);	//CAN1/2接收消息处理.如果该消息被正确处理,读空消息队列
			TaskSSLT[i].Status = 0;
			Tx_SelfTest.ID = (ulong)SelfTest | (ulong)((i + SubNod_12_Start) << 8) | (ulong)MyNod_12;
			Tx_SelfTest.CanData[0] = TaskRSLT[i].No;
			Tx_SelfTest.CanData[1] = 0x12;
			TransmitHandle(&Tx_SelfTest,SynCtrl_SelfTest);
			TaskRSLT[i].Status = 0x55;
			TaskRSLT[i].TimeCount = SelfTestDelay;
			idel = 1;
			break;
		}
	}
	if(!idel)
	{
		for(i = 0; i < MAX_HBCNT; i++)	//接收RTU自检应答
		{
			if(0xAA == TaskRSLT[i].Status)	//需要接收RTU自检应答
			{
				SelfStatus &= ~(0x01 << i);
				idel = 0;
				for(j = 0; j < 2; j++)
				{
					CanReceived.ubMOCfg = 2;
					MSGcon = CAN_ubReadFIFO(i + 50 + j*10, &CanReceived);	//CAN1/2接收消息处理.如果该消息被正确处理,读空消息队列
					if((1 == MSGcon) && (0 == idel))	//正确收到消息
					{
						subID = (ulong)SelfTest | (ulong)(MyNod_12 << 8) | (ulong)(i + SubNod_12_Start);
						if(CanReceived.ulID == subID)
						{
							if(CanReceived.ubData[0] == TaskRSLT[i].No)	//消息序号相同
							{
								TaskRSLT[i].No ++;
								if(0xAA == CanReceived.ubData[1])
								{
									SelfStatus |= (0x01 << i);
								}
								idel = 1;
							}
						}
					}
				}
			}
			TaskRSLT[i].Status = 0;
			if(idel)
			{
				break;
			}
		}
	}
	return(idel);
}

/*******************参数配置查询指令处理*********************/
void CMD_ArgSetCheck_Ctrl(stCAN_SWObj *ExtObj)
{
	ulong SA = 0, PS = 0;
	ubyte RtuState;
	ubyte i,No;
	ubyte HH,MM,SS;
	uword MS;
	INTtoUINT KK,BB,KB;
	slong TK,TB;
	Can_Message Tx_CtrlBack = {0,1,1,1,8,0,{0,0,0,0,0,0,0,0}};	//控制回令
	Tx_CtrlBack.ID = (ulong)Arg_Set_Check | (MainNod_AB << 8) | MyNod_AB;						
	Tx_CtrlBack.CanData[0] = ExtObj->ubData[0];	
	Tx_CtrlBack.CanData[1] = ExtObj->ubData[1];
	Tx_CtrlBack.CanData[2] = ExtObj->ubData[2];
	Tx_CtrlBack.CanData[3] = 0xAA;	//命令成功执行;
	switch(ExtObj->ubData[1])
	{
		case 0x00:	//无动作
			break;
		case 0x12:	//启动自检
			for(i = 0; i < 3; i++)	//启动自检
			{
				RtuState = (Gpio_on_off >> (i + 4)) & 0x01;	//ERTU开机?
				if(0x01 == RtuState)
				{
					TaskSSLT[i].TimeCount = 10*i + 3;	//0.3ms后在不同的定时周期（每个间隔1ms），测控分别向每个RTU发送自检指令
					TaskSSLT[i].Status = 0x55;
				}
				else
				{
					Tx_CtrlBack.CanData[3] = 0x55;	//ERTU未开机
				}
			}
			for(i = 3; i < 6; i++)	//启动自检
			{
				TaskSSLT[i].TimeCount = 10*i + 3;	//0.3ms后在不同的定时周期（每个间隔1ms），测控分别向每个RTU发送自检指令
				TaskSSLT[i].Status = 0x55;
			}
			Tx_CtrlBack.CanData[2] = (~(Gpio_on_off >> 4)) & 0x07;
			break;
		case 0x13:	//取自检结果
			Tx_CtrlBack.CanData[2] = SelfStatus;
			if(0x3F == SelfStatus)
			{
				Tx_CtrlBack.CanData[3] = 0xAA;
			}
			else
			{
				Tx_CtrlBack.CanData[3] = 0x55;
			}
			break;
		case 0x21:	//获取采集值
			No = ExtObj->ubData[2] - 1;
			if(No < ADC_TOTAL)
			{
				if(1 == ADC_Ptr[No].state)
				{
					KB.i = ADC_Ptr[No].PH_Val;
					Tx_CtrlBack.CanData[4] = KB.ch[0];
					Tx_CtrlBack.CanData[5] = KB.ch[1];
					if(0xAA !=  ADC_Ptr[No].Status)
					{
						Tx_CtrlBack.CanData[3] = 0xCC;	//未标定
					}
				}
				else
				{
					Tx_CtrlBack.CanData[3] = 0xBB;	//未使能
				}
			}
			else
			{
				Tx_CtrlBack.CanData[3] = 0x55;	//通道错误
			}
			break;
		case 0x22:	//累积工作时间查询
			MS = (uword)(timingCnt % 1000);
			SS = (ubyte)((timingCnt / 1000) % 60);
			MM = (ubyte)((timingCnt / 60000) % 60);
			HH = (ubyte)((timingCnt / 3600000) % 24);
			Tx_CtrlBack.CanData[2] = HH;
			Tx_CtrlBack.CanData[4] = MM;
			Tx_CtrlBack.CanData[5] = SS;
			Tx_CtrlBack.CanData[6] = (ubyte)(MS & 0xFF);	
			Tx_CtrlBack.CanData[7] = (ubyte)((MS >> 8) & 0xFF);	
			break;
		case 0x44:	//通道标定系数查询
			No = ExtObj->ubData[2] -1;
			if(No < ADC_TOTAL)
			{
				if(1 == ADC_Ptr[No].state)
				{
					if(0xAA == ADC_Ptr[No].Status)
					{
						Tx_CtrlBack.CanData[2] = (ExtObj->ubData[2] & 0x0F) | ((ADC_Ptr[No].para_mode << 4) & 0xF0);
						KK.i = ADC_Ptr[No].K;
						BB.i = ADC_Ptr[No].B;
						Tx_CtrlBack.CanData[4] = KK.ch[0];
						Tx_CtrlBack.CanData[5] = KK.ch[1];
						Tx_CtrlBack.CanData[6] = BB.ch[0];
						Tx_CtrlBack.CanData[7] = BB.ch[1];
					}
					else
					{
						Tx_CtrlBack.CanData[3] = 0xCC;	//未标定
					}
				}
				else
				{
					Tx_CtrlBack.CanData[3] = 0xBB;	//未使能
				}
			}
			else
			{
				Tx_CtrlBack.CanData[3] = 0x55;	//通道错误
			}
			break;
		case 0x80:	//恢复出厂设置
					if( ExtObj->ubData[2] == 0xAA)	//B2内容正确
					{
						if(Store_Para_Init())
						{
							Tx_CtrlBack.CanData[3] = 0xDD;	//存储失败
						}
					}
					else
					{
						Tx_CtrlBack.CanData[3] =  0x55;//B2内容错误	
					}
			break;
		case 0x8A:	//配置全局网主控CANA/B节点/测控CANA/B节点
			SA = (ulong)ExtObj->ubData[4] & 0xFF;	//主控CANA/B节点
			PS = (ulong)ExtObj->ubData[5] & 0xFF;	//测控CANA/B节点
			Tx_CtrlBack.CanData[2] = 0x00;	
			Tx_CtrlBack.CanData[4] = ExtObj->ubData[4];	
			Tx_CtrlBack.CanData[5] = ExtObj->ubData[5];
			if(SA == PS)
			{
				Tx_CtrlBack.CanData[3] = 0x55;//节点相同
			}
			break;
		case 0x8B:	//使能采集
			No = ExtObj->ubData[2] -1;
			if((1 < No) && (ADC_TOTAL > No))
			{
				if(1 == ADC_Ptr[No].state)
				{
					Tx_CtrlBack.CanData[3] = 0xBB;	//已经被使能
				}
				else
				{
					KK.ch[0] =  ExtObj->ubData[4];
					KK.ch[1] =  ExtObj->ubData[5];
					BB.ch[0] =  ExtObj->ubData[6];
					BB.ch[1] =  ExtObj->ubData[7];
					if(20000 < KK.i)
					{
						KK.i = 20000;
					}
					else if(-20000 > KK.i)
					{
						KK.i = -20000;
					}
					else
					{
						
					}
					if(20000 < BB.i)
					{
						BB.i = 20000;
					}
					else if(-20000 > BB.i)
					{
						BB.i = -20000;
					}
					else
					{
						
					}
					ADC_Ptr[No].K = KK.i;
					ADC_Ptr[No].K1 = KK.i;
					ADC_Ptr[No].K2 = KK.i;
					ADC_Ptr[No].B = BB.i;
					ADC_Ptr[No].B1 = BB.i;
					ADC_Ptr[No].B2 = BB.i;
					ADC_Ptr[No].sn = No;
					ADC_Ptr[No].state = 1;
					ADC_Ptr[No].para_mode = ExtObj->ubData[3];
					ADC_Ptr[No].Status = 0x55;
					ADC_Ptr[No].store_addr = ADC_Start_Addr + ADC_Length * No;
					ADC_Ptr[No].store_addr1 = ADC_Start_Addr + ADC_Length * No;
					ADC_Ptr[No].store_addr2 = ADC_Start_Addr + ADC_Length * No;
					ADC_Ptr[No].Max_Val = 400;
					ADC_Ptr[No].Min_Val = 0;
					switch(No)
					{
						case 2:
							P15_Mask |= 0x10;
							break;
						case 3:
							P15_Mask |= 0x20;
							break;
						case 4:
							P15_Mask |= 0x40;
							break;
						case 5:
							P5_Mask |= 0x01;
							break;
						case 6:
							P5_Mask |= 0x04;
							break;
						case 7:
							P5_Mask |= 0x08;
							break;
						case 8:
							P5_Mask |= 0x10;
							break;
						case 9:
							P5_Mask |= 0x20;
							break;
						default:
							break;
					}
					if(FRAM_Write((uword)(ADC_Start_Addr + ADC_Length * No),(ubyte *) &ADC_Ptr[No],(ubyte)sizeof(ADC_Lib)))
					{
						Tx_CtrlBack.CanData[3] = 0xDD;	//存储失败
					}
				}
			}
			else
			{
				Tx_CtrlBack.CanData[3] = 0x55;	//通道错误
			}
			break;
		case 0x8C:	//关闭采集
			No = ExtObj->ubData[2] - 1;
			if((1 < No) && (ADC_TOTAL > No))
			{
				ADC_Ptr[No].state = 0;
				switch(No)
				{
					case 2:
						P15_Mask &= 0xEF;
						break;
					case 3:
						P15_Mask &= 0xDF;
						break;
					case 4:
						P15_Mask &= 0xBF;
						break;
					case 5:
						P5_Mask &= 0xFE;
						break;
					case 6:
						P5_Mask &= 0xFB;
						break;
					case 7:
						P5_Mask &= 0xF7;
						break;
					case 8:
						P5_Mask &= 0xEF;
						break;
					case 9:
						P5_Mask &= 0xDF;
						break;
					default:
						break;
				}
				if(FRAM_Write((uword)(ADC_Start_Addr + ADC_Length * No),(ubyte *) &ADC_Ptr[No],(ubyte)sizeof(ADC_Lib)))
				{
					Tx_CtrlBack.CanData[3] = 0xDD;	//存储失败
				}
			}
			else
			{
				Tx_CtrlBack.CanData[3] = 0x55;	//通道错误
			}
			break;
		case 0x8D:	//系数在线标定
			No = ExtObj->ubData[2] - 1;
			if(No < ADC_TOTAL)
			{
				if(1 == ADC_Ptr[No].state)
				{
					KK.ch[0] =  ExtObj->ubData[4];
					KK.ch[1] =  ExtObj->ubData[5];
					BB.ch[0] =  ExtObj->ubData[6];
					BB.ch[1] =  ExtObj->ubData[7];
					TB = (slong)ADC_Ptr[No].B;
					TB = TB * KK.i + BB.i;
					TK = (slong)ADC_Ptr[No].K;
					TK = TK * KK.i;


					if(20000 < TK)
					{
						KK.i = 20000;
					}
					else if(-20000 > TK)
					{
						KK.i = -20000;
					}
					else
					{
						KK.i = (sword)TK;
					}
					if(20000 < TB)
					{
						BB.i = 20000;
					}
					else if(-20000 > TB)
					{
						BB.i = -20000;
					}
					else
					{
						BB.i = (sword)TB;
					}
					ADC_Ptr[No].K = KK.i;
					ADC_Ptr[No].B = BB.i;
					ADC_Ptr[No].K1 = KK.i;
					ADC_Ptr[No].K2 = KK.i;
					ADC_Ptr[No].B1 = BB.i;
					ADC_Ptr[No].B2 = BB.i;
					ADC_Ptr[No].Status = 0xAA;
					if(FRAM_Write((uword)(ADC_Start_Addr + ADC_Length * No),(ubyte *) &ADC_Ptr[No],(ubyte)sizeof(ADC_Lib)))
					{
						Tx_CtrlBack.CanData[3] = 0xDD;	//存储失败
					}
				}
				else
				{
					Tx_CtrlBack.CanData[3] = 0xBB;	//未使能
				}
			}
			else
			{
				Tx_CtrlBack.CanData[3] = 0x55;	//通道错误
			}
			break;
		default:
			Tx_CtrlBack.CanData[3] = 0xFF;	//命令错误;
			break;
	}
	TransmitHandle(&Tx_CtrlBack,SynCtrl_ArgSCCtrl);
	if(SA != PS)	//静默,切换CANA/B节点,状态清0
	{
		ChangeNod.TimeCount = SilentTime;
		ChangeNod.Status = 0x55;		
		while(0x55 == ChangeNod.Status)
		{
			NOP();
		}
		MainNod_AB = PS;
		MyNod_AB = SA;
		CAN_vInit();
		ChangeNod.Status = 0x00;
		Task1ms.Status = 0x00;
		TaskSHBeat.Status = 0x00;
		TaskSTM1.Status = 0x00;
		TaskSTM2.Status = 0x00;

		for(i = 0; i < MAX_HBCNT; i++)
		{
			Task15ms[i].Status = 0x00;
			TaskSSLT[i].Status = 0x00;
			TaskRSLT[i].Status = 0x00;
			TaskRTM1[i].Status = 0x00;
		}
		for(i = 0; i < 3; i++)
		{
			TaskRHBeat[i].Status = 0x00;
			TaskRTM2[i].Status = 0x00;
		}
		TaskAD.Status = 0x00;
		TaskIO.Status = 0x00;
		Task1s.Status = 0x00;
	}
}
ubyte CmdTransmit(stCAN_SWObj *ExtObj)
{
	ulong substation;		//RTU节点
	ubyte retcode = 0xAA;
	ubyte RtuState;
	ubyte i;
	stCAN_SWObj CanReceived;
	Can_Message Tx_CtrlBack = {0,1,1,1,8,0,{0,0,0,0,0,0,0,0}};	//控制回令
	substation = (ulong) (ExtObj->ulID >> 16) & 0xFF;
	switch(substation)
	{
		case 0:		//ERTU处理相同
		case 1:               
		case 2:
			switch(ExtObj->ubData[1])	//只转发无动作和调压指令,无动作和调压指令处理相同
			{
				case 0x00:	//无动作
				case 0xD1:	//控制指令
					RtuState = (Gpio_on_off >> (substation + 4)) & 0x01;	//ERTU开机?
					if(0x01 == RtuState)
					{
						Tx_CtrlBack.ID = (ulong)Ex_PRO_Ctrl | ((substation + SubNod_12_Start) << 8) | (ulong)MyNod_12;
					}
					else
					{
						retcode = 0x55;	//相应ERTU未开机
					}
					break;
				default:	//不能识别指令
					retcode = 0xFF;
					break;
			}
			break;
		case 3:		//MRTU处理相同
		case 4:
		case 5:
			switch(ExtObj->ubData[1])	//只转发无动作和配置产品代号、配置产品名称，无动作和配置产品代号、配置产品名称的处理相同
			{
				case 0x00:	//无动作
				case 0x94:	//配置产品代号
				case 0x95:	//配置产品名称
					Tx_CtrlBack.ID = (ulong)Ex_Arg_Set | ((substation + SubNod_12_Start) << 8) | (ulong)MyNod_12;
					for(i = 0; i < 8; i++)
					{
						Tx_CtrlBack.CanData[i] = ExtObj->ubData[i];	
					}
					break;
				default:	//不能识别指令
					retcode = 0xFF;
					break;
			}

			break;
		default:
			retcode = 0xDD;
			break;
	}
	if(0xAA == retcode)
	{
		for(i = 0; i < 8; i++)
		{
			Tx_CtrlBack.CanData[i] = ExtObj->ubData[i];	
		}
		CanReceived.ubMOCfg = 8;
		(void)CAN_ubReadFIFO((ubyte)(30 + substation), &CanReceived);	//清空CAN1/2相应消息接收缓存
		CanReceived.ubMOCfg = 8;
		(void)CAN_ubReadFIFO((ubyte)(40 + substation), &CanReceived);
		TransmitHandle(&Tx_CtrlBack,SynCtrl_ExTransmitsub);
		Task15ms[substation].TimeCount = Task15msDelay;
		Task15ms[substation].Status = 0x55;
		Ctrl_AnswerNo[substation] = ExtObj->ubData[0];
	}
	return(retcode);
}
//////////////////////////////////////////////////////
//*************CAN1/2 转发指令应答	****************//
//////////////////////////////////////////////////////
ubyte CAN_12_AnsCmd(void)
{
	ubyte MSGcon;
	ulong subID;
	ubyte nbr_flag;				//CAN1/2处理标志
	ubyte i,j,k;
	stCAN_SWObj CanReceived;
	Can_Message Tx_CtrlBack = {0,1,1,1,8,0,{0,0,0,0,0,0,0,0}};	//控制回令
	ubyte idel = 0;
	for(i = 0; i < 6; i++)	//接收处理6个RTU转发指令应答
	{
		if(0xAA == Task15ms[i].Status)	//需要接收到时转发消息应答
		{
			nbr_flag = 0x55;	//未正确处理过该消息
			for(j = 0; j < 2; j++)
			{
				subID = 0;
				CanReceived.ubMOCfg = 8;
				CanReceived.ulID = 0xFFFFFFFF;
				MSGcon = CAN_ubReadFIFO(i + 30 + j*10, &CanReceived);	//CAN1/2接收指定长度的消息.i + 30 + j*10:30/40...35/45
				if((1 == MSGcon) && (0x55 == nbr_flag))	//正确收到消息且该消息未被正确处理
				{
					switch(i)
					{
						case 0:		//ERTU处理相同(0/1/2)
						case 1:
						case 2:
							switch(CanReceived.ubData[1])	//只转发无动作和调压指令，两个指令处理相同
							{
								case 0x00:	//无动作
								case 0xD1:	//控制指令
									subID = (ulong)Ex_PRO_Ctrl | (ulong)(MyNod_12 << 8) | (ulong)(i + SubNod_12_Start);
									break;
							}
							break;
						case 3:		//MRTU处理相同(3/4/5)
						case 4:
						case 5:
							switch(CanReceived.ubData[1])	//只转发无动作和配置产品代号、配置产品名称，3个指令处理相同
							{
								case 0x00:	//无动作
								case 0x94:	//配置产品代号
								case 0x95:	//配置产品名称
									subID = (ulong)Ex_Arg_Set | (ulong)(MyNod_12 << 8) | (ulong)(i + SubNod_12_Start);
									break;
							}
							break;
					
					}
					if(CanReceived.ulID == subID)
					{
						if(CanReceived.ubData[0] == Ctrl_AnswerNo[i])	//消息序号相同
						{
							subID &= 0x000000FF;
							Tx_CtrlBack.ID = (ulong)ExTransmit | (subID << 16) | (MainNod_AB << 8) | MyNod_AB;
							for(k = 0; k < 8; k++)
							{
								Tx_CtrlBack.CanData[k] = CanReceived.ubData[k];	
							}
							TransmitHandle(&Tx_CtrlBack,SynCtrl_ExTransmitCtrl);
							nbr_flag = 0xAA;	//该消息被正确处理
						}
					}

				}
			}
			Task15ms[i].Status = 0;
			if( 0xAA == nbr_flag)
			{
				idel = 1;
				break;
			}
		}
	}
	return(idel);
}

 // ubMOCfg: this byte contains 
 //         7     6      5     4     3     2     1     0
 //      |-----------------------------------------------|
 //      | 0   | MIDE | IDE | DIR |          DLC         |
 //      |-----------------------------------------------|
 //on sending,only use DLC.
void TransmitHandle(Can_Message *TransMessage, CanSentDest Dest)
{
	stCAN_SWObj Transmiting;
	ubyte i;
	ubyte substation;
	ubyte ubObjNr1,ubObjNr2;
	ubyte SendFlag = 0x55;
	Transmiting.ulID = TransMessage->ID;
	Transmiting.ubMOCfg = ((TransMessage->MIDE & 0x01) << 6) | ((TransMessage->IDE & 0x01) << 5) | ((TransMessage->DIR & 0x01) << 4) | (TransMessage->DLC & 0x0F);
	for(i =0; i < TransMessage->DLC; i++)
	{
		Transmiting.ubData[i] = TransMessage -> CanData[i];
	}
	switch(Dest)
	{
		case SynCtrl_Uergent:	//紧急关断应答	
			ubObjNr1 = 130;
			ubObjNr2 = 140;
			break;
		case SynCtrl_PDCtrl:	//开关指令应答	
			ubObjNr1 = 131;
			ubObjNr2 = 141;
			break;
		case SynCtrl_ArgSCCtrl:	//查询配置指令应答
			ubObjNr1 = 132;
			ubObjNr2 = 142;
			break;
		case SynCtrl_ExTransmitCtrl:	//转发指令应答
			ubObjNr1 = 133;
			ubObjNr2 = 143;
			break;
		case SynCtrl_HeartBeat:		//心跳
			ubObjNr1 = 134;
			ubObjNr2 = 144;
			break;
		case SynCtrl_Telemetry1:	//测控状态1
			ubObjNr1 = 135;
			ubObjNr2 = 145;
			break;
		case SynCtrl_Telemetry2:	//测控状态2
			ubObjNr1 = 136;
			ubObjNr2 = 146;
			break;
//		case SynRTU_HeartBeat:		//ERTU心跳,不转发
//			ubObjNr1 = 137;
//			ubObjNr2 = 147;
//			break;
		case SynRTU_Telemetry1:		//RTU测控状态1
			ubObjNr1 = 138;
			ubObjNr2 = 148;
			break;
		case SynRTU_Telemetry2:		//ERTU测控状态2
			ubObjNr1 = 139;
			ubObjNr2 = 149;
			break;
		case SynCtrl_ExTransmitsub:	//转发指令
			substation = (ubyte)(((TransMessage->ID >> 8) & 0xFF) - SubNod_12_Start);
			ubObjNr1 = 150 + substation;
			ubObjNr2 = 160 + substation;
			break;
		case SynCtrl_SelfTest:		//自检
			substation = (ubyte)(((TransMessage->ID >> 8) & 0xFF) - SubNod_12_Start);
			ubObjNr1 = 170 + substation;
			ubObjNr2 = 180 + substation;
			break;			
		default:
			SendFlag = 0xAA;
			break;

	}
	//发送数据帧设置
	if(0x55 == SendFlag)
	{
		CAN_ubWriteFIFO(ubObjNr1, &Transmiting);//向Can1或CanA发送信息
		CAN_ubWriteFIFO(ubObjNr2, &Transmiting);//向Can2或CanB发送信息
	}
}

sbyte Read_ADC_Head(void)
{
	uword RAD_Head[3] = {0x00,0x00,0x00};
	uword AD_Head_AND,AD_Head_XOR,AD_Head;
	sbyte retcode;
	(void)FRAM_Read((uword)ADC_Head_Addr,(ubyte *) RAD_Head,6);
	AD_Head_AND = RAD_Head[0] & RAD_Head[1];		//取0、1相同位
	AD_Head_XOR = (RAD_Head[0] ^ RAD_Head[1]) & RAD_Head[2];		//0、1不同位取2相应位
	AD_Head = AD_Head_AND | AD_Head_XOR;	//合并为位三取二
	if(AD_Head == 0xEB90)
	{
		retcode = -1;
	}
	else
	{
		retcode = 0;
	}
	return(retcode);
}
void Write_ADC_Head(void)
{
	uword AD_Head[3] = {0xEB90,0xEB90,0xEB90};
	(void)FRAM_Write((uword)ADC_Head_Addr,(ubyte *) AD_Head,6);
}
void Write_ADC_BHead(void)
{
	uword AD_BHead[3] = {0xAAAA,0xAA55,0x5555};
	(void)FRAM_Write((uword)ADC_Head_Addr,(ubyte *) AD_BHead,6);
}

////////////////////////////////////////////////
////////*******AD参数出厂设置**********/////////
////////////////////////////////////////////////
ubyte Store_Para_Init(void)
{
	ubyte i,j;
	ubyte ret_val	= 0;

	P15_Mask = 0x05;
	P5_Mask = 0;
		
	for(i = 0; i < ADC_TOTAL; i++)
	{
		ADC_Ptr[i].sn = i;
		ADC_Ptr[i].store_addr = ADC_Start_Addr + ADC_Length * i;
		ADC_Ptr[i].store_addr1 = ADC_Start_Addr + ADC_Length * i;
		ADC_Ptr[i].store_addr2 = ADC_Start_Addr + ADC_Length * i;
		ADC_Ptr[i].Max_Val = 400;
		ADC_Ptr[i].Min_Val = 0;
		ADC_Ptr[i].K = 1000;
		ADC_Ptr[i].B = 0;
		ADC_Ptr[i].K1 = 1000;
		ADC_Ptr[i].B1 = 0;
		ADC_Ptr[i].K2 = 1000;
		ADC_Ptr[i].B2 = 0;
		ADC_Ptr[i].Status = 0x55;
		
		switch(i)
		{
			case 0:/*电源1远端电压*/
				ADC_Ptr[i].state = 1;
				ADC_Ptr[i].para_mode = 0;
			break;
			case 1:/*电源2远端电压*/
				ADC_Ptr[i].state = 1;
				ADC_Ptr[i].para_mode = 0;
			break;
			default:/*备用*/
				ADC_Ptr[i].state = 0;
				ADC_Ptr[i].para_mode = 3;
			break;	
		}			
		for(j = 0; j < MAX_READ_CNT; j++)
		{
			ADC_Ptr[i].ReadV[j] = 0;
		}
		ADC_Ptr[i].FilterV = 0;
		ADC_Ptr[i].PH_Val = 0;
	}
	for(i = 0; i < ADC_TOTAL; i++)
	{
		ret_val = FRAM_Write((uword)(ADC_Start_Addr + ADC_Length * i),(ubyte *) &ADC_Ptr[i],(ubyte)sizeof(ADC_Lib));		////写入ADC铁电存储参数
		if(ret_val)
		{
			break;
		}
	}
	if (ADC_TOTAL == i)
	{
		Write_ADC_Head();
		ret_val = 0;
	}
	else
	{
		Write_ADC_BHead();
		ret_val = 1;
	}
	return(ret_val);
}
////////////////////////////////////////////////
////////*******从铁电中读取AD参数******/////////
////////////////////////////////////////////////
void ReStore_Para_Init(void)
{
	ubyte i,j;
	P15_Mask = 0x05;
	P5_Mask = 0;

	/*铁电参数读取*/
	if (Read_ADC_Head())
	{
		for(i = 0; i < ADC_TOTAL; i++)/*读取10路AD参数*/
		{
			(void)FRAM_Read((uword)(ADC_Start_Addr + ADC_Length * i),(ubyte *)&ADC_Ptr[i],(ubyte)sizeof(ADC_Lib));	//读取ADC铁电存储参数
			if(ADC_Ptr[i].K == ADC_Ptr[i].K1)
			{
				ADC_Ptr[i].K2 = ADC_Ptr[i].K;
			}
			else if(ADC_Ptr[i].K == ADC_Ptr[i].K2)
			{
				ADC_Ptr[i].K1 = ADC_Ptr[i].K;
			}
			else if(ADC_Ptr[i].K1 == ADC_Ptr[i].K2)
			{
				ADC_Ptr[i].K = ADC_Ptr[i].K1;
			}
			else
			{
				ADC_Ptr[i].K = 1000;
				ADC_Ptr[i].K1 = 1000;
				ADC_Ptr[i].K2 = 1000;
			}

			if(ADC_Ptr[i].B == ADC_Ptr[i].B1)
			{
				ADC_Ptr[i].B2 = ADC_Ptr[i].B;
			}
			else if(ADC_Ptr[i].B == ADC_Ptr[i].B2)
			{
				ADC_Ptr[i].B1 = ADC_Ptr[i].B;
			}
			else if(ADC_Ptr[i].B1 == ADC_Ptr[i].B2)
			{
				ADC_Ptr[i].B = ADC_Ptr[i].B1;
			}
			else
			{
				ADC_Ptr[i].B = 0;
				ADC_Ptr[i].B1 = 0;
				ADC_Ptr[i].B2 = 0;
			}

			if(ADC_Ptr[i].store_addr == ADC_Ptr[i].store_addr1)
			{
				ADC_Ptr[i].store_addr2 = ADC_Ptr[i].store_addr;
			}
			else if(ADC_Ptr[i].store_addr == ADC_Ptr[i].store_addr2)
			{
				ADC_Ptr[i].store_addr1 = ADC_Ptr[i].store_addr;
			}
			else if(ADC_Ptr[i].store_addr1 == ADC_Ptr[i].store_addr2)
			{
				ADC_Ptr[i].store_addr = ADC_Ptr[i].store_addr1;
			}
			else
			{
				ADC_Ptr[i].store_addr = ADC_Start_Addr + ADC_Length * i;
				ADC_Ptr[i].store_addr1 = ADC_Ptr[i].store_addr;
				ADC_Ptr[i].store_addr2 = ADC_Ptr[i].store_addr;
			}
			for(j = 0; j < MAX_READ_CNT; j++)
			{
				ADC_Ptr[i].ReadV[j] = 0;
			}
			ADC_Ptr[i].FilterV = 0;
			ADC_Ptr[i].PH_Val = 0;
/******************电压通道对应表*******************
****	序号	模拟通道	AD通道		输入口	****
****	 1		 电压1		ADC1.0		P15.0	****
****	 2		 电压2		ADC1.2		P15.2	****
****	 3		 电压3		ADC1.4		P15.4	****
****	 4		 电压4		ADC1.5		P15.5	****
****	 5		 电压5		ADC1.6		P15.6	****
****	 6		 电压6		ADC0.0		P5.0	****
****	 7		 电压7		ADC0.2		P5.2	****
****	 8		 电压8		ADC0.3		P5.3	****
****	 9		 电压9		ADC0.4		P5.4	****
****	 10		 电压10		ADC0.5		P5.5	****
**********************END**************************/

			if(1 == ADC_Ptr[i].state)	//使能AD通道
			{
				switch(i)
				{
					case 2:
						P15_Mask |= 0x10;
						break;
					case 3:
						P15_Mask |= 0x20;
						break;
					case 4:
						P15_Mask |= 0x40;
						break;
					case 5:
						P5_Mask |= 0x01;
						break;
					case 6:
						P5_Mask |= 0x04;
						break;
					case 7:
						P5_Mask |= 0x08;
						break;
					case 8:
						P5_Mask |= 0x10;
						break;
					case 9:
						P5_Mask |= 0x20;
						break;
					default:
						break;
				}
			}
		}
	}
	else
	{
		(void)Store_Para_Init();
	}
	for(i = 0; i < IO_TOTAL; i++)/*读取10路IO输入*/
	{
		PORTIN_Ptr[i].state = 1;
		PORTIN_Ptr[i].delay_cnt = 20;
		PORTIN_Ptr[i].Port_In_State = 0;
		PORTIN_Ptr[i].Port_In_cnt = 0;
		PORTIN_Ptr[i].Final_State = 0;
	}
	farVolt1.i = 0;
	farVolt2.i = 0;
}

////////////////////////////////////////////////
////////******获取指定设备当前状态*****/////////
////////////////////////////////////////////////

ubyte Get_Stat(ubyte ch)
{
	ubyte stat = 0;
	switch(ch)
	{
		case 0:
			stat = (ubyte)(IO_ubReadPin(IO_P0_4) & 0x1);
			break;
		case 1:
			stat = (ubyte)(IO_ubReadPin(IO_P0_5) & 0x1);
			break;
		case 2:
			stat = (ubyte)(IO_ubReadPin(IO_P0_6) & 0x1);
			break;
		case 3:
			stat = (ubyte)(IO_ubReadPin(IO_P0_7) & 0x1);
			break;
		case 4:
			stat = (ubyte)(IO_ubReadPin(IO_P10_4) & 0x1);
			break;
		case 5:
			stat = (ubyte)( IO_ubReadPin(IO_P10_5) & 0x1);
			break;
		case 6:
			stat = (ubyte)(IO_ubReadPin(IO_P10_6) & 0x1);
			break;
		case 7:
			stat = (ubyte)(IO_ubReadPin(IO_P10_7) & 0x1);
			break;
		case 8:
			stat = (ubyte)(IO_ubReadPin(IO_P10_8) & 0x1);
			break;
		case 9:
			stat = (ubyte)(IO_ubReadPin(IO_P10_9) & 0x1);
			break;
		default:
			break;	
	}

	return stat;
}
////////////////////////////////////////////////
///////****获取所有设备当前稳定状态****/////////
////////////////////////////////////////////////

ubyte Get_IOstate(void)
{
	ubyte i;
	ubyte idel = 0;
	if(0xAA == TaskIO.Status)
	{
		for(i = 0, TM2_Status = 0; i < IO_TOTAL; i++)
		{
			TM2_Status = (TM2_Status >> 1);
			if(1 ==PORTIN_Ptr[i].state)
			{
				PORTIN_Ptr[i].Port_In_State = Get_Stat(i);
				if(1 == PORTIN_Ptr[i].Port_In_State)
				{
					PORTIN_Ptr[i].Port_In_cnt ++;	
				}
				else if(PORTIN_Ptr[i].Port_In_cnt > 0)
				{
					PORTIN_Ptr[i].Port_In_cnt --;
				}
				if(PORTIN_Ptr[i].Port_In_cnt >= PORTIN_Ptr[i].delay_cnt)
				{
					PORTIN_Ptr[i].Port_In_cnt =  PORTIN_Ptr[i].delay_cnt;
					PORTIN_Ptr[i].Final_State = 1;	
				}
				else if(0 == PORTIN_Ptr[i].Port_In_cnt)
				{
					PORTIN_Ptr[i].Final_State = 0;	
				}
				if(1 == PORTIN_Ptr[i].Final_State)
				{
					TM2_Status |= 0x8000;
				}
			}
		}
		TM2_Status >>= (16 - IO_TOTAL);
		idel = 0x01;
		TaskIO.Status = 0x00;
	}
	else
	{
		idel = 0x00;
	}
	return(idel);
}

////////////////////////////////////////////////
////////*************AD****************/////////
////////////////////////////////////////////////
void Adc_Read(ubyte cnt)
{	
	if(MAX_READ_CNT > cnt)
	{
		ADC1_VFR = 0x0001;	//清除ADC1结果寄存器标志位02456
		ADC1_VFR = 0x0004;
		ADC1_VFR = 0x0010;
		ADC1_VFR = 0x0020;
		ADC1_VFR = 0x0040;
		ADC1_CRCR1 = P15_Mask;	//定义ADC1转换通道为P15
		ADC1_CRMR1 |= 0x0200;	//ADC1转换

		ADC0_VFR = 0x0001;	//清除ADC0结果寄存器标志位02345
		ADC0_VFR = 0x0004;
		ADC0_VFR = 0x0008;
		ADC0_VFR = 0x0010;
		ADC0_VFR = 0x0020;
		ADC0_CRCR1 = P5_Mask;	//定义ADC0转换通道为P5
		ADC0_CRMR1 |= 0x0200;	//ADC0转换
		
		while((ADC1_VFR & P15_Mask) != P15_Mask)	//等待直到ADC1转换完成
		{
			NOP();
		}
		while((ADC0_VFR & P5_Mask) != P5_Mask)	//等待直到ADC0转换完成
		{
			NOP();
		}
		//读取转换结果
		for (i_ch = 0; i_ch < ADC_TOTAL; i_ch ++)
		{
			if(ADC_Ptr[i_ch].state == 1)
			{
				if(((uword volatile) *ADC_RCR[i_ch]) & 0x1000)
				{
					ADC_Ptr[i_ch].ReadV[cnt] = (((uword volatile) *ADC_RESR[i_ch]) & 0x0FFC) >> 2;	//bit11~bit2有效
				}
			}
		}
	}
}
void ADC_Filter(void)
{
	ubyte i, j;
	uword  Max_Value, Min_Value;

	for(i = 0; i <ADC_TOTAL; i ++)
	{
		if(1 == ADC_Ptr[i].state)
		{
			Max_Value = ADC_Ptr[i].ReadV[0];
			Min_Value = ADC_Ptr[i].ReadV[0];
			ADC_Ptr[i].FilterV = 0;
			for(j = 0; j < MAX_READ_CNT; j++)
			{
				ADC_Ptr[i].FilterV += ADC_Ptr[i].ReadV[j];	
				if( ADC_Ptr[i].ReadV[j] > Max_Value)
				{
					Max_Value = ADC_Ptr[i].ReadV[j];
				}
				if( ADC_Ptr[i].ReadV[j] < Min_Value)
				{
					Min_Value = ADC_Ptr[i].ReadV[j];
				}
			}
			ADC_Ptr[i].FilterV = ADC_Ptr[i].FilterV - Max_Value - Min_Value;
		}		
	}
}
void Get_AD_Value(ubyte No)
{
	float ret, mid;
	sword temp = 0;

	if(ADC_TOTAL > No)
	{
		if(1 == ADC_Ptr[No].state)
		{
			switch(ADC_Ptr[No].para_mode)
			{
				case 0:	/*电压单位:0.1V*/
					ret = (float) ADC_Ptr[No].FilterV * 0.00025456;		//U=V*5/1023/8/0.024/100==单位:100V
					temp = (sword)(ret * ADC_Ptr[No].K + ADC_Ptr[No].B);
					if(0xAA ==  ADC_Ptr[No].Status)
					{
						if(0 > temp)
						{
							ADC_Ptr[No].PH_Val = 0;
						}
						else if(400 >= temp)
						{
							ADC_Ptr[No].PH_Val = temp;
						}
						else
						{
							ADC_Ptr[No].PH_Val = 400;
						}
					}
					else
					{
						ADC_Ptr[No].PH_Val = temp;
					}
					break;
				case 1:	/*电流单位:1mA*/
					ret = (float) ADC_Ptr[No].FilterV * 0.00024957;		//I=V*5/1023/8/5100/0.00048
					temp = (sword)(ret * ADC_Ptr[No].K + ADC_Ptr[No].B);
					if(0xAA ==  ADC_Ptr[No].Status)
					{
						if(0 > temp)
						{
							ADC_Ptr[No].PH_Val = 0;
						}
						else if(2000 >= temp)
						{
							ADC_Ptr[No].PH_Val = temp;
						}
						else
						{
							ADC_Ptr[No].PH_Val = 2000;
						}
					}	
					else
					{
						ADC_Ptr[No].PH_Val = temp;
					}
					break;
				case 2:	/*温度单位:0.1℃*/
					//V = (R *(10000 - 300.920169)- 39000*300.920169)/(39000+ R)
					//R = 1000+3.85*T
					//T =((R - 1000)/3.85);
					//R = 39000 * (FilterV + 300.920169) / (10000 - 300.920169 - FilterV);
					
					mid = (float) ADC_Ptr[No].FilterV * 0.0006109 + 300.920169;		//V1 = V*5/1023/8 + 300.920169
					ret = mid  * 39000.0 / (10000.0 - mid);		//电阻值:R = 39000 * V1 / (10000.0 - V1)
					ret = (ret - 1000.0) /3.85;	//R=1000+3.85*T ->T = (R - 1000.0) / 3.85
					temp = (sword)((ret * ADC_Ptr[No].K + ADC_Ptr[No].B) / 100.0);
					if(0xAA ==  ADC_Ptr[No].Status)
					{
						if(-1000 > temp)
						{
							ADC_Ptr[No].PH_Val = -1000;
						}
						else if(2000 > temp )
						{
							ADC_Ptr[No].PH_Val = temp;
						}
						else
						{
							ADC_Ptr[No].PH_Val = 2000;
						}
					}
					else
					{
						ADC_Ptr[No].PH_Val = temp;
					}
					break;
				default:	/*其他单位:1*/
					ret = (float) ADC_Ptr[No].FilterV * 0.0006109;	//U=V*5/1023/8 
					temp = (sword)((ret * ADC_Ptr[No].K + ADC_Ptr[No].B) / 1000.0);
					ADC_Ptr[No].PH_Val = temp;
					break;
			}
		}
	}
	if(0 == No)
	{
		farVolt1.i = ADC_Ptr[0].PH_Val;
		if(200 > farVolt1.i)
		{
			farVolt1.i = 0;
		}
		else if(2000 < farVolt1.i)	//取2000
		{
			farVolt1.i = 2000;
		}
	}
	else if(1 == No)
	{
		farVolt2.i = ADC_Ptr[1].PH_Val;
		if(0 > farVolt2.i)
		{
			farVolt2.i = 0;
		}
		else if(2000 < farVolt2.i)
		{
			farVolt2.i = 2000;
		}
	}
}

void TimeSharing(void)//分时处理
{
	ubyte i;
	Sync_Start = 0xAA;
	if(0x55 == ChangeNod.Status)	//切换节点静默时间记时
	{
		ChangeNod.TimeCount --;
		if(0 == ChangeNod.TimeCount)
		{
			ChangeNod.Status = 0xAA;
		}
	}
	Task1ms.TimeCount ++;
	if(Task1msDelay <= Task1ms.TimeCount)//1ms任务记时
	{
		timingCnt++;			//毫秒记时
		Task1ms.TimeCount = 0;
		Task1ms.Status = 0xAA;
	}
	
	TaskSHBeat.TimeCount --;
	if(0 == TaskSHBeat.TimeCount)//发送心跳周期任务记时
	{
		TaskSHBeat.TimeCount = HBitSDelay;
		TaskSHBeat.Status = 0xAA;
	}
	TaskSTM1.TimeCount --;
	if(0 == TaskSTM1.TimeCount)//发送遥测1周期任务记时
	{
		TaskSTM1.TimeCount = HBitSDelay;
		TaskSTM1.Status = 0xAA;
	}
	TaskSTM2.TimeCount --;
	if(0 == TaskSTM2.TimeCount)//发送遥测2周期任务记时
	{
		TaskSTM2.TimeCount = HBitSDelay;
		TaskSTM2.Status = 0xAA;
	}
	for(i = 0; i < MAX_HBCNT; i++)
	{
		if(0x55 == Task15ms[i].Status)	//15ms接收转发应答任务记时
		{
			Task15ms[i].TimeCount --;
			if(0 == Task15ms[i].TimeCount)
			{
				Task15ms[i].Status = 0xAA;
			}
		}
		if(0x55 == TaskSSLT[i].Status)	//启动自检命令发送延时
		{
			TaskSSLT[i].TimeCount --;
			if(0 == TaskSSLT[i].TimeCount)
			{
				TaskSSLT[i].Status = 0xAA;
			}
		}
		if(0x55 == TaskRSLT[i].Status)	//等待自检命令应答延时
		{
			TaskRSLT[i].TimeCount --;
			if(0 == TaskRSLT[i].TimeCount)
			{
				TaskRSLT[i].Status = 0xAA;
			}
		}
		TaskRTM1[i].TimeCount --;		//接收RTU遥测1周期任务记时
		if(0 == TaskRTM1[i].TimeCount)	//接收心跳、遥测2周期任务记时
		{
			TaskRTM1[i].TimeCount = HBitRDelay;
			TaskRTM1[i].Status = 0xAA;
		}
		if(HB_count[i] < HB_Overflow_Time)	//未收到心跳记时
		{
			HB_count[i] ++；
		}
	}
	for(i = 0; i < 3; i++)	//接收心跳、遥测2周期任务记时
	{
		TaskRHBeat[i].TimeCount --;
		if(0 == TaskRHBeat[i].TimeCount)	//接收ERTU心跳周期任务记时
		{
			TaskRHBeat[i].TimeCount = HBitRDelay;
			TaskRHBeat[i].Status = 0xAA;
		}
		TaskRTM2[i].TimeCount ++;
		if(HBitRDelay <= TaskRTM2[i].TimeCount)	//接收ERTU遥测2周期任务记时
		{
			TaskRTM2[i].TimeCount = 0;
			TaskRTM2[i].Status = 0xAA;
		}
	}
	TaskAD.TimeCount --;
	if(0 == TaskAD.TimeCount)//AD任务记时
	{
		TaskAD.TimeCount = TaskADDelay;
		TaskAD.Status = 0xAA;
	}
	TaskIO.TimeCount --;
	if(0 == TaskIO.TimeCount)//AD任务记时
	{
		TaskIO.TimeCount = TaskIODelay;
		TaskIO.Status = 0xAA;
	}
	Task1s.TimeCount --;
	if(0 == Task1s.TimeCount)		//1s
	{
		TOGGLEIO_P2_12;	//呼吸灯闪烁
		Task1s.TimeCount = Task1sDelay;
		Task1s.Status = 0xAA;
	}

}


