@echo off
chcp 65001
cd /d "G:\trae\视频下载网站"

echo === 测试 douyin-downloader 库 ===
python test_douyin_downloader.py
echo.

echo === Git Push ===
git add .
git commit -m "全面转向 douyin-downloader 库，版本 v3.0.0"
git push origin master

echo 完成!
pause