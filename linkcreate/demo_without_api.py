#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示脚本（无需API）
展示文档处理器的核心功能，不调用真实的DeepSeek API
"""

import json
import os
from datetime import datetime
from deepseek_document_processor import DeepSeekDocumentProcessor

class MockDeepSeekProcessor(DeepSeekDocumentProcessor):
    """
    模拟的DeepSeek处理器，用于演示功能
    """
    
    def __init__(self):
        # 不需要真实的API密钥
        self.api_key = "demo-key"
        self.base_url = "demo-url"
    
    def call_deepseek_api(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """
        模拟API调用，返回预设的文档内容
        """
        # 根据提示词中的组件名称返回不同的模拟文档
        if "MAIN" in prompt:
            return self._generate_main_doc()
        elif "ADC" in prompt:
            return self._generate_adc_doc()
        elif "CAN" in prompt:
            return self._generate_can_doc()
        elif "GPT" in prompt:
            return self._generate_gpt_doc()
        elif "IO" in prompt:
            return self._generate_io_doc()
        elif "SCS" in prompt:
            return self._generate_scs_doc()
        else:
            return self._generate_generic_doc()
    
    def _generate_main_doc(self):
        return """
## 组件概述

MAIN组件是整个系统的核心控制模块，负责系统的初始化和各个子模块的协调管理。作为系统的入口点，它确保所有硬件和软件组件按照正确的顺序启动并进入正常工作状态。

## 功能详细说明

### 系统初始化
- **硬件初始化**: 配置CPU时钟、内存控制器、中断控制器等基础硬件
- **模块初始化**: 按照依赖关系顺序初始化各个功能模块
- **系统自检**: 验证各模块的初始化状态和基本功能
- **配置加载**: 从配置文件或EEPROM中加载系统参数

### 主循环管理
- **任务调度**: 管理系统中各个任务的执行顺序和优先级
- **事件处理**: 响应系统事件和中断请求
- **状态监控**: 持续监控系统运行状态

## 技术实现要点

1. **启动顺序控制**: 确保关键模块优先初始化
2. **错误处理机制**: 在初始化失败时提供恢复策略
3. **资源管理**: 合理分配系统资源给各个模块
4. **同步机制**: 确保多模块间的协调工作

## 相关API或接口说明

### main()
- **功能**: 系统主入口函数
- **参数**: 无
- **返回值**: int (0表示正常退出)
- **调用时机**: 系统启动时

### system_config()
- **功能**: 系统配置函数
- **参数**: 配置参数结构体
- **返回值**: 配置状态码
- **调用时机**: main()函数中的初始化阶段

## 使用示例或注意事项

### 使用示例
```c
int main(void) {
    // 系统配置
    if (system_config() != CONFIG_SUCCESS) {
        return ERROR_CONFIG_FAILED;
    }
    
    // 模块初始化
    init_all_modules();
    
    // 进入主循环
    while (1) {
        process_tasks();
        handle_events();
    }
    
    return 0;
}
```

### 注意事项
- 确保在调用其他模块前完成MAIN模块的初始化
- 监控系统资源使用情况，避免内存泄漏
- 实现看门狗机制防止系统死锁
"""
    
    def _generate_adc_doc(self):
        return """
## 组件概述

ADC（模拟数字转换器）组件负责将模拟信号转换为数字信号，是系统与外部模拟世界交互的重要接口。该组件支持多通道采样，具有高精度和快速转换的特点。

## 功能详细说明

### 信号采集
- **多通道支持**: 支持最多8个模拟输入通道
- **高精度转换**: 12位分辨率，确保测量精度
- **快速采样**: 采样率可达1MHz
- **自动校准**: 内置校准机制，确保长期稳定性

### 数据处理
- **滤波功能**: 内置数字滤波器，减少噪声干扰
- **阈值检测**: 支持设置上下限阈值，自动报警
- **数据缓存**: 提供FIFO缓存，支持批量数据读取

## 技术实现要点

1. **参考电压管理**: 使用稳定的参考电压源
2. **采样时序控制**: 精确控制采样时间和转换时间
3. **中断机制**: 支持转换完成中断和阈值越限中断
4. **DMA支持**: 可配置DMA传输，减少CPU负载

## 相关API或接口说明

### ADC_Init()
- **功能**: ADC模块初始化
- **参数**: 配置结构体（采样率、通道配置等）
- **返回值**: 初始化状态码
- **调用时机**: 系统初始化阶段

### ADC_Read(channel)
- **功能**: 读取指定通道的ADC值
- **参数**: channel - 通道号（0-7）
- **返回值**: 12位ADC转换结果
- **调用时机**: 需要获取模拟量时

