#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发票合并打印助手 - 命令行接口
"""

import argparse
from .merger import InvoiceMerger


def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(
        description="发票合并打印助手 - 将电子发票按月份合并到A4纸上",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  invoice-merger ./invoices                     # 基本用法
  invoice-merger ./invoices -o ./output         # 指定输出目录
  invoice-merger ./invoices -c 2                # 每行2列
  invoice-merger ./invoices -o ./output -c 4    # 自定义输出和列数

输出:
  - 按月份生成PDF文件 (YYYY-MM.pdf)
  - 生成统计文件 (info.txt)
        """
    )

    parser.add_argument(
        "input_folder",
        help="输入文件夹路径（包含电子发票PDF文件）"
    )
    parser.add_argument(
        "-o", "--output",
        help="输出文件夹路径（默认: input_folder/output）"
    )
    parser.add_argument(
        "-c", "--columns",
        type=int,
        default=3,
        help="每行放置的列数 (默认: 3)"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 1.1.0"
    )

    args = parser.parse_args()

    # 创建合并器并运行
    merger = InvoiceMerger(
        input_folder=args.input_folder,
        output_folder=args.output,
        columns=args.columns
    )
    merger.run()


if __name__ == "__main__":
    main()
