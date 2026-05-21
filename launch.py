# -*- coding: utf-8 -*-
import subprocess
import sys
import os

# 日志文件
log_file = 'startup_log.txt'

# 清空旧日志
if os.path.exists(log_file):
    os.remove(log_file)

def log(msg):
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{msg}\n")
    print(msg)

log("=" * 60)
log("抖音视频下载器启动脚本")
log("=" * 60)

log(f"\n1. 系统信息:")
log(f"   Python 版本: {sys.version}")
log(f"   Python 路径: {sys.executable}")
log(f"   当前目录: {os.getcwd()}")

log("\n2. 检查并安装依赖:")

# 检查 Flask
try:
    import flask
    log("   ✓ Flask 已安装")
except ImportError:
    log("   ✗ Flask 未安装，正在安装...")
    result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'Flask==2.3.3'],
                           capture_output=True, text=True)
    if result.returncode == 0:
        log("   ✓ Flask 安装成功")
    else:
        log(f"   ✗ Flask 安装失败: {result.stderr[:300]}")

# 检查 douyin_downloader
try:
    from douyin_downloader import DouyinDownloader
    log("   ✓ douyin_downloader 已安装")
except ImportError:
    log("   ✗ douyin_downloader 未安装，正在安装...")
    result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'git+https://github.com/jiji262/douyin-downloader.git'],
                           capture_output=True, text=True)
    if result.returncode == 0:
        log("   ✓ douyin_downloader 安装成功")
    else:
        log(f"   ✗ douyin_downloader 安装失败: {result.stderr[:300]}")

log("\n3. 尝试导入并启动服务器:")
try:
    from douyin_downloader import DouyinDownloader
    downloader = DouyinDownloader()
    log("   ✓ douyin_downloader 初始化成功")
    
    # 启动 Flask 应用
    from flask import Flask, jsonify, request, send_file, redirect
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = '/app/downloads'
    app.config['PORT'] = 8787
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    @app.route('/')
    def index():
        return send_file('index.html')
    
    @app.route('/api/version')
    def get_version():
        return jsonify({'version': 'v3.0.0', 'backend': 'douyin-downloader'})
    
    @app.route('/api/parse', methods=['POST'])
    def parse_url():
        try:
            data = request.get_json()
            url = data.get('url', '').strip()
            if not url:
                return jsonify({'success': False, 'message': '请输入抖音链接'})
            result = downloader.parse(url)
            if result:
                video_info = {
                    'success': True,
                    'type': 'video',
                    'title': result.get('title', ''),
                    'author': result.get('author', ''),
                    'thumbnail': result.get('cover', ''),
                    'video_url': result.get('video_url', ''),
                    'video_id': result.get('aweme_id', '')
                }
                if result.get('images'):
                    video_info['type'] = 'image'
                    video_info['image_url_list'] = result['images']
                return jsonify(video_info)
            else:
                return jsonify({'success': False, 'message': '解析失败'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    
    log("   ✓ Flask 应用配置完成")
    log(f"\n4. 启动服务器:")
    log(f"   版本: v3.0.0")
    log(f"   地址: http://localhost:{app.config['PORT']}")
    log("   按 Ctrl+C 停止")
    log("=" * 60)
    
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=True)
    
except Exception as e:
    log(f"   ✗ 启动失败: {str(e)}")
    import traceback
    log(f"   详细错误: {traceback.format_exc()}")

log("\n服务器已停止")