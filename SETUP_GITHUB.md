# 🚀 GitHub 设置指南

本指南将帮助您将 AIMovie Cloud 项目配置到 GitHub 上。

## 📋 前提条件

### 1. 安装 Git
如果您还没有安装 Git，请按照以下步骤：

**Windows:**
- 下载并安装 [Git for Windows](https://git-scm.com/download/win)
- 或使用 Chocolatey: `choco install git`
- 或使用 Winget: `winget install Git.Git`

**macOS:**
- 使用 Homebrew: `brew install git`
- 或下载 [Git for macOS](https://git-scm.com/download/mac)

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install git
```

### 2. 配置 Git
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. 创建 GitHub 账户
如果您还没有 GitHub 账户，请访问 [github.com](https://github.com) 注册。

## 🔧 项目设置

### 1. 初始化本地仓库
```bash
# 在项目根目录执行
git init
git add .
git commit -m "feat: initial commit - AIMovie Cloud v1.0"
```

### 2. 创建 GitHub 仓库

#### 方法 A: 通过 GitHub 网站
1. 访问 [github.com](https://github.com)
2. 点击右上角的 "+" 按钮
3. 选择 "New repository"
4. 填写仓库信息：
   - **Repository name**: `aimovie-cloud`
   - **Description**: `AI-powered video narration generator using cloud services`
   - **Visibility**: Public 或 Private
   - **不要**勾选 "Initialize this repository with a README"
5. 点击 "Create repository"

#### 方法 B: 使用 GitHub CLI (可选)
```bash
# 安装 GitHub CLI
# Windows: winget install GitHub.cli
# macOS: brew install gh
# Linux: 参考 https://cli.github.com/

# 登录并创建仓库
gh auth login
gh repo create aimovie-cloud --public --description "AI-powered video narration generator using cloud services"
```

### 3. 连接本地仓库到 GitHub
```bash
# 添加远程仓库 (替换 YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/aimovie-cloud.git

# 推送代码
git branch -M main
git push -u origin main
```

## 🔒 安全设置

### 1. 保护主分支
在 GitHub 仓库页面：
1. 进入 Settings → Branches
2. 点击 "Add rule"
3. 设置 Branch name pattern: `main`
4. 勾选以下选项：
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Include administrators

### 2. 设置 Secrets (用于 CI/CD)
在 GitHub 仓库页面：
1. 进入 Settings → Secrets and variables → Actions
2. 添加以下 secrets (如果需要在 CI 中测试):
   - `QWEN_API_KEY`: 通义千问 API 密钥
   - `ALIYUN_ACCESS_KEY_ID`: 阿里云访问密钥 ID
   - `ALIYUN_ACCESS_KEY_SECRET`: 阿里云访问密钥
   - `BAIDU_API_KEY`: 百度 AI API 密钥
   - `BAIDU_SECRET_KEY`: 百度 AI 密钥

## 📝 仓库配置

### 1. 启用 GitHub Pages (可选)
如果您想托管文档：
1. 进入 Settings → Pages
2. Source 选择 "Deploy from a branch"
3. Branch 选择 `main` 和 `/docs` 文件夹
4. 点击 Save

### 2. 配置 Issues 和 Discussions
1. 进入 Settings → General
2. 在 Features 部分：
   - ✅ Issues
   - ✅ Discussions (推荐)
   - ✅ Wiki (可选)

### 3. 添加 Topics
在仓库主页点击设置图标，添加以下 topics：
- `ai`
- `video-processing`
- `cloud-computing`
- `tts`
- `narration`
- `fastapi`
- `streamlit`
- `python`

## 🏷️ 创建第一个 Release

### 1. 创建标签
```bash
git tag -a v1.0.0 -m "Release v1.0.0: Initial cloud version"
git push origin v1.0.0
```

### 2. 在 GitHub 创建 Release
1. 进入仓库的 Releases 页面
2. 点击 "Create a new release"
3. 选择标签 `v1.0.0`
4. 填写 Release 信息：
   - **Release title**: `v1.0.0 - AIMovie Cloud Initial Release`
   - **Description**: 从 CHANGELOG.md 复制相关内容
5. 点击 "Publish release"

## 🔄 开发工作流

### 1. 分支策略
```bash
# 创建功能分支
git checkout -b feature/new-feature

# 开发完成后
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature

# 在 GitHub 创建 Pull Request
```

### 2. 提交消息规范
使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：
- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式化
- `refactor:` 代码重构
- `test:` 添加测试
- `chore:` 维护任务

### 3. Pull Request 流程
1. 创建功能分支
2. 开发并测试
3. 提交 Pull Request
4. 代码审查
5. 合并到主分支

## 🤝 协作设置

### 1. 添加协作者
在 Settings → Manage access 中邀请协作者。

### 2. 设置团队权限
- **Admin**: 完全访问权限
- **Write**: 可以推送代码
- **Read**: 只读访问

### 3. 代码审查规则
- 至少需要 1 个审查者批准
- 所有 CI 检查必须通过
- 分支必须是最新的

## 📊 监控和分析

### 1. 启用 Insights
GitHub 会自动提供以下分析：
- 代码频率
- 贡献者活动
- 流量统计
- 依赖关系图

### 2. 设置通知
在 Settings → Notifications 中配置：
- Issues 和 Pull Requests
- 安全警报
- 依赖更新

## 🔧 自动化工具

### 1. Dependabot
在 `.github/dependabot.yml` 中配置自动依赖更新：
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

### 2. 代码扫描
启用 GitHub 的安全功能：
- Code scanning
- Secret scanning
- Dependency review

## 📚 文档维护

### 1. README 徽章
在 README.md 中添加状态徽章：
```markdown
[![CI](https://github.com/YOUR_USERNAME/aimovie-cloud/workflows/CI/badge.svg)](https://github.com/YOUR_USERNAME/aimovie-cloud/actions)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
```

### 2. 保持文档更新
- 定期更新 README.md
- 维护 CHANGELOG.md
- 更新 API 文档

## 🎉 完成！

现在您的 AIMovie Cloud 项目已经完全配置好 GitHub 了！您可以：

1. 🔄 开始协作开发
2. 🚀 使用 CI/CD 自动化
3. 📊 跟踪项目进展
4. 🤝 接受社区贡献
5. 📦 发布新版本

如有任何问题，请查看 [GitHub 文档](https://docs.github.com/) 或在项目中创建 Issue。 