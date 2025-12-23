#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 验证代码分析工具的功能
"""

import os
import tempfile
from pathlib import Path
from code_analyzer import CodeAnalyzer


def create_test_files():
    """创建测试用的C代码文件"""
    test_dir = Path("test_repo")
    test_dir.mkdir(exist_ok=True)
    
    # 创建main.c
    main_c = """
#include <stdio.h>
#include "system.h"

int main(int argc, char* argv[]) {
    printf("System starting...\\n");
    system_config();
    system_init();
    
    while(1) {
        system_loop();
    }
    
    return 0;
}

void system_loop() {
    // Main system loop
    check_inputs();
    process_data();
    update_outputs();
}
"""
    
    # 创建adc.c
    adc_c = """
#include "adc.h"

void ADC_Init(void) {
    // Initialize ADC module
    // Configure ADC registers
}

int ADC_Read(int channel) {
    // Read ADC value from specified channel
    // Return converted value
    return 0;
}

void ADC_Calibrate(void) {
    // Calibrate ADC for better accuracy
}
"""
    
    # 创建can.c
    can_c = """
#include "can.h"

void CAN_Init(void) {
    // Initialize CAN controller
}

int CAN_SendMessage(CAN_Message* msg) {
    // Send CAN message
    return 0;
}

int CAN_Receive(CAN_Message* msg) {
    // Receive CAN message
    return 0;
}
"""
    
    # 创建io.c
    io_c = """
#include "io.h"

void IO_SetLED(int led_id, int state) {
    // Set LED state
}

int IO_ReadButton(int button_id) {
    // Read button state
    return 0;
}

void IO_Init(void) {
    // Initialize IO pins
}
"""
    
    # 写入文件
    with open(test_dir / "main.c", "w") as f:
        f.write(main_c)
    
    with open(test_dir / "adc.c", "w") as f:
        f.write(adc_c)
    
    with open(test_dir / "can.c", "w") as f:
        f.write(can_c)
    
    with open(test_dir / "io.c", "w") as f:
        f.write(io_c)
    
    print(f"测试文件已创建在 {test_dir} 目录")
    return str(test_dir)


def test_without_api():
    """测试不使用API的功能"""
    print("=== 测试代码分析工具（不使用API）===")
    
    # 创建测试文件
    test_repo = create_test_files()
    
    # 创建分析器（使用无效的API密钥进行测试）
    analyzer = CodeAnalyzer(api_key="test_key")
    
    # 测试读取表格文件
    print("\\n1. 测试读取表格文件...")
    components = analyzer.read_table_file("example_table.txt")
    print(f"读取到 {len(components)} 个组件")
    for comp in components:
        print(f"  - {comp['name']}: {comp['function']}")
    
    # 测试查找C文件
    print("\\n2. 测试查找C文件...")
    c_files = analyzer.find_c_files(test_repo)
    print(f"找到 {len(c_files)} 个C文件")
    for file in c_files:
        print(f"  - {file}")
    
    # 测试提取函数
    print("\\n3. 测试提取函数...")
    all_functions = []
    for file_path in c_files:
        functions = analyzer.extract_functions_from_file(file_path)
        all_functions.extend(functions)
        print(f"  {file_path}: {len(functions)} 个函数")
        for func in functions:
            print(f"    - {func['name']} (第{func['line_number']}行)")
    
    # 测试函数筛选
    print("\\n4. 测试函数筛选...")
    for component in components[:2]:  # 只测试前两个组件
        relevant_functions = analyzer.filter_functions_by_component(all_functions, component)
        print(f"  {component['name']}: {len(relevant_functions)} 个相关函数")
        for func in relevant_functions:
            print(f"    - {func['name']}")
    
    print("\\n✅ 基础功能测试完成！")
    print("\\n注意: 要使用完整功能，请配置有效的DeepSeek API密钥")


if __name__ == "__main__":
    test_without_api()