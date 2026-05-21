import subprocess

# Git 完整路径
git_path = r'C:\Program Files\Git\bin\git.exe'
repo_path = r'G:\trae\视频下载网站'

# 执行命令并保存输出
output_lines = []

# git status
output_lines.append("=== git status ===")
result = subprocess.run([git_path, '-C', repo_path, 'status'], capture_output=True, text=True)
output_lines.append(f"输出: {result.stdout}")
if result.stderr:
    output_lines.append(f"错误: {result.stderr}")
output_lines.append(f"返回码: {result.returncode}")

# git add
output_lines.append("\n=== git add . ===")
result = subprocess.run([git_path, '-C', repo_path, 'add', '.'], capture_output=True, text=True)
output_lines.append(f"输出: {result.stdout}")
if result.stderr:
    output_lines.append(f"错误: {result.stderr}")
output_lines.append(f"返回码: {result.returncode}")

# git commit
output_lines.append("\n=== git commit ===")
result = subprocess.run([git_path, '-C', repo_path, 'commit', '-m', '更新版本号至v2.5.5，添加详细日志记录'], capture_output=True, text=True)
output_lines.append(f"输出: {result.stdout}")
if result.stderr:
    output_lines.append(f"错误: {result.stderr}")
output_lines.append(f"返回码: {result.returncode}")

# git push
output_lines.append("\n=== git push ===")
result = subprocess.run([git_path, '-C', repo_path, 'push', 'origin', 'master'], capture_output=True, text=True)
output_lines.append(f"输出: {result.stdout}")
if result.stderr:
    output_lines.append(f"错误: {result.stderr}")
output_lines.append(f"返回码: {result.returncode}")

# 写入文件
with open('git_result.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print("结果已保存到 git_result.txt")