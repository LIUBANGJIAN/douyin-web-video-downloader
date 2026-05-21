import os

os.chdir(r'G:\trae\视频下载网站')

print("=== 开始推送 ===")

# git status
print("\n1. git status")
os.system(r'"C:\Program Files\Git\bin\git.exe" status')

# git add
print("\n2. git add .")
os.system(r'"C:\Program Files\Git\bin\git.exe" add .')

# git commit
print("\n3. git commit")
os.system(r'"C:\Program Files\Git\bin\git.exe" commit -m "更新版本号至v2.5.5"')

# git push
print("\n4. git push")
os.system(r'"C:\Program Files\Git\bin\git.exe" push origin master')

print("\n=== 完成 ===")