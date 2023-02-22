:: Check for Python Installation
python --version 2>NUL
if errorlevel 1 goto errorNoPython

:: Reaching here means Python is installed.
:: Execute stuff...

:: Once done, exit the batch file -- skips executing the errorNoPython section
goto:library
goto:eof

:errorNoPython
echo.
echo Error^: Python not installed
echo Start install......
curl -O https://www.python.org/ftp/python/3.10.0/python-3.10.0.exe
python-3.10.0.exe /quiet InstallAllUsers=1 PrependPath=1
setx PATH "%PATH%;C:\Python27\Scripts"
goto:library
goto:eof

:library
echo "install numpy";
pip3 install numpy;
echo "install PIL";
pip3 install PIL;
echo "install pyautogui";
pip3 install pyautogui;
echo "install reportlab";
pip3 install reportlab;
echo "install glob";
pip3 install glob2;
echo "install schedule";
pip install schedule;
