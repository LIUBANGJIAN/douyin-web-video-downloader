@echo off
cd /d "G:\trae\视频下载网站"
echo 正在添加文件...
git add .
echo 正在提交...
git commit -m "更新版本号至v2.5.5，添加详细日志记录"
echo 正在推送...
git push origin master
echo 推送完成！
pause