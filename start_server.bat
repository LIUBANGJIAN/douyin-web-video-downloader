@echo off
cd /d "G:\trae\视频下载网站"
echo 启动服务器...
python app.py > server.log 2>&1
echo 服务器已退出