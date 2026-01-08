# 快速开始

本文档帮助你快速上手 invoice-merger。

## 安装

```bash
pip install invoice-merger
```

## 基本使用（推荐 - 虚拟环境友好）

```bash
python -m invoice_merger ./invoices
```

就这么简单！程序会自动：
- ✅ 扫描文件夹中的所有电子发票PDF
- ✅ 按月份分组
- ✅ 识别日期和金额
- ✅ 合并到A4纸上
- ✅ 生成统计文件

## 输出结果

运行后会在输入文件夹的 `output` 子目录生成：

```
invoices/
├── 发票1.pdf
├── 发票2.pdf
└── output/
    ├── 2025-10.pdf   ← 10月的合并PDF
    ├── 2025-11.pdf   ← 11月的合并PDF
    └── info.txt      ← 统计信息
```

## 高级用法

### 自定义输出目录

```bash
python -m invoice_merger ./invoices -o ./output
```

### 调整每行列数（默认3列）

```bash
python -m invoice_merger ./invoices -c 2  # 每行2列
python -m invoice_merger ./invoices -c 4  # 每行4列
```

### 组合使用

```bash
python -m invoice_merger ./invoices -o ./merged -c 2
```

## 为什么使用 `python -m` ？

### ✅ 优点

1. **虚拟环境无需激活**
   ```bash
   # 无需 source venv/bin/activate
   python -m invoice_merger ./data
   ```

2. **明确 Python 版本**
   ```bash
   python3.11 -m invoice_merger ./data
   python3.12 -m invoice_merger ./data
   ```

3. **跨平台一致**
   - Windows: `python -m invoice_merger`
   - Mac/Linux: `python -m invoice_merger`

4. **开发友好**
   ```bash
   pip install -e .
   python -m invoice_merger ./test_data
   ```

### 其他使用方式

如果你全局安装了包，也可以直接使用命令：

```bash
pip install invoice-merger
invoice-merger ./invoices
```

或使用 pipx（推荐用于全局工具）：

```bash
pipx install invoice-merger
invoice-merger ./invoices
```

## 常见问题

### Q: 找不到发票？
A: 确保文件名格式为 `{id}-电子发票.pdf`

### Q: 日期识别错误？
A: 程序选择最早日期作为乘车日期。如有问题，请检查PDF内容。

### Q: 金额为0？
A: PDF中无法提取金额时显示0，不影响合并功能。

### Q: 如何在其他目录运行？
A: 使用绝对路径或相对路径：
```bash
python -m invoice_merger /path/to/invoices
python -m invoice_merger ../parent/invoices
```

## 需要帮助？

- 查看完整文档：[README.md](README.md)
- 提交问题：https://github.com/luzhongqiu/invoice-merger/issues
- 部署指南：[DEPLOY.md](DEPLOY.md)
