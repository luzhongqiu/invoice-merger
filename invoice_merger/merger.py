#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发票合并打印助手 - 核心模块
"""

import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict

import fitz  # PyMuPDF
from tqdm import tqdm

# 隐藏 MuPDF 警告信息（PDF 内部结构问题不影响功能）
fitz.TOOLS.mupdf_display_errors(False)


class InvoiceMerger:
    """发票合并器"""

    # A4纸尺寸 (单位: 点, 1英寸=72点, A4=210x297mm)
    A4_WIDTH = 595.0  # 约210mm
    A4_HEIGHT = 842.0  # 约297mm

    def __init__(self, input_folder: str, output_folder: Optional[str] = None, columns: int = 3):
        """
        初始化发票合并器

        Args:
            input_folder: 输入文件夹路径
            output_folder: 输出文件夹路径，默认为输入文件夹下的output子目录
            columns: 每行放置的列数，默认3列
        """
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder) if output_folder else self.input_folder / "output"
        self.columns = columns

        # 创建输出目录
        self.output_folder.mkdir(parents=True, exist_ok=True)

    def scan_pdfs(self) -> List[Path]:
        """
        递归扫描输入文件夹及其子文件夹中的所有PDF文件
        自动排除output文件夹

        Returns:
            PDF文件路径列表
        """
        # 递归查找所有PDF文件
        all_pdfs = list(self.input_folder.rglob("*.pdf"))

        # 排除output文件夹中的文件
        pdf_files = [
            pdf for pdf in all_pdfs
            if not str(pdf.relative_to(self.input_folder)).startswith("output")
        ]

        print(f"找到 {len(pdf_files)} 个PDF文件（递归扫描所有子文件夹，排除output目录）")
        return pdf_files

    def extract_invoice_id(self, pdf_path: Path) -> Optional[str]:
        """
        从文件名提取发票ID用于去重

        文件名格式：{id}-电子发票.pdf
        例如：26319130671000153108-电子发票.pdf

        Args:
            pdf_path: PDF文件路径

        Returns:
            发票ID，如果无法提取则返回None
        """
        try:
            filename = pdf_path.name

            # 查找 "-电子发票" 的位置
            if "-电子发票" in filename:
                # 分割文件名，取第一部分作为ID
                invoice_id = filename.split("-电子发票")[0]
                return invoice_id if invoice_id else None

            return None

        except Exception:
            return None

    def extract_amount_from_pdf(self, pdf_path: Path) -> float:
        """
        从PDF中提取票价金额

        Args:
            pdf_path: PDF文件路径

        Returns:
            金额（元）

        Raises:
            ValueError: 如果无法提取金额（金额为0是严重错误）
        """
        try:
            doc = fitz.open(pdf_path)
            page = doc[0]
            text = page.get_text()
            doc.close()

            # 查找票价：￥xx.xx 或 票价:￥xx.xx
            amount_patterns = [
                r'票价[：:]\s*￥\s*([\d.]+)',
                r'￥\s*([\d.]+)',
                r'金额[：:]\s*￥?\s*([\d.]+)',
                r'([\d.]+)\s*元',
            ]

            for pattern in amount_patterns:
                match = re.search(pattern, text)
                if match:
                    try:
                        amount = float(match.group(1))
                        # 验证金额合理性（高铁票价通常在几元到几千元之间）
                        if 0 < amount < 10000:
                            return amount
                    except ValueError:
                        continue

            # 无法提取金额 - 这是严重错误，必须中止
            raise ValueError(f"无法从 {pdf_path.name} 提取票价金额！")

        except ValueError:
            raise  # 重新抛出 ValueError
        except Exception as e:
            raise ValueError(f"处理 {pdf_path.name} 时出错: {e}")

    def extract_date_from_pdf(self, pdf_path: Path) -> datetime:
        """
        从PDF中提取乘车日期（智能识别，排除开票日期）

        Args:
            pdf_path: PDF文件路径

        Returns:
            提取到的日期，如果无法提取则返回文件修改时间
        """
        try:
            doc = fitz.open(pdf_path)
            page = doc[0]
            text = page.get_text()
            doc.close()

            # 查找所有日期
            date_pattern = r'(\d{4})年(\d{1,2})月(\d{1,2})日'
            matches = re.findall(date_pattern, text)

            if not matches:
                tqdm.write(f"警告: 无法从 {pdf_path.name} 提取日期，使用文件修改时间")
                timestamp = pdf_path.stat().st_mtime
                return datetime.fromtimestamp(timestamp)

            # 将所有找到的日期转换为datetime对象
            dates = []
            for match in matches:
                year, month, day = int(match[0]), int(match[1]), int(match[2])
                try:
                    date = datetime(year, month, day)
                    if 2020 <= year <= 2030:
                        dates.append(date)
                except ValueError:
                    continue

            if not dates:
                tqdm.write(f"警告: 无法从 {pdf_path.name} 提取有效日期，使用文件修改时间")
                timestamp = pdf_path.stat().st_mtime
                return datetime.fromtimestamp(timestamp)

            # 智能选择：返回最早的日期（乘车日期通常早于开票日期）
            ride_date = min(dates)

            # 验证合理性：乘车日期不应该在很久的将来
            now = datetime.now()
            if ride_date > now:
                # 如果最小日期在未来，选择第二早的日期（如果有）
                if len(dates) > 1:
                    dates_sorted = sorted(dates)
                    ride_date = dates_sorted[1] if dates_sorted[1] <= now else dates_sorted[0]

            return ride_date

        except Exception as e:
            tqdm.write(f"错误: 处理 {pdf_path.name} 时出错: {e}")
            timestamp = pdf_path.stat().st_mtime
            return datetime.fromtimestamp(timestamp)

    def group_by_month(self, pdf_files: List[Path]) -> Dict[str, List[Tuple[datetime, Path, float]]]:
        """
        按月份分组PDF文件，并去重，同时提取金额

        Args:
            pdf_files: PDF文件路径列表

        Returns:
            按月份分组的字典，key为YYYY-MM格式，value为(日期, 路径, 金额)元组列表
        """
        groups = defaultdict(list)
        seen_ids: Set[str] = set()
        duplicate_count = 0

        for pdf_path in tqdm(pdf_files, desc="分析PDF文件", unit="个"):
            # 提取发票ID用于去重
            invoice_id = self.extract_invoice_id(pdf_path)

            # 去重检查
            if invoice_id and invoice_id in seen_ids:
                tqdm.write(f"跳过重复: {pdf_path.name} (ID: {invoice_id})")
                duplicate_count += 1
                continue

            if invoice_id:
                seen_ids.add(invoice_id)

            # 提取日期、金额并分组
            date = self.extract_date_from_pdf(pdf_path)

            # 提取金额（如果失败会抛出异常）
            try:
                amount = self.extract_amount_from_pdf(pdf_path)
            except ValueError as e:
                tqdm.write("")
                tqdm.write("=" * 60)
                tqdm.write("⚠️  金额识别错误 - 程序已停止")
                tqdm.write("=" * 60)
                tqdm.write(f"\n错误: {e}")
                tqdm.write(f"\n文件: {pdf_path}")
                tqdm.write("\n原因: 无法从PDF中提取票价金额")
                tqdm.write("\n建议: ")
                tqdm.write("  1. 检查PDF文件是否损坏")
                tqdm.write("  2. 检查是否为扫描版PDF（需要OCR处理）")
                tqdm.write("  3. 手动打开PDF确认是否包含票价信息")
                tqdm.write("\n为保证报销准确性，程序已停止运行。")
                tqdm.write("请修复问题后重新运行。")
                tqdm.write("=" * 60)
                raise  # 重新抛出异常，停止程序

            month_key = date.strftime("%Y-%m")
            groups[month_key].append((date, pdf_path, amount))

        if duplicate_count > 0:
            print(f"\n已去除 {duplicate_count} 个重复文件")

        # 对每个月内的文件按票价排序（方便财务审计）
        for month_key in groups:
            groups[month_key].sort(key=lambda x: x[2])  # x[2] 是金额

        return groups

    def merge_pdfs(self, pdf_list: List[Tuple[datetime, Path, float]], output_path: Path) -> Tuple[int, float, Dict[float, int]]:
        """
        将多个PDF合并到A4纸上，保持原始宽高比

        Args:
            pdf_list: (日期, PDF路径, 金额)元组列表
            output_path: 输出文件路径

        Returns:
            (票数量, 总金额, 按票价分组的统计字典)元组
        """
        output_doc = fitz.open()

        # 计算每列的宽度
        col_width = self.A4_WIDTH / self.columns
        margin = 10  # 页边距
        spacing = 5  # 图片间距

        current_page = None
        current_col = 0
        row_height = 0
        current_y = margin

        total_count = 0
        total_amount = 0.0
        amount_groups = defaultdict(int)  # 按票价分组统计

        for _, pdf_path, amount in tqdm(pdf_list, desc="合并PDF", unit="个", leave=False):
            total_count += 1
            total_amount += amount
            amount_groups[amount] += 1  # 按票价分组计数
            try:
                src_doc = fitz.open(pdf_path)

                for page_idx in range(len(src_doc)):
                    src_page = src_doc[page_idx]
                    # 获取原始页面尺寸
                    src_rect = src_page.rect
                    src_width = src_rect.width
                    src_height = src_rect.height

                    # 计算缩放比例，保持宽高比
                    scale = (col_width - 2 * spacing) / src_width
                    scaled_width = src_width * scale
                    scaled_height = src_height * scale

                    # 检查是否需要新建页面
                    if current_page is None or (current_col == 0 and current_y + scaled_height > self.A4_HEIGHT - margin):
                        current_page = output_doc.new_page(width=self.A4_WIDTH, height=self.A4_HEIGHT)
                        current_y = margin
                        current_col = 0
                        row_height = 0

                    # 计算当前图片位置
                    x = margin + current_col * col_width + spacing
                    y = current_y

                    # 创建目标矩形
                    target_rect = fitz.Rect(x, y, x + scaled_width, y + scaled_height)

                    # 插入页面
                    current_page.show_pdf_page(target_rect, src_doc, page_idx)

                    # 更新行高（取当前行中最高的图片）
                    row_height = max(row_height, scaled_height)

                    # 移动到下一列
                    current_col += 1

                    # 如果到达行尾，换行
                    if current_col >= self.columns:
                        current_col = 0
                        current_y += row_height + spacing
                        row_height = 0

                src_doc.close()

            except Exception as e:
                tqdm.write(f"错误: 处理 {pdf_path.name} 时出错: {e}")

        # 保存合并后的PDF
        output_doc.save(output_path)
        output_doc.close()
        tqdm.write(f"✓ 已生成: {output_path.name} ({total_count}张票, {total_amount:.2f}元)")

        return total_count, total_amount, dict(amount_groups)

    def run(self):
        """运行发票合并流程"""
        print("=" * 50)
        print("发票合并打印助手")
        print("=" * 50)

        # 1. 扫描PDF文件
        pdf_files = self.scan_pdfs()
        if not pdf_files:
            print("未找到PDF文件")
            return

        # 2. 按月份分组
        print()
        groups = self.group_by_month(pdf_files)

        print("\n按月份分组结果:")
        for month_key, files in sorted(groups.items()):
            print(f"  {month_key}: {len(files)} 个文件")

        # 3. 合并PDF并收集统计信息
        print()
        statistics = []
        for month_key, files in sorted(groups.items()):
            output_path = self.output_folder / f"{month_key}.pdf"
            count, amount, amount_groups = self.merge_pdfs(files, output_path)
            statistics.append({
                'filename': f"{month_key}.pdf",
                'count': count,
                'amount': amount,
                'amount_groups': amount_groups  # 按票价分组的统计
            })

        # 4. 生成统计文件
        info_path = self.output_folder / "info.txt"
        with open(info_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("发票合并统计信息\n")
            f.write("=" * 60 + "\n\n")

            total_count = 0
            total_amount = 0.0

            for stat in statistics:
                # 写入月份汇总
                line = f"{stat['filename']:20s}  票数量: {stat['count']:3d}张  总金额: {stat['amount']:8.2f}元\n"
                f.write(line)

                # 写入详细的票价分组统计
                amount_groups = stat['amount_groups']
                if amount_groups:
                    # 按票价排序
                    for price in sorted(amount_groups.keys()):
                        ticket_count = amount_groups[price]
                        subtotal = price * ticket_count
                        f.write(f"  票价: {price:7.2f}元  ×  {ticket_count:3d}张  =  {subtotal:8.2f}元\n")

                f.write("\n")  # 每个月份后空一行

                total_count += stat['count']
                total_amount += stat['amount']

            f.write("-" * 60 + "\n")
            f.write(f"{'合计':20s}  票数量: {total_count:3d}张  总金额: {total_amount:8.2f}元\n")
            f.write("=" * 60 + "\n")

        print("\n" + "=" * 50)
        print("✓ 处理完成！")
        print(f"输出目录: {self.output_folder}")
        print(f"统计文件: {info_path.name}")
        print(f"总计: {total_count}张票, {total_amount:.2f}元")
        print("=" * 50)
