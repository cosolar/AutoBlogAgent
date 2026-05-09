#!/bin/bash

# GitHub 自动上传脚本
# 使用方法: ./scripts/push_to_github.sh <GitHub_Token> <仓库名称> [可选: 仓库描述]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查参数
if [ -z "$1" ]; then
    echo -e "${RED}错误: 缺少 GitHub Token${NC}"
    echo "使用方式: $0 <GitHub_Token> <仓库名称> [可选: 仓库描述]"
    exit 1
fi

if [ -z "$2" ]; then
    echo -e "${RED}错误: 缺少仓库名称${NC}"
    echo "使用方式: $0 <GitHub_Token> <仓库名称> [可选: 仓库描述]"
    exit 1
fi

GITHUB_TOKEN=$1
REPO_NAME=$2
REPO_DESCRIPTION=${3:-"技术热点追踪与博客生成工作流 - 自动追踪开源技术平台热点并生成专业博客"}
USERNAME=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user | grep -o '"login": "[^"]*' | cut -d'"' -f4)

echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}  GitHub 自动上传工具${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""

# 检查是否已初始化git
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}初始化 Git 仓库...${NC}"
    git init
    git checkout -b main
fi

# 配置 Git
git config user.name "$USERNAME"
git config user.email "$USERNAME@github.com"

# 创建 .gitignore（如果不存在）
if [ ! -f ".gitignore" ]; then
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

# 添加所有文件
echo -e "${YELLOW}添加文件到 Git...${NC}"
git add .

# 检查是否有文件提交
if git diff --staged --quiet; then
    echo -e "${YELLOW}没有新的文件需要提交${NC}"
else
    # 提交文件
    echo -e "${YELLOW}提交文件...${NC}"
    git commit -m "feat: 初始化技术热点追踪与博客生成项目"
fi

# 检查远程仓库是否已存在
echo -e "${YELLOW}检查远程仓库...${NC}"
REMOTE_URL="https://github.com/${USERNAME}/${REPO_NAME}.git"

# 尝试添加远程仓库
git remote remove origin 2>/dev/null || true
git remote add origin "https://${GITHUB_TOKEN}@github.com/${USERNAME}/${REPO_NAME}.git"

# 创建 GitHub 仓库（如果不存在）
echo -e "${YELLOW}创建 GitHub 仓库...${NC}"
CREATE_REPO_RESPONSE=$(curl -s -X POST \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"${REPO_NAME}\",\"description\":\"${REPO_DESCRIPTION}\",\"private\":false,\"auto_init\":false}" \
    "https://api.github.com/user/repos")

# 检查是否创建成功或已存在
if echo "$CREATE_REPO_RESPONSE" | grep -q '"full_name"'; then
    echo -e "${GREEN}✓ 仓库创建成功或已存在${NC}"
elif echo "$CREATE_REPO_RESPONSE" | grep -q '"Already exists"'; then
    echo -e "${YELLOW}⚠ 仓库已存在，将推送现有仓库${NC}"
else
    echo -e "${YELLOW}⚠ 创建仓库响应: $CREATE_REPO_RESPONSE${NC}"
fi

# 推送到 GitHub
echo -e "${YELLOW}推送到 GitHub...${NC}"
git push -u origin main --force

echo ""
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}  上传成功！${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""
echo -e "📦 仓库地址: ${GREEN}https://github.com/${USERNAME}/${REPO_NAME}${NC}"
echo ""
