import subprocess
import os
import sys
import tempfile

def run_download_test():
    # 设置环境变量
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['LANG'] = 'en_US.UTF-8'
    
    # 测试命令
    url = "https://v.douyin.com/MpeyIZyxMTA/"
    download_path = "G:/trae/视频下载网站/downloads"
    
    # 创建临时配置文件
    config_content = f'''link:
  - "{url}"
path: "{download_path}"
database: false
browser_fallback:
  enabled: true
  headless: true
'''
    
    temp_config_path = tempfile.mktemp(suffix='.yml')
    with open(temp_config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    try:
        print(f"配置文件内容:\n{config_content}")
        print(f"\n配置文件路径: {temp_config_path}")
        print(f"\n开始运行下载命令...")
        
        result = subprocess.run(
            ['douyin-dl', '-c', temp_config_path, '-v'],
            capture_output=True,
            timeout=120,
            env=env
        )
        
        print(f"\n返回码: {result.returncode}")
        print(f"\n标准输出:")
        try:
            print(result.stdout.decode('utf-8'))
        except:
            print(result.stdout)
        
        print(f"\n错误输出:")
        try:
            print(result.stderr.decode('utf-8'))
        except:
            print(result.stderr)
            
    finally:
        os.unlink(temp_config_path)

if __name__ == "__main__":
    run_download_test()
