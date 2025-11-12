#!/bin/bash

echo "========================================"
echo "手势控制系统启动脚本"
echo "========================================"
echo ""

# 检查conda是否安装
if ! command -v conda &> /dev/null; then
    echo "[错误] 未检测到conda，请先安装Anaconda或Miniconda"
    exit 1
fi

# 初始化conda
eval "$(conda shell.bash hook)"

# 检查handGR环境是否存在
echo "[1/5] 检查conda环境..."
if conda env list | grep -q "handGR"; then
    echo "handGR环境已存在"
else
    echo "handGR环境不存在，正在创建..."
    conda create -n handGR python=3.9 -y
    if [ $? -ne 0 ]; then
        echo "[错误] 创建conda环境失败"
        exit 1
    fi
    echo "环境创建成功！"
fi

# 激活环境
echo ""
echo "[2/5] 激活conda环境..."
conda activate handGR
if [ $? -ne 0 ]; then
    echo "[错误] 激活环境失败"
    exit 1
fi

# 安装后端依赖
echo ""
echo "[3/5] 安装后端依赖..."
if [ -f "requirements.txt" ]; then
    echo "安装项目依赖..."
    pip install -r requirements.txt
fi

if [ -f "gesture_control_app/backend/requirements-backend.txt" ]; then
    echo "安装后端依赖..."
    pip install -r gesture_control_app/backend/requirements-backend.txt
fi

# 安装前端依赖
echo ""
echo "[4/5] 检查前端依赖..."
cd gesture_control_app/frontend
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖（首次运行需要较长时间）..."
    npm install
    if [ $? -ne 0 ]; then
        echo "[错误] 安装前端依赖失败"
        cd ../..
        exit 1
    fi
else
    echo "前端依赖已安装"
fi
cd ../..

# 启动服务
echo ""
echo "[5/5] 启动服务..."
echo ""
echo "========================================"
echo "服务启动中..."
echo "前端地址: http://localhost:3000"
echo "后端地址: http://localhost:5000"
echo ""
echo "按 Ctrl+C 可以停止服务"
echo "========================================"
echo ""

# 启动后端（后台）
cd gesture_control_app/backend
conda activate handGR
python app.py &
BACKEND_PID=$!
cd ../..

# 等待后端启动
sleep 3

# 启动前端（后台）
cd gesture_control_app/frontend
npm run dev &
FRONTEND_PID=$!
cd ../..

# 等待前端启动
sleep 5

# 打开浏览器（根据操作系统）
echo "正在打开浏览器..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Mac OS
    open http://localhost:3000
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open http://localhost:3000
fi

echo ""
echo "服务已启动！"
echo "后端进程ID: $BACKEND_PID"
echo "前端进程ID: $FRONTEND_PID"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待用户中断
trap "echo ''; echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait

