"""
发票合并打印助手

将电子发票按月份自动分组并合并到A4纸上，便于打印报销。
"""

from .merger import InvoiceMerger

__version__ = "1.1.0"
__author__ = "Your Name"
__all__ = ["InvoiceMerger"]
