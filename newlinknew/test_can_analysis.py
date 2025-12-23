#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAN组件分析功能测试脚本
测试改进后的代码分析工具对CAN相关函数的识别和分析能力
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def create_test_can_code():
    """创建测试用的CAN相关C代码文件"""
    test_dir = current_dir / "test_can_code"
    test_dir.mkdir(exist_ok=True)
    
    # 创建CAN驱动文件
    can_driver_code = '''
#include "can_driver.h"
#include <stdint.h>

// CAN控制器初始化
int CAN_Init(uint32_t baudrate) {
    // 配置CAN控制器波特率
    CAN_REG->BAUD = baudrate;
    // 启用CAN控制器
    CAN_REG->CTRL |= CAN_CTRL_ENABLE;
    return 0;
}

// 发送CAN消息
int CAN_SendMessage(uint32_t id, uint8_t* data, uint8_t length) {
    if (length > 8) return -1;
    
    // 设置消息ID
    CAN_REG->TX_ID = id;
    // 设置数据长度
    CAN_REG->TX_DLC = length;
    // 复制数据
    for (int i = 0; i < length; i++) {
        CAN_REG->TX_DATA[i] = data[i];
    }
    // 发送消息
    CAN_REG->TX_CMD = CAN_TX_START;
    return 0;
}

// 接收CAN消息
int CAN_ReceiveMessage(uint32_t* id, uint8_t* data, uint8_t* length) {
    // 检查是否有消息
    if (!(CAN_REG->STATUS & CAN_RX_READY)) {
        return -1;
    }
    
    // 读取消息ID
    *id = CAN_REG->RX_ID;
    // 读取数据长度
    *length = CAN_REG->RX_DLC;
    // 读取数据
    for (int i = 0; i < *length; i++) {
        data[i] = CAN_REG->RX_DATA[i];
    }
    
    // 清除接收标志
    CAN_REG->STATUS &= ~CAN_RX_READY;
    return 0;
}

// 设置CAN过滤器
void CAN_SetFilter(uint32_t filter_id, uint32_t mask) {
    CAN_REG->FILTER_ID = filter_id;
    CAN_REG->FILTER_MASK = mask;
    CAN_REG->FILTER_CTRL |= CAN_FILTER_ENABLE;
}

// 获取CAN状态
uint32_t CAN_GetStatus(void) {
    return CAN_REG->STATUS;
}

// 通用延时函数（与CAN无关）
void delay_ms(uint32_t ms) {
    for (volatile uint32_t i = 0; i < ms * 1000; i++) {
        // 空循环延时
    }
}

// 系统时钟配置（与CAN无关）
void SystemClock_Config(void) {
    // 配置系统时钟
    RCC->CR |= RCC_CR_HSEON;
    while (!(RCC->CR & RCC_CR_HSERDY));
}
'''
    
    with open(test_dir / "can_driver.c", "w", encoding="utf-8") as f:
        f.write(can_driver_code)
    
    # 创建CAN应用层文件
    can_app_code = '''
#include "can_app.h"
#include "can_driver.h"

// CAN应用层初始化
int CAN_App_Init(void) {
    // 初始化CAN驱动
    if (CAN_Init(500000) != 0) {
        return -1;
    }
    
    // 设置接收过滤器
    CAN_SetFilter(0x123, 0x7FF);
    return 0;
}

// 发送心跳消息
void CAN_SendHeartbeat(void) {
    uint8_t heartbeat_data[1] = {0x01};
    CAN_SendMessage(0x700, heartbeat_data, 1);
}

// 处理接收到的CAN消息
void CAN_ProcessMessage(uint32_t id, uint8_t* data, uint8_t length) {
    switch (id) {
        case 0x123:
            // 处理控制命令
            handle_control_command(data, length);
            break;
        case 0x456:
            // 处理状态查询
            handle_status_query(data, length);
            break;
        default:
            // 未知消息ID
            break;
    }
}

// 数学计算函数（与CAN无关）
int calculate_checksum(uint8_t* data, int length) {
    int sum = 0;
    for (int i = 0; i < length; i++) {
        sum += data[i];
    }
    return sum & 0xFF;
}

// 字符串处理函数（与CAN无关）
void string_copy(char* dest, const char* src) {
    while (*src) {
        *dest++ = *src++;
    }
    *dest = '\\0';
}
'''
    
    with open(test_dir / "can_app.c", "w", encoding="utf-8") as f:
        f.write(can_app_code)
    
    print(f"已创建测试CAN代码文件在: {test_dir}")
    return test_dir

