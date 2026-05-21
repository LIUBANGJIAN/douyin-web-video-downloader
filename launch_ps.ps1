$scriptContent = @'
Write-Host "正在启动抖音视频下载器..." -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray

Write-Host "`n1. 检查 Python 环境:" -ForegroundColor Yellow
Write-Host "   Python 版本: $($(python --version 2>&1))"
Write-Host "   Python 路径: $($(Get-Command python).Source)"

Write-Host "`n2. 检查并安装依赖:" -ForegroundColor Yellow

# 检查 Flask
try {
    python -c "import flask; print('Flask 已安装')"
} catch {
    Write-Host "   Flask 未安装，正在安装..." -ForegroundColor Red
    pip install Flask==2.3.3
}

# 检查 douyin_downloader
try {
    python -c "from douyin_downloader import DouyinDownloader; print('douyin_downloader 已安装')"
} catch {
    Write-Host "   douyin_downloader 未安装，正在安装..." -ForegroundColor Red
    pip install git+https://github.com/jiji262/douyin-downloader.git
}

Write-Host "`n3. 启动服务器:" -ForegroundColor Yellow
Write-Host "   版本: v3.0.0"
Write-Host "   地址: http://localhost:8787"
Write-Host "`n   按 Ctrl+C 停止服务器"
Write-Host "=" * 50 -ForegroundColor Gray

python app.py
'@

$scriptContent | Out-File -FilePath "start_server.ps1" -Encoding UTF8

Start-Process powershell -ArgumentList "-NoExit -File start_server.ps1"