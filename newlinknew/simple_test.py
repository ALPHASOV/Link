#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化测试脚本 - 验证基础功能（不需要外部依赖）
"""

import os
import re
from pathlib import Path


def read_table_file(table_file_path):
    """读取表格文件，解析组件信息"""
    components = []
    try:
        with open(table_file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split('//')
                if len(parts) >= 3:
                    component = {
                        'name': parts[0].strip(),
                        'function': parts[1].strip(),
                        'key_functions': parts[2].strip(),
                        'line_number': line_num
                    }
                    components.append(component)
                else:
                    print(f"警告: 第{line_num}行格式不正确: {line}")
    except FileNotFoundError:
        print(f"错误: 找不到表格文件 {table_file_path}")
    except Exception as e:
        print(f"错误: 读取表格文件时出错: {e}")
    
    return components


def find_c_files(repo_path):
    """查找仓库中所有的.c和.h文件"""
    c_files = []
    repo_path = Path(repo_path)
    
    if not repo_path.exists():
        print(f"错误: 仓库路径不存在: {repo_path}")
        return c_files
    
    # 递归查找.c和.h文件
    for file_path in repo_path.rglob("*"):
        if file_path.suffix.lower() in ['.c', '.h']:
            c_files.append(str(file_path))
    
    print(f"找到 {len(c_files)} 个C/H文件")
    return c_files


def extract_functions_from_file(file_path):
    """从C/H文件中提取函数定义"""
    functions = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 正则表达式匹配函数定义
        function_pattern = r'(?:^|\n)\s*([a-zA-Z_][a-zA-Z0-9_\s\*]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(?:\{|;)'
        
        matches = re.finditer(function_pattern, content, re.MULTILINE)
        
        for match in matches:
            return_type = match.group(1).strip()
            function_name = match.group(2).strip()
            
            # 跳过一些常见的非函数匹配
            if function_name in ['if', 'while', 'for', 'switch', 'return']:
                continue
            
            # 计算行号
            line_number = content[:match.start()].count('\n') + 1
            
            # 提取完整的函数签名
            start_pos = match.start()
            end_pos = content.find('\n', match.end())
            if end_pos == -1:
                end_pos = match.end()
            
            function_signature = content[start_pos:end_pos].strip()
            
            functions.append({
                'name': function_name,
                'return_type': return_type,
                'signature': function_signature,
                'file_path': file_path,
                'line_number': line_number
            })
    
    except Exception as e:
        print(f"错误: 解析文件 {file_path} 时出错: {e}")
    
    return functions


def create_test_files():
    """创建测试用的C代码文件"""
    test_dir = Path("test_repo")
    test_dir.mkdir(exist_ok=True)
    
    # 创建main.c
    main_c = """#include <stdio.h>
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
    adc_c = """#include "adc.h"

void ADC_Init(void) {
    // Initialize ADC module
}

int ADC_Read(int channel) {
    // Read ADC value from specified channel
    return 0;
}

void ADC_Calibrate(void) {
    // Calibrate ADC for better accuracy
}
"""
    
    # 创建can.c
    can_c = """#include "can.h"

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
    io_c = """#include "io.h"

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


def main():
    """主测试函数"""
    print("=== 代码分析工具基础功能测试 ===")
    
    # 创建测试文件
    test_repo = create_test_files()
    
    # 测试读取表格文件
    print("\n1. 测试读取表格文件...")
    components = read_table_file("example_table.txt")
    print(f"读取到 {len(components)} 个组件")
    for comp in components:
        print(f"  - {comp['name']}: {comp['function']}")
    
    # 测试查找C文件
    print("\n2. 测试查找C文件...")
    c_files = find_c_files(test_repo)
    print(f"找到 {len(c_files)} 个C文件")
    for file in c_files:
        print(f"  - {file}")
    
    # 测试提取函数
    print("\n3. 测试提取函数...")
    all_functions = []
    for file_path in c_files:
        functions = extract_functions_from_file(file_path)
        all_functions.extend(functions)
        print(f"  {Path(file_path).name}: {len(functions)} 个函数")
        for func in functions:
            print(f"    - {func['name']} (第{func['line_number']}行)")
    
    print(f"\n总共找到 {len(all_functions)} 个函数")
    
    print("\n✅ 基础功能测试完成！")
    print("\n📝 项目文件说明:")
    print("  - main.py: 主程序入口")
    print("  - code_analyzer.py: 核心分析器类")
    print("  - config.py: 配置文件（需要设置DeepSeek API密钥）")
    print("  - example_table.txt: 示例表格文件")
    print("  - README.md: 详细使用说明")
    print("\n🚀 使用方法:")
    print("  1. 在config.py中设置您的DeepSeek API密钥")
    print("  2. 准备您的组件表格文件")
    print("  3. 运行: python main.py <表格文件> <代码仓库路径>")


if __name__ == "__main__":
    main()