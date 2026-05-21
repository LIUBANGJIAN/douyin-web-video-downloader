import subprocess
import sys

# 安装并获取输出
result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'git+https://github.com/jiji262/douyin-downloader.git'], 
                       capture_output=True, text=True)

# 写入日志文件
with open('pip_install_log.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 60 + "\n")
    f.write("PIP 安装日志\n")
    f.write("=" * 60 + "\n\n")
    f.write("STDOUT:\n")
    f.write(result.stdout)
    f.write("\n\nSTDERR:\n")
    f.write(result.stderr)
    f.write("\n\n返回码: " + str(result.returncode))

print("安装完成，日志已写入 pip_install_log.txt")