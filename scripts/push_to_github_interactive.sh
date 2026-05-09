#!/bin/bash

# ==========================================
# 交互式 GitHub 上传脚本
# ==========================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     GitHub 一键上传工具 v2.0              ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════╝${NC}"
echo ""

# 检查 GitHub CLI
if command -v gh &> /dev/null; then
    echo -e "${GREEN}✓${NC} GitHub CLI 已安装"
    GH_AUTH=$(gh auth status 2>&1)
    if echo "$GH_AUTH" | grep -q "Logged in"; then
        echo -e "${GREEN}✓${NC} GitHub CLI 已登录"
        USE_GH_CLI=true
    else
        echo -e "${YELLOW}⚠${NC} GitHub CLI 未登录，将使用 Token 方式"
        USE_GH_CLI=false
    fi
else
    echo -e "${YELLOW}⚠${NC} GitHub CLI 未安装"
    USE_GH_CLI=false
fi

# 获取仓库名称
DEFAULT_REPO_NAME=$(basename $(pwd))
echo ""
echo -e "${BOLD}📦 仓库设置${NC}"
read -p "仓库名称 [${DEFAULT_REPO_NAME}]: " REPO_NAME
REPO_NAME=${REPO_NAME:-$DEFAULT_REPO_NAME}

read -p "仓库描述: " REPO_DESCRIPTION
REPO_DESCRIPTION=${REPO_DESCRIPTION:-"技术热点追踪与博客生成工作流"}

# 初始化 Git（如果需要）
if [ ! -d ".git" ]; then
    echo ""
    echo -e "${YELLOW}初始化 Git 仓库...${NC}"
    git init
    git checkout -b main
fi

# 配置 Git 用户信息
echo ""
echo -e "${BOLD}👤 Git 用户配置${NC}"
read -p "GitHub 用户名: " GIT_USERNAME
read -p "GitHub 邮箱: " GIT_EMAIL

git config user.name "$GIT_USERNAME"
git config user.email "$GIT_EMAIL"

# 创建 .gitignore（如果不存在）
if [ ! -f ".gitignore" ]; then
    echo ""
    echo -e "${YELLOW}创建 .gitignore...${NC}"
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local
EOF
fi

# 添加文件并提交
echo ""
echo -e "${BOLD}📝 提交文件${NC}"
git add .
git commit -m "feat: 初始化技术热点追踪与博客生成项目"

# 推送到 GitHub
echo ""
if [ "$USE_GH_CLI" = true ]; then
    echo -e "${BLUE}使用 GitHub CLI 创建仓库...${NC}"
    gh repo create "$REPO_NAME" --public --description "$REPO_DESCRIPTION" --source=. --push
    echo ""
    echo -e "${GREEN}✓ 上传成功！${NC}"
    echo -e "📦 仓库地址: ${GREEN}https://github.com/${GIT_USERNAME}/${REPO_NAME}${NC}"
else
    echo -e "${BOLD}🔐 GitHub Token${NC}"
    echo -e "请获取 GitHub Personal Access Token:"
    echo -e "  → ${BLUE}https://github.com/settings/tokens/new${NC}"
    echo -e "  → 勾选 ${YELLOW}repo${NC} 权限"
    echo ""
    read -sp "请输入 Token: " GITHUB_TOKEN
    echo ""

    # 创建远程仓库
    echo -e "${YELLOW}创建远程仓库...${NC}"
    curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"${REPO_NAME}\",\"description\":\"${REPO_DESCRIPTION}\",\"public\":true}" \
        "https://api.github.com/user/repos" | grep -q "full_name" && \
        echo -e "${GREEN}✓ 仓库创建成功${NC}" || \
        echo -e "${YELLOW}⚠ 仓库可能已存在${NC}"

    # 添加远程仓库并推送
    git remote remove origin 2>/dev/null || true
    git remote add origin "https://${GIT_USERNAME}:${GITHUB_TOKEN}@github.com/${GIT_USERNAME}/${REPO_NAME}.git"
    git push -u origin main --force

    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║           上传成功！ 🎉                       ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "📦 仓库地址: ${GREEN}https://github.com/${GIT_USERNAME}/${REPO_NAME}${NC}"
fi

echo ""
