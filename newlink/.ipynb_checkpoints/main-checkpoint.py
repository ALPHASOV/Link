#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序入口 - 代码分析工具
"""

import sys
import argparse
from pathlib import Path
from code_analyzer import CodeAnalyzer


def main():
    parser = argparse.ArgumentParser(description='代码分析工具 - 使用DeepSeek API分析C代码仓库')
    parser.add_argument('table_file', help='组件表格文件路径 (txt格式)')
    parser.add_argument('repo_path', help='代码仓库路径')
    parser.add_argument('-o', '--output', default='output', help='输出目录 (默认: output)')
    parser.add_argument('-k', '--api-key', help='DeepSeek API密钥 (可选，会覆盖config.py中的设置)')
    parser.add_argument('-d', '--detailed', action='store_true', help='使用详细分析模式（包含find_others功能）')
    
    args = parser.parse_args()
    
    # 检查输入文件
    if not Path(args.table_file).exists():
        print(f"错误: 表格文件不存在: {args.table_file}")
        sys.exit(1)
    
    if not Path(args.repo_path).exists():
        print(f"错误: 仓库路径不存在: {args.repo_path}")
        sys.exit(1)
    
    # 创建分析器
    if args.api_key:
        analyzer = CodeAnalyzer(api_key=args.api_key)
    else:
        analyzer = CodeAnalyzer()
    
    # 开始处理
    try:
        if args.detailed:
            print("使用详细分析模式（包含find_others功能）...")
            analyzer.process_repository_with_detailed_analysis(args.table_file, args.repo_path, args.output)
        else:
            print("使用标准分析模式...")
            analyzer.process_repository(args.table_file, args.repo_path, args.output)
        print("\n✅ 分析完成！")
    except KeyboardInterrupt:
        print("\n❌ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 处理过程中出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()