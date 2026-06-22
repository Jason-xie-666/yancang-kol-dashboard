@echo off
chcp 65001 >nul
title 言仓文创 KOL 内容品控工作台

echo.
echo   ╔══════════════════════════════════╗
echo   ║   言仓文创 KOL 内容品控工作台   ║
echo   ╚══════════════════════════════════╝
echo.

echo [1/3] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo   X 未找到 Python，请先安装 Python 3.8+
    echo     下载: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo   ✓ Python 已就绪

echo [2/3] 检查依赖...
pip install streamlit openai --quiet 2>nul
echo   ✓ 依赖已就绪

echo [3/3] 启动 Streamlit...
echo.
echo   浏览器将打开 http://localhost:8501
echo   按 Ctrl+C 可停止服务
echo.
start "" http://localhost:8501
streamlit run app.py --server.headless false

pause
