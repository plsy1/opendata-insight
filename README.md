# OpenData Insight (ODI) - 开源数据分析与聚合平台

<div align="center">
  <img src="https://img.shields.io/badge/build-passing-brightgreen.svg" alt="Build Status" />
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python Version" />
  <img src="https://img.shields.io/badge/node-v18+-green.svg" alt="Node Version" />
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT License" />
</div>

## 📌 项目介绍

**OpenData Insight (ODI)** 是一个面向学术研究与数据聚合的开源分析看板工具。本项目旨在提供一个高扩展性、跨平台的可视化操作界面，帮助科研人员、数据分析师以及决策者从复杂的多维数据集中快速抽取核心指标、生成关联图表，并实现自动化的数据监控与预警反馈。

系统采用了现代化的前后端分离架构：
- **后端引擎**：基于 Python 构建，负责多源异构数据的接入、清洗加工、计算以及后台任务调度。
- **前端看板**：基于现代 Web 前端框架构建，提供流畅的响应式界面交互与数据可视化视图。

## 🚀 核心功能

- **多源数据接入集成**：支持统一接口管理，无缝接入关系型数据库、CSV 数据集以及第三方 RESTful API 等结构化和半结构化数据。
- **动态灵活的统计看板**：内置高度定制化的 Dashboard 组件，支持各种数据过滤、多维度搜索和趋势实时展现。
- **自动化数据收集引擎**：集成高性能的自动化网络接口和数据抓取模块，支持定时触发自动拉取、更新最新统计资源。
- **异步处理管道**：基于消息队列与定时任务处理海量数据的批处理需求，避免长时间运行阻塞数据展示。
- **用户隔离与权限控制**：提供可靠的用户鉴权架构，确保个人研究数据或敏感业务统计能得到安全的隔离访问。

## �️ 环境准备与快速启动

为保证本地计算集群和前端图形界面的成功运行，您需要准备以下环境：

- **Node.js** (v18 或更高版本)
- **NPM** 或 **Yarn**
- **Python** (3.11 及以上版本)

### 1. 克隆代码库

```bash
git clone https://github.com/your-org/opendata-insight.git
cd opendata-insight
```

### 2. 初始化前端依赖

前端可视化图表库与路由模块位于 `frontend` 目录：

```bash
cd frontend
npm install
```

### 3. 配置后端服务环境

算法引擎与定时调度服务位于 `backend` 目录。建议使用 Python 虚拟环境避免包冲突：

```bash
cd ../backend
python3 -m venv venv
source venv/bin/activate  # Windows 用户为 venv\Scripts\activate
pip install -r requirements.txt
```

### 4. 启动本地开发服务

平台提供了一个集成启动脚本，能够一键启动前后端以及所需的数据总线，便于快速进行离线调试：

```bash
# 确保终端当前处于项目根目录
./dev.sh
```

## 📚 贡献指南 (Contributing)

我们非常欢迎学术团体与开源社区的开发者参与到这个数据科学基础设施的建设中。

1. **需求反馈**：欢迎在 Issue 区报告 BUG，或提出新的数据分析维度需求。
2. **代码提交**：请 Fork 仓库并从 `main` 分支创建您的功能分支。
3. **算法扩展**：若开发了新的通用数据清洗算子或是图形渲染组件，请提交 Pull Request，并在提交信息中附带测试用例。

## � 版权声明 (License)

本项目遵循 **MIT License**。详情请参阅当前目录下的 LICENSE 文件。
