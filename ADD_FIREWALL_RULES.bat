@echo off
echo Adding Windows Firewall Rules for Store Navigator...
echo.
echo This script needs to run as Administrator
echo.
pause

netsh advfirewall firewall add rule name="Frontend Web Server (8080)" dir=in action=allow protocol=TCP localport=8080
netsh advfirewall firewall add rule name="Backend API (8040)" dir=in action=allow protocol=TCP localport=8040

echo.
echo Done! Firewall rules added.
echo.
echo You can now access the app from your iPhone at:
echo http://172.20.10.2:8080
echo.
pause
