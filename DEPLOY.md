# 部署指南

本文档说明如何将 invoice-merger 发布到 PyPI。

## 前置准备

### 1. 注册 PyPI 账号

- 访问 [PyPI](https://pypi.org/account/register/) 注册账号
- 访问 [TestPyPI](https://test.pypi.org/account/register/) 注册测试账号（用于测试）

### 2. 创建 API Token

在 PyPI 账号设置中创建 API Token：
- 登录 PyPI
- 进入 Account settings → API tokens
- 创建新 token，保存到安全位置

### 3. 安装发布工具

```bash
pip install build twine
```

## 发布流程

### 步骤1: 更新版本号

编辑以下文件，更新版本号：
- `pyproject.toml` 中的 `version`
- `invoice_merger/__init__.py` 中的 `__version__`
- `invoice_merger/cli.py` 中的 version 参数

### 步骤2: 清理旧构建

```bash
rm -rf build/ dist/ *.egg-info/
```

### 步骤3: 构建包

```bash
python -m build
```

这会在 `dist/` 目录生成两个文件：
- `invoice_merger-x.x.x.tar.gz` (源代码发行版)
- `invoice_merger-x.x.x-py3-none-any.whl` (Wheel 包)

### 步骤4: 检查包

```bash
twine check dist/*
```

### 步骤5: 测试发布到 TestPyPI（可选但推荐）

```bash
twine upload --repository testpypi dist/*
```

然后测试安装：

```bash
pip install --index-url https://test.pypi.org/simple/ invoice-merger
```

### 步骤6: 正式发布到 PyPI

```bash
twine upload dist/*
```

输入你的 PyPI API Token：
- Username: `__token__`
- Password: 你的 API Token（以 `pypi-` 开头）

### 步骤7: 验证安装

```bash
pip install invoice-merger
```

## 自动化脚本

为了简化流程，可以创建一个发布脚本。

### build.sh

```bash
#!/bin/bash

# 清理旧构建
rm -rf build/ dist/ *.egg-info/

# 构建包
python -m build

# 检查包
twine check dist/*

echo "构建完成！"
echo "运行以下命令发布："
echo "  测试环境: twine upload --repository testpypi dist/*"
echo "  正式环境: twine upload dist/*"
```

## 版本管理

遵循[语义化版本](https://semver.org/lang/zh-CN/)：

- `MAJOR.MINOR.PATCH`
  - MAJOR: 不兼容的 API 变更
  - MINOR: 向下兼容的新功能
  - PATCH: 向下兼容的问题修正

示例：
- `1.0.0` - 初始发布
- `1.0.1` - Bug 修复
- `1.1.0` - 新功能
- `2.0.0` - 重大更新

## 发布检查清单

在发布前确认：

- [ ] 更新版本号
- [ ] 更新 README.md 和 CHANGELOG.md
- [ ] 运行所有测试
- [ ] 更新依赖版本
- [ ] 清理临时文件
- [ ] 构建包
- [ ] 检查包完整性
- [ ] 在 TestPyPI 测试
- [ ] 创建 Git tag
- [ ] 发布到 PyPI
- [ ] 验证安装

## 常见问题

### 1. 包名已存在

如果包名已被占用，需要修改 `pyproject.toml` 中的 `name` 字段。

### 2. 上传失败

检查：
- API Token 是否正确
- 版本号是否已存在（PyPI 不允许覆盖已发布的版本）
- 网络连接是否正常

### 3. 安装后无法运行

检查：
- `pyproject.toml` 中的 `[project.scripts]` 配置是否正确
- 模块路径是否正确

## 用户使用方式

发布后，用户推荐使用以下方式（按优先级排序）：

### 1. Python 模块方式（推荐 - 适用虚拟环境）
```bash
pip install invoice-merger
python -m invoice_merger ./invoices
```

### 2. 命令行方式（全局安装）
```bash
pip install invoice-merger
invoice-merger ./invoices
```

### 3. pipx 安装（隔离环境）
```bash
pipx install invoice-merger
invoice-merger ./invoices
```

## 资源链接

- [项目主页](https://github.com/luzhongqiu/invoice-merger)
- [PyPI](https://pypi.org/)
- [TestPyPI](https://test.pypi.org/)
- [Python Packaging User Guide](https://packaging.python.org/)
- [Twine Documentation](https://twine.readthedocs.io/)
