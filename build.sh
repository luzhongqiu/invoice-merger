#!/bin/bash

# 发票合并打印助手 - 构建脚本

set -e

echo "=========================================="
echo "  发票合并打印助手 - 构建脚本"
echo "=========================================="

# 清理旧构建
echo ""
echo "[1/4] 清理旧构建文件..."
rm -rf build/ dist/ *.egg-info/ invoice_merger.egg-info/

# 构建包
echo ""
echo "[2/4] 构建包..."
python -m build

# 检查包
echo ""
echo "[3/4] 检查包完整性..."
twine check dist/*

# 显示构建结果
echo ""
echo "[4/4] 构建完成！"
echo ""
echo "生成的文件:"
ls -lh dist/

echo ""
echo "=========================================="
echo "  下一步操作"
echo "=========================================="
echo ""
echo "测试发布 (TestPyPI):"
echo "  twine upload --repository testpypi dist/*"
echo ""
echo "正式发布 (PyPI):"
echo "  twine upload dist/*"
echo ""
echo "=========================================="