def create_test_table():
    """创建测试用的组件表格文件"""
    table_content = '''组件名	功能	关键函数
CAN	发送/接收CAN消息	CAN_SendMessage()、CAN_ReceiveMessage()、CAN_Init()、CAN_SetFilter()、CAN_GetStatus()、CAN_App_Init()、CAN_SendHeartbeat()、CAN_ProcessMessage()
'''
    
    table_file = current_dir / "test_can_table.txt"
    with open(table_file, "w", encoding="utf-8") as f:
        f.write(table_content)
    
    print(f"已创建测试表格文件: {table_file}")
    return table_file

def run_can_analysis_test():
    """运行CAN组件分析测试"""
    print("开始CAN组件分析功能测试...")
    
    # 创建测试文件
    test_code_dir = create_test_can_code()
    test_table_file = create_test_table()
    
    # 导入分析器
    try:
        from code_analyzer import CodeAnalyzer
        from main import parse_component_table
        
        # 解析组件表格
        components = parse_component_table(str(test_table_file))
        print(f"解析到 {len(components)} 个组件")
        
        # 创建分析器实例
        analyzer = CodeAnalyzer()
        
        # 分析CAN组件
        can_component = components[0]  # CAN组件
        print(f"\\n分析组件: {can_component['name']}")
        print(f"功能描述: {can_component['description']}")
        print(f"关键函数: {can_component['keywords']}")
        
        # 扫描代码文件
        code_files = analyzer.scan_code_files(str(test_code_dir))
        print(f"\\n找到 {len(code_files)} 个代码文件:")
        for file_path in code_files:
            print(f"  - {file_path}")
        
        # 提取函数
        all_functions = []
        for file_path in code_files:
            functions = analyzer.extract_functions_from_file(file_path)
            all_functions.extend(functions)
        
        print(f"\\n提取到 {len(all_functions)} 个函数:")
        for func in all_functions:
            print(f"  - {func['name']} (文件: {func['file_path'].split('/')[-1]})")
        
        # 筛选相关函数
        filtered_functions = analyzer.filter_functions_by_component(all_functions, can_component)
        print(f"\\n筛选出 {len(filtered_functions)} 个相关函数:")
        for func in filtered_functions:
            score = func.get('relevance_score', 0)
            print(f"  - {func['name']} (相关性得分: {score})")
        
        # 生成报告
        output_dir = current_dir / "test_output"
        output_dir.mkdir(exist_ok=True)
        
        print(f"\\n正在生成分析报告...")
        print("注意: 由于未配置DeepSeek API密钥，将使用备用描述")
        
        # 模拟分析结果（因为没有真实的API密钥）
        mock_analysis_results = []
        for func in filtered_functions:
            mock_result = {
                'function_name': func['name'],
                'function_description': f"函数 {func['name']} 的详细分析暂时不可用（需要配置API密钥）",
                'parameters': func.get('signature', ''),
                'return_value': func.get('return_type', 'unknown'),
                'file_path': func['file_path'],
                'line_number': func.get('line_number', 0),
                'relevance_score': func.get('relevance_score', 0),
                'component_relevance': '相关' if func.get('relevance_score', 0) > 5 else '低度相关',
                'is_relevant': func.get('relevance_score', 0) > 3
            }
            mock_analysis_results.append(mock_result)
        
        # 生成报告文件
        analyzer.generate_component_report(can_component, mock_analysis_results, str(output_dir))
        
        print(f"\\n测试完成！")
        print(f"输出目录: {output_dir}")
        print("\\n测试总结:")
        print(f"- 扫描了 {len(code_files)} 个代码文件")
        print(f"- 提取了 {len(all_functions)} 个函数")
        print(f"- 筛选出 {len(filtered_functions)} 个相关函数")
        print(f"- 生成了分析报告")
        
        return True
        
    except ImportError as e:
        print(f"导入模块失败: {e}")
        return False
    except Exception as e:
        print(f"测试过程中出错: {e}")
        return False

if __name__ == "__main__":
    success = run_can_analysis_test()
    if success:
        print("\\n✅ CAN组件分析功能测试成功！")
    else:
        print("\\n❌ CAN组件分析功能测试失败！")