## 使用示例或注意事项

### 使用示例
```c
// 初始化ADC
ADC_Config_t config = {
    .sample_rate = ADC_1MHZ,
    .resolution = ADC_12BIT,
    .reference = ADC_VREF_3V3
};
ADC_Init(&config);

// 读取通道0的值
uint16_t adc_value = ADC_Read(0);
float voltage = (adc_value * 3.3f) / 4096.0f;
```

### 注意事项
- 确保输入信号在允许的电压范围内
- 考虑信号的建立时间，避免采样过快
- 定期进行校准以保持精度
"""
    
    def _generate_can_doc(self):
        return """
## 组件概述

CAN（控制器局域网）组件实现了CAN总线通信协议，支持高可靠性的网络通信。该组件广泛应用于汽车电子、工业控制等领域，具有强大的错误检测和处理能力。

## 功能详细说明

### 通信协议
- **CAN 2.0A/B支持**: 兼容标准和扩展帧格式
- **多波特率**: 支持125kbps到1Mbps的波特率
- **自动重传**: 发送失败时自动重传机制
- **错误检测**: CRC校验、位填充检测等

### 消息管理
- **消息过滤**: 硬件消息过滤器，减少CPU负载
- **优先级仲裁**: 基于消息ID的优先级仲裁
- **消息缓存**: 发送和接收FIFO缓存

## 技术实现要点

1. **位时序配置**: 精确配置位时序参数
2. **错误处理**: 实现错误帧检测和恢复机制
3. **总线状态监控**: 监控总线负载和错误率
4. **同步机制**: 确保消息的实时性

## 相关API或接口说明

### CAN_SendMessage()
- **功能**: 发送CAN消息
- **参数**: 消息ID、数据指针、数据长度
- **返回值**: 发送状态码
- **调用时机**: 需要发送数据时

### CAN_Receive()
- **功能**: 接收CAN消息
- **参数**: 消息缓存指针
- **返回值**: 接收到的消息数量
- **调用时机**: 定期轮询或中断触发

## 使用示例或注意事项

### 使用示例
```c
// 发送消息
CAN_Message_t msg = {
    .id = 0x123,
    .length = 8,
    .data = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08}
};
CAN_SendMessage(&msg);

// 接收消息
CAN_Message_t rx_msg;
if (CAN_Receive(&rx_msg) > 0) {
    // 处理接收到的消息
    process_message(&rx_msg);
}
```

### 注意事项
- 确保总线终端电阻正确配置
- 监控总线错误率，及时处理异常
- 合理设计消息ID分配策略
"""
    
    def _generate_gpt_doc(self):
        return """
## 组件概述

GPT（通用定时器）组件提供精确的时间控制功能，支持多种定时模式和PWM输出。该组件是系统时序控制的核心，广泛用于任务调度、信号生成和时间测量。

## 功能详细说明

### 定时功能
- **多定时器支持**: 支持多个独立的定时器通道
- **高精度计时**: 微秒级精度的时间控制
- **多种模式**: 单次定时、周期定时、PWM输出等
- **级联功能**: 支持定时器级联，扩展计时范围

### PWM输出
- **可调占空比**: 0-100%占空比调节
- **频率控制**: 宽范围频率输出
- **多通道同步**: 支持多通道同步PWM输出

## 技术实现要点

1. **时钟源选择**: 支持多种时钟源配置
2. **预分频器**: 灵活的预分频配置
3. **中断机制**: 定时器溢出和比较匹配中断
4. **DMA支持**: 支持DMA更新比较值

## 相关API或接口说明

### GPT_Init()
- **功能**: 定时器初始化
- **参数**: 定时器配置结构体
- **返回值**: 初始化状态码
- **调用时机**: 系统初始化阶段

### GPT_StartTimer()
- **功能**: 启动定时器
- **参数**: 定时器ID、定时周期
- **返回值**: 启动状态码
- **调用时机**: 需要开始计时时

## 使用示例或注意事项

### 使用示例
```c
// 初始化定时器
GPT_Config_t config = {
    .timer_id = GPT_TIMER0,
    .mode = GPT_MODE_PERIODIC,
    .period_us = 1000  // 1ms周期
};
GPT_Init(&config);

// 启动定时器
GPT_StartTimer(GPT_TIMER0, 1000);

// PWM输出配置
GPT_SetPWM(GPT_TIMER1, 1000, 50);  // 1kHz, 50%占空比
```

### 注意事项
- 选择合适的时钟源和预分频值
- 避免定时器溢出导致的时序错误
- 合理分配定时器资源
"""
    
    def _generate_io_doc(self):
        return """
## 组件概述

IO（输入输出）组件管理系统的数字输入输出接口，包括GPIO控制、LED指示、按键检测等功能。该组件是系统与外部设备交互的重要接口。

## 功能详细说明

### GPIO控制
- **多端口支持**: 支持多个GPIO端口
- **方向配置**: 可配置为输入或输出模式
- **上拉下拉**: 内置上拉下拉电阻配置
- **中断功能**: 支持边沿触发和电平触发中断

### LED控制
- **多LED支持**: 支持多个LED指示灯
- **亮度控制**: PWM调光功能
- **闪烁模式**: 多种闪烁模式选择

### 按键检测
- **防抖处理**: 硬件和软件防抖机制
- **长按检测**: 支持长按和短按检测
- **组合按键**: 支持多按键组合检测

## 技术实现要点

1. **电平转换**: 支持不同电压电平的IO接口
2. **保护机制**: 过压和过流保护
3. **低功耗设计**: 支持低功耗模式
4. **实时响应**: 快速的IO状态变化响应

## 相关API或接口说明

### IO_SetLED()
- **功能**: 设置LED状态
- **参数**: LED编号、状态（开/关/闪烁）
- **返回值**: 操作状态码
- **调用时机**: 需要控制LED时

### IO_ReadButton()
- **功能**: 读取按键状态
- **参数**: 按键编号
- **返回值**: 按键状态（按下/释放）
- **调用时机**: 需要检测按键时

## 使用示例或注意事项

### 使用示例
```c
// 设置LED状态
IO_SetLED(LED_POWER, LED_ON);     // 电源LED开启
IO_SetLED(LED_STATUS, LED_BLINK); // 状态LED闪烁

// 读取按键状态
if (IO_ReadButton(BUTTON_RESET) == BUTTON_PRESSED) {
    // 处理复位按键按下事件
    system_reset();
}

// GPIO配置
IO_ConfigGPIO(GPIO_PORT_A, GPIO_PIN_0, GPIO_OUTPUT);
IO_WriteGPIO(GPIO_PORT_A, GPIO_PIN_0, GPIO_HIGH);
```

### 注意事项
- 确保IO电压电平匹配
- 合理设置防抖时间
- 避免IO冲突和短路
"""
    
    def _generate_scs_doc(self):
        return """
## 组件概述

SCS（系统状态监控）组件负责监控系统的运行状态，包括硬件状态、软件状态、性能指标等。该组件是系统可靠性和稳定性的重要保障。

## 功能详细说明

### 状态监控
- **硬件监控**: CPU温度、电压、时钟频率等
- **软件监控**: 任务状态、内存使用、堆栈溢出等
- **性能监控**: CPU使用率、响应时间、吞吐量等
- **通信监控**: 总线状态、网络连接、数据传输等

### 故障检测
- **看门狗机制**: 防止系统死锁
- **异常检测**: 检测系统异常和错误
- **自动恢复**: 故障自动恢复机制
- **日志记录**: 详细的故障日志记录

### 诊断功能
- **自检程序**: 系统启动自检
- **在线诊断**: 运行时诊断功能
- **远程诊断**: 支持远程诊断接口

## 技术实现要点

1. **实时监控**: 高频率的状态采样
2. **阈值管理**: 灵活的阈值配置
3. **事件驱动**: 基于事件的状态变化处理
4. **数据存储**: 状态数据的持久化存储

## 相关API或接口说明

### SCS_Init()
- **功能**: 系统状态监控初始化
- **参数**: 监控配置参数
- **返回值**: 初始化状态码
- **调用时机**: 系统初始化阶段

### SCS_CheckStatus()
- **功能**: 检查系统状态
- **参数**: 状态类型
- **返回值**: 系统状态信息
- **调用时机**: 定期状态检查

## 使用示例或注意事项

### 使用示例
```c
// 初始化状态监控
SCS_Config_t config = {
    .monitor_interval = 100,  // 100ms监控间隔
    .enable_watchdog = true,
    .temp_threshold = 85      // 85°C温度阈值
};
SCS_Init(&config);

// 检查系统状态
SCS_Status_t status;
if (SCS_CheckStatus(&status) == SCS_OK) {
    if (status.cpu_temp > TEMP_WARNING) {
        // 处理过温警告
        handle_overheat_warning();
    }
}

// 喂狗操作
SCS_FeedWatchdog();
```

### 注意事项
- 合理设置监控间隔，平衡性能和实时性
- 及时响应状态变化和告警
- 定期更新看门狗，防止系统重启
"""
    
    def _generate_generic_doc(self):
        return """
