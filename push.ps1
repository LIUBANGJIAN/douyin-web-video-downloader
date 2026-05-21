$ErrorActionPreference = 'Continue'

Write-Host "=== 开始推送至 GitHub ===" -ForegroundColor Green

# 添加所有文件
Write-Host "`n1. git add ." -ForegroundColor Cyan
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "git add 失败" -ForegroundColor Red
    exit 1
}

# 提交
Write-Host "`n2. git commit" -ForegroundColor Cyan
git commit -m "更新版本号至v2.5.5，添加详细日志记录以诊断解析问题"
if ($LASTEXITCODE -ne 0) {
    Write-Host "git commit 失败" -ForegroundColor Red
    exit 1
}

# 推送
Write-Host "`n3. git push" -ForegroundColor Cyan
git push origin master
if ($LASTEXITCODE -ne 0) {
    Write-Host "git push 失败" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== 推送成功 ===" -ForegroundColor Green