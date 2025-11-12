@echo off
chcp 65001 > nul
echo ========================================
echo 手势控制系统启动脚本
echo ========================================
echo.

REM 检查conda是否安装
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误] 未检测到conda，请先安装Anaconda或Miniconda
    pause
    exit /b 1
)

REM 检查handGR环境是否存在
echo [1/5] 检查conda环境...
conda env list | findstr "handGR" >nul 2>nul
if %errorlevel% neq 0 (
    echo handGR环境不存在，正在创建...
    conda create -n handGR python=3.9 -y
    if %errorlevel% neq 0 (
        echo [错误] 创建conda环境失败
        pause
        exit /b 1
    )
    echo 环境创建成功！
) else (
    echo handGR环境已存在
)

REM 激活环境
echo.
echo [2/5] 激活conda环境...
call conda activate handGR
if %errorlevel% neq 0 (
    echo [错误] 激活环境失败
    pause
    exit /b 1
)

REM 安装后端依赖
echo.
echo [3/5] 安装后端依赖...
REM 回到项目根目录
cd /d "%~dp0.."
if exist "requirements.txt" (
    echo 安装项目依赖...
    pip install -r requirements.txt
)
if exist "gesture_control_app\backend\requirements-backend.txt" (
    echo 安装后端依赖...
    pip install -r gesture_control_app\backend\requirements-backend.txt
)

REM 安装前端依赖
echo.
echo [4/5] 检查前端依赖...
cd /d "%~dp0frontend"
if not exist "node_modules" (
    echo 安装前端依赖（首次运行需要较长时间）...
    call npm install
    if %errorlevel% neq 0 (
        echo [错误] 安装前端依赖失败
        cd /d "%~dp0"
        cd ..\..
        pause
        exit /b 1
    )
) else (
    echo 前端依赖已安装
)
cd /d "%~dp0"
cd ..\..

REM 启动服务
echo.
echo [5/5] 启动服务...
echo.
echo ========================================
echo 服务启动中...
echo 前端地址: http://localhost:3000
echo 后端地址: http://localhost:5000
echo.
echo 按 Ctrl+C 可以停止服务
echo ========================================
echo.

REM 获取当前脚本所在的完整路径
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

REM 启动后端（后台）
start "手势控制-后端服务" cmd /k "conda activate handGR && cd /d "%SCRIPT_DIR%backend" && python app.py"

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端（后台）
start "手势控制-前端服务" cmd /k "cd /d "%SCRIPT_DIR%frontend" && npm run dev"

REM 等待前端启动
timeout /t 5 /nobreak >nul

REM 打开浏览器
echo 正在打开浏览器...
start http://localhost:3000

echo.
echo 服务已启动！如需停止服务，请关闭弹出的命令行窗口。
echo.
pause