## 组件概述

该组件是系统的重要组成部分，提供特定的功能和服务。

## 功能详细说明

基于提供的技术信息，该组件具有以下主要功能：
- 核心功能实现
- 接口管理
- 状态控制
- 错误处理

## 技术实现要点

1. 模块化设计
2. 接口标准化
3. 错误处理机制
4. 性能优化

## 相关API或接口说明

详细的API说明请参考技术文档。

## 使用示例或注意事项

请根据具体的应用场景合理使用该组件。
"""

def demo_search_functionality():
    """
    演示搜索功能
    """
    print("=== 搜索功能演示 ===")
    
    # 创建模拟处理器
    processor = MockDeepSeekProcessor()
    
    # 加载示例数据
    components_data = processor.load_json_file("components.json")
    technical_data = processor.load_json_file("technical_data.json")
    
    if not components_data or not technical_data:
        print("无法加载示例数据文件")
        return
    
    # 提取组件信息
    components = processor.extract_component_info(components_data)
    print(f"\n提取到 {len(components)} 个组件:")
    
    for i, component in enumerate(components, 1):
        print(f"{i}. {component['name']}: {component['function']}")
        print(f"   关键词: {', '.join(component['keywords'])}")
        
        # 搜索相关信息
        related_info = processor.search_related_info(component['keywords'], technical_data)
        print(f"   找到 {len(related_info)} 条相关信息")
        
        # 显示前3条匹配信息
        for j, info in enumerate(related_info[:3], 1):
            print(f"     {j}. 路径: {info['path']}")
            print(f"        关键词: {info['matched_keyword']}")
            print(f"        类型: {info['type']}")
        
        if len(related_info) > 3:
            print(f"     ... 还有 {len(related_info) - 3} 条信息")
        
        print()

def demo_document_generation():
    """
    演示文档生成功能
    """
    print("=== 文档生成演示 ===")
    
    # 创建模拟处理器
    processor = MockDeepSeekProcessor()
    
    # 演示为ADC组件生成文档
    component = {
        "name": "ADC",
        "function": "读取模拟信号",
        "keywords": ["ADC_Init()", "ADC_Read(channel)", "模拟转换"]
    }
    
    # 模拟相关信息
    related_info = [
        {
            "path": "hardware_interfaces.analog_inputs.ADC_Init()",
            "matched_keyword": "ADC_Init()",
            "type": "key",
            "content": "ADC_Init(): ADC模块初始化函数，配置采样率和通道"
        },
        {
            "path": "hardware_interfaces.analog_inputs.ADC_Read(channel)",
            "matched_keyword": "ADC_Read(channel)",
            "type": "key",
            "content": "ADC_Read(channel): 读取指定通道的模拟信号值"
        }
    ]
    
    print(f"\n为组件 '{component['name']}' 生成文档...")
    print(f"组件功能: {component['function']}")
    print(f"关键词: {', '.join(component['keywords'])}")
    print(f"相关信息: {len(related_info)} 条")
    
    # 生成文档
    document = processor.generate_component_document(component, related_info)
    
    print("\n生成的文档内容:")
    print("=" * 60)
    print(document)
    print("=" * 60)

def demo_full_process():
    """
    演示完整的处理流程
    """
    print("=== 完整流程演示 ===")
    
    # 创建模拟处理器
    processor = MockDeepSeekProcessor()
    
    # 设置输出目录
    output_dir = "demo_output"
    
    print(f"\n开始处理文档，输出目录: {output_dir}")
    
    # 处理文档
    processor.process_documents(
        components_file="components.json",
        search_file="technical_data.json",
        output_dir=output_dir
    )
    
    print(f"\n处理完成！请查看 {output_dir} 目录中的生成文件。")

def main():
    """
    主演示函数
    """
    print("DeepSeek 文档处理器 - 功能演示")
    print("(本演示使用模拟数据，无需真实API密钥)")
    print("=" * 50)
    
    while True:
        print("\n请选择演示功能:")
        print("1. 搜索功能演示")
        print("2. 文档生成演示")
        print("3. 完整流程演示")
        print("0. 退出")
        
        choice = input("\n请输入选择 (0-3): ").strip()
        
        if choice == "1":
            demo_search_functionality()
        elif choice == "2":
            demo_document_generation()
        elif choice == "3":
            demo_full_process()
        elif choice == "0":
            print("演示结束，谢谢使用！")
            break
        else:
            print("无效选择，请重新输入")
        
        input("\n按回车键继续...")

if __name__ == "__main__":
    main()