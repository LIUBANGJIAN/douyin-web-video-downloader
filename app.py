from flask import Flask, jsonify, request, send_file, redirect
import os
import subprocess
import sys
import json
import logging
from datetime import datetime

app = Flask(__name__)

APP_VERSION = 'v3.1.1'

# 定义目录结构
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.environ.get('CONFIG_DIR', os.path.join(BASE_DIR, 'config'))
LOG_DIR = os.environ.get('LOG_DIR', os.path.join(BASE_DIR, 'logs'))
DOWNLOAD_DIR = os.environ.get('DOWNLOAD_DIR', os.path.join(BASE_DIR, 'downloads'))
PORT = int(os.environ.get('PORT', 8787))

# 创建目录
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# 配置日志
def setup_logging():
    log_file = os.path.join(LOG_DIR, f'{datetime.now().strftime("%Y-%m-%d")}.log')
    logger = logging.getLogger('douyin_downloader')
    logger.setLevel(logging.INFO)
    
    # 避免重复添加处理器
    if not logger.handlers:
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

# 创建环境变量解决 Unicode 编码问题
def get_douyin_env():
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['LANG'] = 'en_US.UTF-8'
    return env

# 安全执行 douyin-dl 命令
def run_douyin_command(args, timeout=60):
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=get_douyin_env(),
            errors='replace'
        )
        return result
    except Exception as e:
        # 如果 text=True 失败，尝试使用 bytes 模式
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                timeout=timeout,
                env=get_douyin_env()
            )
            # 手动解码，忽略错误
            stdout = result.stdout.decode('utf-8', errors='replace') if result.stdout else ''
            stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ''
            # 返回一个类似 subprocess.CompletedProcess 的对象
            return type('CompletedProcess', (), {
                'returncode': result.returncode,
                'stdout': stdout,
                'stderr': stderr
            })
        except Exception as e2:
            logger.error(f"运行 douyin-dl 命令失败: {e2}")
            return type('CompletedProcess', (), {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e2)
            })

# 检查 douyin-downloader 是否可用
DOUYIN_DOWNLOADER_AVAILABLE = False
DOUYIN_DOWNLOADER_CMD = "douyin-dl"

def check_douyin_downloader():
    global DOUYIN_DOWNLOADER_AVAILABLE, DOUYIN_DOWNLOADER_CMD
    
    # 设置环境变量解决 Unicode 编码问题
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['LANG'] = 'en_US.UTF-8'
    
    try:
        result = run_douyin_command([DOUYIN_DOWNLOADER_CMD, '--version'], timeout=30)
        if result.returncode == 0 and result.stdout:
            DOUYIN_DOWNLOADER_AVAILABLE = True
            logger.info(f"douyin-downloader 已安装: {result.stdout.strip()}")
            return
        logger.warning(f"命令行测试失败, 返回码: {result.returncode}, stderr: {result.stderr[:200]}")
    except Exception as e:
        logger.error(f"命令行检查失败: {e}")
    
    logger.error("douyin-downloader 不可用")

check_douyin_downloader()

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/version')
def get_version():
    return jsonify({
        'version': APP_VERSION,
        'backend': 'douyin-downloader',
        'douyin_downloader': DOUYIN_DOWNLOADER_AVAILABLE
    })

@app.route('/api/parse', methods=['POST'])
def parse_url():
    if not DOUYIN_DOWNLOADER_AVAILABLE:
        return jsonify({'success': False, 'message': 'douyin-downloader 未安装'})
    
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'success': False, 'message': '请输入抖音链接'})
        
        logger.info(f"开始解析链接: {url}")
        
        config_content = f'''
link:
  - "{url}"
path: {DOWNLOAD_DIR}
mode:
  - post
number:
  post: 1
database: false
browser_fallback:
  enabled: false
'''
        config_path = os.path.join(CONFIG_DIR, 'temp_config.yml')
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        result = run_douyin_command([DOUYIN_DOWNLOADER_CMD, '-c', config_path, '-v'], timeout=60)
        
        os.remove(config_path)
        
        if result.returncode == 0:
            logger.info(f"链接解析成功: {url}")
            video_info = {
                'success': True,
                'type': 'video',
                'title': '解析成功',
                'author': '',
                'thumbnail': '',
                'video_url': url,
                'video_id': ''
            }
            return jsonify(video_info)
        else:
            error_msg = result.stderr[:200] if result.stderr else result.stdout[:200]
            logger.error(f"链接解析失败: {url}, 错误: {error_msg}")
            return jsonify({'success': False, 'message': f'解析失败: {error_msg}'})
    
    except subprocess.TimeoutExpired:
        logger.error(f"链接解析超时: {url}")
        return jsonify({'success': False, 'message': '解析超时'})
    except Exception as e:
        logger.error(f"链接解析异常: {url}, 错误: {str(e)}")
        return jsonify({'success': False, 'message': f'解析失败: {str(e)}'})

