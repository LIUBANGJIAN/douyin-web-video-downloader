import subprocess
import os

def find_git_path():
    """查找 Git 可执行文件路径"""
    # 常见的 Git 安装路径
    git_paths = [
        r'C:\Program Files\Git\bin\git.exe',
        r'C:\Program Files (x86)\Git\bin\git.exe',
        r'C:\Git\bin\git.exe',
    ]
    
    for path in git_paths:
        if os.path.exists(path):
            return path
    
    # 尝试从 PATH 环境变量中查找
    try:
        result = subprocess.run(['where', 'git'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout:
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    
    return None

def run_command(cmd, cwd=None):
    print(f"执行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    print(f"输出: {result.stdout}")
    if result.stderr:
        print(f"错误: {result.stderr}")
    return result.returncode == 0

if __name__ == '__main__':
    repo_path = r'G:\trae\视频下载网站'
    os.chdir(repo_path)
    
    print("=== 开始推送代码到 GitHub ===")
    
    # 查找 Git 路径
    git_path = find_git_path()
    if git_path:
        print(f"找到 Git: {git_path}")
        # 设置 git 命令
        git_cmd = f'"{git_path}"'
    else:
        print("警告: 未找到 Git，使用系统 PATH 中的 git")
        git_cmd = "git"
    
    # git status
    print("\n1. 检查状态:")
    run_command(f"{git_cmd} status", repo_path)
    
    # git add
    print("\n2. 添加文件:")
    if not run_command(f"{git_cmd} add .", repo_path):
        print("git add 失败")
        exit(1)
    
    # git commit
    print("\n3. 提交更改:")
    if not run_command(f'{git_cmd} commit -m "更新版本号至v2.5.5，添加详细日志记录"', repo_path):
        print("git commit 失败")
        exit(1)
    
    # git push
    print("\n4. 推送到远程仓库:")
    if run_command(f"{git_cmd} push origin master", repo_path):
        print("\n✅ 推送成功！")
    else:
        print("\n❌ 推送失败")
        exit(1)