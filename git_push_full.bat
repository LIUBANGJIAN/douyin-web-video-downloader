@echo off
cd /d "G:\trae\视频下载网站"

set GIT_PATH="C:\Program Files\Git\bin\git.exe"
if not exist %GIT_PATH% set GIT_PATH="C:\Program Files (x86)\Git\bin\git.exe"

echo 正在添加文件...
%GIT_PATH% add .

echo 正在提交...
%GIT_PATH% commit -m "更新版本号至v2.5.5，添加详细日志记录"

echo 正在推送...
%GIT_PATH% push origin master

echo 推送完成！
pause