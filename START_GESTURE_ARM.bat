@echo off
setlocal

title Gesture Controlled Robotic Arm

echo ==========================================
echo   GESTURE CONTROLLED ROBOTIC ARM
echo ==========================================
echo.
echo Starting ROS 2 Jazzy in WSL...
echo.

REM Start ROS 2 + RViz in WSL
start "ROS 2 + RViz" wsl.exe -d Ubuntu-24.04 bash -lc "cd ~/gesture-robotic-arm && ./scripts/run_live_ros2.sh"

echo Waiting for ROS 2 UDP receiver...
timeout /t 5 /nobreak >nul

REM Get current WSL IP address
for /f "tokens=1" %%I in ('wsl.exe -d Ubuntu-24.04 hostname -I') do set WSL_IP=%%I

echo WSL IP: %WSL_IP%
echo.
echo Starting Windows webcam + MediaPipe...
echo.

cd /d "%~dp0"

.\venv\Scripts\python.exe .\python\run_udp.py --host %WSL_IP% --port 5005

echo.
echo Gesture application stopped.
pause