@app.route('/api/download', methods=['POST'])
def download_video():
    if not DOUYIN_DOWNLOADER_AVAILABLE:
        return jsonify({'success': False, 'message': 'douyin-downloader 未安装'})
    
    try:
        data = request.get_json()
        url = data.get('url', '')
        
        if not url:
            return jsonify({'success': False, 'message': '请提供下载链接'})
        
        logger.info(f"开始下载视频: {url}")
        
        # 使用时间戳创建唯一的配置文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_path = os.path.join(CONFIG_DIR, f'temp_config_{timestamp}.yml')
        config_content = f'''
link:
  - "{url}"
path: {DOWNLOAD_DIR}
mode:
  - post
number:
  post: 1
database: false
browser_fallback:
  enabled: false
'''
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        result = run_douyin_command([DOUYIN_DOWNLOADER_CMD, '-c', config_path], timeout=120)
        
        os.remove(config_path)
        
        if result.returncode == 0:
            # 查找最新下载的文件
            video_files = []
            for item in os.listdir(DOWNLOAD_DIR):
                if item.endswith('.mp4'):
                    file_path = os.path.join(DOWNLOAD_DIR, item)
                    mtime = os.path.getmtime(file_path)
                    video_files.append((mtime, item))
            
            if video_files:
                video_files.sort(key=lambda x: x[0], reverse=True)
                video_file = video_files[0][1]
                file_path = os.path.join(DOWNLOAD_DIR, video_file)
                file_size = os.path.getsize(file_path)
                logger.info(f"视频下载成功: {video_file}, 大小: {file_size} bytes")
                return jsonify({
                    'success': True,
                    'filename': video_file,
                    'download_url': f'/download/{video_file}'
                })
            else:
                logger.error(f"下载成功但未找到文件: {url}")
                return jsonify({'success': False, 'message': '下载成功但未找到文件'})
        else:
            error_msg = result.stderr[:200] if result.stderr else result.stdout[:200]
            logger.error(f"视频下载失败: {url}, 错误: {error_msg}")
            return jsonify({'success': False, 'message': f'下载失败: {error_msg}'})
    
    except subprocess.TimeoutExpired:
        logger.error(f"视频下载超时: {url}")
        return jsonify({'success': False, 'message': '下载超时'})
    except Exception as e:
        logger.error(f"视频下载异常: {url}, 错误: {str(e)}")
        return jsonify({'success': False, 'message': f'下载失败: {str(e)}'})

@app.route('/download/<filename>')
def serve_download(filename):
    try:
        file_path = os.path.join(DOWNLOAD_DIR, filename)
        if os.path.exists(file_path):
            logger.info(f"提供下载文件: {filename}")
            return send_file(file_path, as_attachment=True)
        else:
            logger.error(f"文件不存在: {filename}")
            return jsonify({'success': False, 'message': '文件不存在'}), 404
    except Exception as e:
        logger.error(f"下载文件异常: {filename}, 错误: {str(e)}")
        return jsonify({'success': False, 'message': '文件不存在'}), 404

@app.route('/api/direct-download', methods=['GET'])
def direct_download():
    if not DOUYIN_DOWNLOADER_AVAILABLE:
        return jsonify({'success': False, 'message': 'douyin-downloader 未安装'}), 500
    
    url = request.args.get('url', '')
    if not url:
        return jsonify({'success': False, 'message': '缺少url参数'}), 400
    
    try:
        logger.info(f"直接下载请求: {url}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_path = os.path.join(CONFIG_DIR, f'direct_config_{timestamp}.yml')
        config_content = f'''
link:
  - "{url}"
path: {DOWNLOAD_DIR}
mode:
  - post
number:
  post: 1
database: false
browser_fallback:
  enabled: false
'''
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        result = run_douyin_command([DOUYIN_DOWNLOADER_CMD, '-c', config_path], timeout=120)
        
        os.remove(config_path)
        
        if result.returncode == 0:
            video_files = []
            for item in os.listdir(DOWNLOAD_DIR):
                if item.endswith('.mp4'):
                    file_path = os.path.join(DOWNLOAD_DIR, item)
                    mtime = os.path.getmtime(file_path)
                    video_files.append((mtime, item))
            
            if video_files:
                video_files.sort(key=lambda x: x[0], reverse=True)
                video_file = video_files[0][1]
                logger.info(f"直接下载成功: {video_file}")
                return send_file(os.path.join(DOWNLOAD_DIR, video_file), as_attachment=True)
            else:
                logger.error(f"直接下载失败，未找到文件: {url}")
                return jsonify({'success': False, 'message': '下载失败'}), 400
        else:
            logger.error(f"直接下载失败: {url}")
            return jsonify({'success': False, 'message': '下载失败'}), 400
    
    except Exception as e:
        logger.error(f"直接下载异常: {url}, 错误: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/quick-download', methods=['POST'])
def quick_download():
    if not DOUYIN_DOWNLOADER_AVAILABLE:
        return jsonify({'success': False, 'message': 'douyin-downloader 未安装'}), 500
    
    data = request.get_json()
    url = data.get('url', '')
    
    if not url:
        return jsonify({'success': False, 'message': '缺少url参数'}), 400
    
    return jsonify({
        'success': True,
        'video_url': url,
        'title': '',
        'author': ''
    })

if __name__ == '__main__':
    print(f"服务器启动，版本: {APP_VERSION}")
    print(f"douyin-downloader 可用: {DOUYIN_DOWNLOADER_AVAILABLE}")
    print(f"运行在: http://0.0.0.0:{PORT}")
    print(f"配置目录: {CONFIG_DIR}")
    print(f"日志目录: {LOG_DIR}")
    print(f"下载目录: {DOWNLOAD_DIR}")
    logger.info(f"服务器启动，版本: {APP_VERSION}")
    app.run(host='0.0.0.0', port=PORT, debug=True)
