@echo off
cd /d "G:\trae\视频下载网站"

echo === Git Push Script ===
echo Current directory: %cd%
echo.

echo 1. git add .
"C:\Program Files\Git\bin\git.exe" add .

echo.
echo 2. git commit
"C:\Program Files\Git\bin\git.exe" commit -m "Fix syntax error, update version to v2.5.6"

echo.
echo 3. git push
"C:\Program Files\Git\bin\git.exe" push origin master

echo.
echo Done!
pause