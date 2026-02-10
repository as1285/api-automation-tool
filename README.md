# 接口自动化测试桌面工具

## 项目简介

这是一个使用Python和PyQt5开发的接口自动化测试桌面工具，支持从Swagger/OpenAPI文档生成接口测试用例，并提供完整的测试执行和报告生成功能。

## 功能特性

### 1. 接口文档导入
- 支持导入Swagger/OpenAPI 2.0和3.0格式文档
- 支持从URL或本地文件导入
- 自动解析文档并提取接口信息

### 2. 测试用例生成
- 根据接口文档自动生成测试用例
- 支持自定义测试用例参数
- 可视化管理测试用例

### 3. 测试执行
- 支持批量执行测试用例
- 可配置基础URL
- 实时显示测试执行结果
- 详细的错误信息展示

### 4. 测试报告
- 生成HTML格式的测试报告
- 生成JSON格式的测试报告
- 包含详细的测试结果和统计信息
- 可导出报告文件

## 技术栈

- **编程语言**: Python 3.7+
- **GUI框架**: PyQt5
- **HTTP请求**: requests
- **YAML解析**: PyYAML
- **测试框架**: pytest
- **测试报告**: allure-pytest
- **环境管理**: python-dotenv

## 安装说明

### 方法1: 使用虚拟环境

```bash
# 克隆仓库
git clone https://github.com/as1285/api-automation-tool.git
cd api-automation-tool

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 方法2: 直接安装

```bash
# 克隆仓库
git clone https://github.com/as1285/api-automation-tool.git
cd api-automation-tool

# 直接安装依赖
pip install -r requirements.txt
```

## 使用方法

### 启动工具

```bash
# 使用虚拟环境
venv\Scripts\python.exe main.py

# 或直接运行
python main.py
```

### 使用流程

1. **文档导入**:
   - 在"文档导入"标签页中输入Swagger文档URL或本地文件路径
   - 点击"解析文档"按钮
   - 查看解析结果

2. **生成测试用例**:
   - 切换到"测试用例"标签页
   - 点击"生成测试用例"按钮
   - 查看生成的测试用例列表

3. **执行测试**:
   - 切换到"测试执行"标签页
   - 输入基础URL
   - 点击"执行测试"按钮
   - 查看测试执行结果

4. **查看报告**:
   - 切换到"测试报告"标签页
   - 点击"生成HTML报告"或"生成JSON报告"按钮
   - 查看报告内容
   - 保存报告文件

## 项目结构

```
api-automation-tool/
├── main.py              # 应用入口
├── README.md            # 项目说明
├── requirements.txt     # 依赖配置
└── app/
    ├── __init__.py
    ├── gui/             # GUI界面模块
    │   ├── __init__.py
    │   └── main_window.py  # 主窗口实现
    ├── core/            # 核心功能模块
    │   ├── __init__.py
    │   ├── doc_parser.py        # 接口文档解析器
    │   ├── test_case_generator.py  # 测试用例生成器
    │   ├── test_executor.py     # 测试执行器
    │   └── report_generator.py  # 报告生成器
    ├── utils/           # 工具函数模块
    │   └── __init__.py
    └── models/          # 数据模型模块
        └── __init__.py
```

## 核心模块说明

### 1. 文档解析器 (doc_parser.py)
- 解析Swagger/OpenAPI文档
- 提取接口信息，包括路径、方法、参数等

### 2. 测试用例生成器 (test_case_generator.py)
- 根据接口信息生成测试用例
- 支持自动填充默认参数

### 3. 测试执行器 (test_executor.py)
- 执行HTTP请求
- 处理响应和错误
- 验证测试结果

### 4. 报告生成器 (report_generator.py)
- 生成HTML和JSON格式的测试报告
- 计算测试统计信息

## 示例

### 导入Swagger文档

1. 输入Swagger文档URL: `https://petstore.swagger.io/v2/swagger.json`
2. 点击"解析文档"按钮
3. 查看解析结果

### 生成测试用例

1. 切换到"测试用例"标签页
2. 点击"生成测试用例"按钮
3. 查看生成的测试用例列表

### 执行测试

1. 输入基础URL: `https://petstore.swagger.io/v2`
2. 点击"执行测试"按钮
3. 查看测试执行结果

### 查看报告

1. 切换到"测试报告"标签页
2. 点击"生成HTML报告"按钮
3. 查看生成的测试报告

## 配置选项

### 环境变量

可以在项目根目录创建`.env`文件，配置以下环境变量：

```
# 基础URL
BASE_URL=https://api.example.com

# 超时设置
TIMEOUT=30

# 重试次数
RETRY_COUNT=3
```

### 自定义配置

可以修改`app/core/config.py`文件中的配置项：

- `DEFAULT_TIMEOUT`: 默认超时时间
- `DEFAULT_RETRY_COUNT`: 默认重试次数
- `DEFAULT_HEADERS`: 默认HTTP头部

## 开发指南

### 代码风格

- 遵循PEP 8代码风格
- 使用4个空格缩进
- 类名使用驼峰命名法
- 函数和变量名使用下划线分隔

### 测试

```bash
# 运行测试
python -m pytest

# 运行测试并生成allure报告
python -m pytest --alluredir=./allure-results

# 查看allure报告
allure serve ./allure-results
```

### 打包

```bash
# 使用PyInstaller打包
pip install pyinstaller
pyinstaller --onefile --windowed --name api-automation-tool main.py
```

## 常见问题

### 1. 无法解析Swagger文档

- 检查文档格式是否正确
- 检查网络连接是否正常
- 检查文档URL是否可访问

### 2. 测试执行失败

- 检查基础URL是否正确
- 检查网络连接是否正常
- 检查接口是否正常运行
- 检查测试用例参数是否正确

### 3. 报告生成失败

- 检查测试执行是否完成
- 检查测试结果是否存在
- 检查文件权限是否正确

## 贡献

欢迎贡献代码！请按照以下步骤：

1. Fork本仓库
2. 创建特性分支: `git checkout -b feature/AmazingFeature`
3. 提交更改: `git commit -m 'Add some AmazingFeature'`
4. 推送到分支: `git push origin feature/AmazingFeature`
5. 打开Pull Request

## 许可证

本项目采用MIT许可证 - 详见LICENSE文件

## 联系方式

- **GitHub**: [https://github.com/as1285](https://github.com/as1285)
- **Email**: 498771018@qq.com

## 更新日志

### v1.0.0 (2026-02-10)
- 初始版本
- 支持Swagger文档导入
- 支持测试用例生成
- 支持测试执行
- 支持HTML和JSON报告生成

---

**感谢使用接口自动化测试桌面工具！** 🚀