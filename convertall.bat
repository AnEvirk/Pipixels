setlocal enabledelayedexpansion
echo >find
dir /B *.ui >> find
set temp_path=%~dp0
cd C:\Users\gyxep\AppData\Local\Programs\Python\Python35-32\Scripts
for /F "delims=." %%i in (%temp_path%\find) do (
pyuic5 %temp_path%\%%i.ui > %temp_path%\%%i.py
)
pause