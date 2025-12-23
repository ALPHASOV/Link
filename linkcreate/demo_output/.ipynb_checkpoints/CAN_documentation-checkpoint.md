# CAN 组件文档

**生成时间**: 2025-07-18 20:37:54


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


## 数据来源映射

- **CAN**: root.system_architecture.main_controller.modules.CAN (key)
- **CAN**: root.hardware_interfaces.communication.CAN_interface (key)
- **CAN**: root.hardware_interfaces.communication.CAN_interface.message_format (value)
- **CAN_SendMessage()**: root.hardware_interfaces.communication.CAN_interface.CAN_SendMessage() (key)
- **CAN**: root.hardware_interfaces.communication.CAN_interface.CAN_SendMessage() (key)
- **CAN**: root.hardware_interfaces.communication.CAN_interface.CAN_SendMessage() (value)
- **CAN_Receive()**: root.hardware_interfaces.communication.CAN_interface.CAN_Receive() (key)
- **CAN**: root.hardware_interfaces.communication.CAN_interface.CAN_Receive() (key)
- **CAN**: root.hardware_interfaces.communication.CAN_interface.CAN_Receive() (value)
- **CAN**: root.hardware_interfaces.communication.protocols.CANopen (key)
- **CAN**: root.hardware_interfaces.communication.protocols.CANopen (value)
- **通信协议**: root.hardware_interfaces.communication.protocols.J1939 (value)
