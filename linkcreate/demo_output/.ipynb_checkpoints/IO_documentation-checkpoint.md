# IO 组件文档

**生成时间**: 2025-07-18 20:37:56


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


## 数据来源映射

- **输入输出**: root.system_architecture.main_controller.modules.IO (value)
- **输入输出**: root.hardware_interfaces.digital_io.gpio_ports.port_A (value)
- **输入输出**: root.hardware_interfaces.digital_io.gpio_ports.port_B (value)
- **输入输出**: root.hardware_interfaces.digital_io.gpio_ports.port_C (value)
- **IO_SetLED()**: root.hardware_interfaces.digital_io.IO_SetLED() (key)
- **LED**: root.hardware_interfaces.digital_io.IO_SetLED() (key)
- **LED**: root.hardware_interfaces.digital_io.IO_SetLED() (value)
- **IO_ReadButton()**: root.hardware_interfaces.digital_io.IO_ReadButton() (key)
- **按钮**: root.hardware_interfaces.digital_io.IO_ReadButton() (value)
- **LED**: root.hardware_interfaces.digital_io.led_indicators (key)
- **LED**: root.hardware_interfaces.digital_io.led_indicators.power_led (key)
- **LED**: root.hardware_interfaces.digital_io.led_indicators.status_led (key)
- **LED**: root.hardware_interfaces.digital_io.led_indicators.error_led (key)
- **按钮**: root.hardware_interfaces.digital_io.button_inputs.reset_button (value)
- **按钮**: root.hardware_interfaces.digital_io.button_inputs.mode_button (value)
