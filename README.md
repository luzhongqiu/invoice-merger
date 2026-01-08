# 发票合并打印助手 (Invoice Merger)

[![PyPI version](https://badge.fury.io/py/invoice-merger.svg)](https://badge.fury.io/py/invoice-merger)
[![Python Version](https://img.shields.io/pypi/pyversions/invoice-merger.svg)](https://pypi.org/project/invoice-merger/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

电子发票按月份自动分组并合并到A4纸上，便于打印报销。

专为中国高铁电子发票设计，支持自动识别乘车日期、票价金额，按月份分组合并，生成统计报表。

## 功能特点

- ✅ 自动扫描文件夹中的PDF发票（支持递归扫描子文件夹）
- ✅ 智能识别乘车日期（基于最早日期原则）
- ✅ 智能识别票价金额并自动汇总
- ✅ 基于发票号码自动去重
- ✅ 按月份自动分组
- ✅ 同一月份内按时间从小到大排序
- ✅ 生成统计文件（票数量、总金额）
- ✅ 保持原始宽高比，不扭曲图片
- ✅ 可配置每行列数（默认3列）
- ✅ 自动计算行数，充分利用A4纸空间
- ✅ 实时进度显示

## 安装

### 方式一：从 PyPI 安装（推荐）

```bash
pip install invoice-merger
```

### 方式二：从源码安装

```bash
git clone https://github.com/luzhongqiu/invoice-merger.git
cd invoice-merger
pip install -e .
```

## 使用方法

### 基本用法（推荐）

使用 Python 模块方式运行（**适用于虚拟环境**）：

```bash
python -m invoice_merger <输入文件夹路径>
```

例如：
```bash
python -m invoice_merger ./invoices
```

输出文件将保存在输入文件夹的 `output` 子目录中。

### 命令行方式

如果全局安装（使用 `pip install` 或 `pipx install`），也可以直接使用命令：

```bash
invoice-merger ./invoices
```

### 高级选项

```bash
python -m invoice_merger <输入文件夹> -o <输出文件夹> -c <列数>
```

参数说明：
- `-o, --output`: 指定输出文件夹路径（可选，默认为输入文件夹下的output目录）
- `-c, --columns`: 每行放置的列数（可选，默认为3列）
- `-v, --version`: 显示版本信息
- `-h, --help`: 显示帮助信息

### 示例

1. 使用默认设置（3列）：
   ```bash
   python -m invoice_merger ./my_invoices
   ```

2. 自定义输出目录：
   ```bash
   python -m invoice_merger ./my_invoices -o ./merged_pdfs
   ```

3. 自定义列数（如每行2列）：
   ```bash
   python -m invoice_merger ./my_invoices -c 2
   ```

4. 同时指定输出目录和列数：
   ```bash
   python -m invoice_merger ./my_invoices -o ./output -c 4
   ```

5. 查看帮助信息：
   ```bash
   python -m invoice_merger --help
   ```

## 输出格式

### PDF文件
- 输出文件按月份命名，格式为 `YYYY-MM.pdf`
- 例如：`2025-10.pdf`, `2025-11.pdf`
- 同一月份内的发票按时间顺序排列

### 统计文件（info.txt）
程序会自动生成 `info.txt` 统计文件，包含每个月的汇总信息：

```
============================================================
发票合并统计信息
============================================================

2025-10.pdf           票数量:  35张  总金额:  1285.00元
2025-11.pdf           票数量:  38张  总金额:  1533.00元
2025-12.pdf           票数量:  46张  总金额:  1784.00元
2026-01.pdf           票数量:   1张  总金额:     0.00元

------------------------------------------------------------
合计                    票数量: 120张  总金额:  4602.00元
============================================================
```

**说明**：
- 每行显示一个PDF文件的统计信息
- 包含票数量和总金额
- 最后一行显示所有月份的总计
- 便于报销时核对金额

## 支持的日期格式

程序会自动识别PDF中的以下日期格式：
- `2025年10月15日` 或 `2025-10-15`
- `2025.10.15`
- `10/15/2025`

如果无法从PDF内容中提取日期，将使用文件的修改时间作为日期。

## 工作原理

1. **扫描阶段**：递归扫描指定文件夹及所有子文件夹中的PDF文件（自动排除output目录）
2. **识别阶段**：从PDF文本内容中提取日期、发票号码和金额信息
3. **去重阶段**：根据发票号码自动去除重复文件
4. **分组阶段**：按月份分组，组内按时间排序
5. **合并阶段**：
   - 按指定列数排列
   - 计算缩放比例，保持原始宽高比
   - 自动计算行数，充分利用A4纸空间
   - 当前页放不下时自动创建新页面
   - 同时统计每个月的票数量和总金额
6. **统计阶段**：生成info.txt文件，汇总所有月份的统计信息

## 日期识别逻辑

程序专门针对**高铁电子发票**设计，使用智能算法识别乘车日期：

### 识别原理

1. **提取所有日期**：从PDF中查找所有 `YYYY年MM月DD日` 格式的日期
2. **智能选择**：选择**最早的日期**作为乘车日期
3. **原理依据**：开票时间总是晚于或等于乘车时间

### 示例

```
PDF内容包含两个日期：
  - 2025年10月31日  ← 乘车日期
  - 2026年01月07日  ← 开票日期

程序选择：2025-10-31（最早日期）
```

### 重要假设

⚠️ **本程序假设开票日期晚于乘车日期**

这个假设适用于绝大多数场景，因为：
- ✅ 高铁票通常在乘车后统一开票
- ✅ 即使乘车当天开票，日期也不会早于乘车日期
- ❌ **不适用**：如果PDF中包含其他更早的日期（如打印日期、系统生成日期等），可能导致识别错误

### 去重机制

程序通过文件名自动去重：
- 从文件名中提取发票ID（格式：`{id}-电子发票.pdf`）
- 如果发现相同ID，自动跳过
- 避免重复下载的文件被合并多次

**示例**：
```
26319130671000153108-电子发票.pdf         ✓ 保留
26319130671000153108-电子发票 (1).pdf    ✗ 跳过（重复）
```

## 金额识别逻辑

程序自动从PDF中提取票价信息：

### 识别方法

- 查找 `票价:￥xx.xx` 格式的金额
- 验证金额合理性（0-10000元范围）
- 按月份自动汇总

### 金额统计

- 每个月的PDF文件独立统计
- 生成 `info.txt` 包含详细的金额汇总
- 显示每个月的票数和总金额
- 最后显示所有月份的合计

### ⚠️ 重要安全保护机制

**为保证报销准确性，程序内置了金额识别保护机制：**

✅ **如果无法识别票价金额，程序会立即报错并停止运行**

这是有意设计的安全措施，因为：
1. **金额=0是严重错误**：报销金额不准确会造成财务问题
2. **及时发现问题**：在合并前就发现问题，避免打印后才发现错误
3. **保证报销准确**：只有所有金额都正确识别，才允许生成报销文件

**当遇到金额识别错误时：**
```
⚠️  金额识别错误 - 程序已停止
错误: 无法从 xxx.pdf 提取票价金额！
建议:
  1. 检查PDF文件是否损坏
  2. 检查是否为扫描版PDF（需要OCR处理）
  3. 手动打开PDF确认是否包含票价信息
```

**这意味着：**
- ✅ 所有生成的 `info.txt` 中的金额都是准确的
- ✅ 可以放心用于报销，无需担心金额错误
- ✅ 程序不会"悄悄"地把金额设为0

## 目录结构示例

程序支持递归扫描，可以处理包含子文件夹的复杂目录结构：

```
my_invoices/
├── 2025年10月/
│   ├── 发票1.pdf
│   └── 发票2.pdf
├── 2025年11月/
│   ├── 发票3.pdf
│   └── 发票4.pdf
├── 其他发票/
│   └── 发票5.pdf
└── output/           ← 输出目录（自动排除扫描）
    ├── 2025-10.pdf    (合并后的PDF)
    ├── 2025-11.pdf    (合并后的PDF)
    └── info.txt       (统计信息)
```

**说明**：
- 程序会自动递归扫描所有子文件夹
- 无需手动整理文件夹结构
- output 目录会被自动排除，避免重复处理
- info.txt 自动生成，包含所有月份的统计汇总

## 注意事项

- 确保输入的PDF文件包含文本内容（非纯图片扫描）
- 如果是扫描版PDF，建议先进行OCR处理
- 程序会在处理过程中输出详细的日志信息
- 如果某个PDF无法提取日期，会使用文件修改时间并给出警告

## 技术栈

- Python 3.8+
- PyMuPDF (fitz) - PDF处理库
- tqdm - 进度条显示

## FAQ

### 为什么推荐使用 `python -m invoice_merger` 方式？

1. **虚拟环境友好**：在虚拟环境中无需激活即可使用
2. **跨平台一致**：Windows/Mac/Linux 都是相同的命令
3. **明确 Python 版本**：可以指定使用哪个 Python（如 `python3.11 -m invoice_merger`）
4. **开发更方便**：使用 `pip install -e .` 安装后立即可用

### 如何在任何地方使用？

```bash
# 方式1: 使用 python -m（推荐）
python -m invoice_merger /path/to/invoices

# 方式2: 全局安装后使用命令
pip install invoice-merger
invoice-merger /path/to/invoices

# 方式3: pipx 隔离安装
pipx install invoice-merger
invoice-merger /path/to/invoices
```

### 开发时如何测试？

```bash
# 1. 克隆仓库
git clone https://github.com/luzhongqiu/invoice-merger.git
cd invoice-merger

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装开发版
pip install -e .

# 4. 测试运行
python -m invoice_merger ./test_data
```

## 贡献

欢迎提交 Issue 和 Pull Request！

项目地址：https://github.com/luzhongqiu/invoice-merger

## 许可证

MIT License
