import subprocess
import sys

# 执行命令并保存输出
result = subprocess.run(
    ['git', 'push', 'origin', 'master'],
    cwd=r'G:\trae\视频下载网站',
    capture_output=True,
    text=True
)

# 写入文件
with open('push_result.txt', 'w', encoding='utf-8') as f:
    f.write("标准输出:\n")
    f.write(result.stdout)
    f.write("\n\n错误输出:\n")
    f.write(result.stderr)
    f.write("\n\n返回码:\n")
    f.write(str(result.returncode))

print("已保存推送结果到 push_result.txt")