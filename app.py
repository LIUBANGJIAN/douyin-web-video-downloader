from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
import uuid
import re
import subprocess
import sys
from urllib.parse import urlparse

app = Flask(__name__)

APP_VERSION = "v1.5.0"

app.config['UPLOAD_FOLDER'] = os.environ.get('DOWNLOAD_DIR', '/app/downloads')
app.config['PORT'] = int(os.environ.get('PORT', 8787))

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

NODE_AVAILABLE = False
NODE_PATH = ""

def check_nodejs():
    global NODE_AVAILABLE, NODE_PATH
    try:
        result = subprocess.run(['which', 'node'], capture_output=True, text=True)
        NODE_PATH = result.stdout.strip()
        if NODE_PATH:
            version_result = subprocess.run(['node', '-v'], capture_output=True, text=True)
            if version_result.returncode == 0:
                NODE_AVAILABLE = True
                app.logger.info(f"✅ Node.js 可用: {version_result.stdout.strip()}")
            else:
                app.logger.warning("❌ Node.js 不可用")
        else:
            app.logger.warning("❌ Node.js 未找到")
    except Exception as e:
        app.logger.warning(f"❌ 检查 Node.js 失败: {str(e)}")

check_nodejs()

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/version')
def version():
    return jsonify({'version': APP_VERSION, 'node_available': NODE_AVAILABLE})

def extract_url(text):
    patterns = [
        r'https?://v\.douyin\.com/[a-zA-Z0-9_-]+/?',
        r'https?://www\.douyin\.com/video/[a-zA-Z0-9_-]+/?',
        r'https?://douyin\.com/video/[a-zA-Z0-9_-]+/?',
        r'https?://www\.bilibili\.com/video/[a-zA-Z0-9]+/?',
        r'https?://bilibili\.com/video/[a-zA-Z0-9]+/?',
        r'https?://www\.youtube\.com/watch\?v=[a-zA-Z0-9_-]+',
        r'https?://youtu\.be/[a-zA-Z0-9_-]+',
        r'https?://[^\s]+',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            url = match.group(0).rstrip('.,')
            if url:
                return url
    
    clean_text = re.sub(r'[^a-zA-Z0-9_\-:/.]', '', text.strip())
    if 'http' in clean_text:
        return clean_text
    
    return text.strip()

def get_site_info(url):
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    
    if 'douyin' in domain or 'v.douyin' in domain:
        return {
            'type': 'douyin',
            'name': '抖音',
            'referer': 'https://www.douyin.com/'
        }
    elif 'bilibili' in domain or 'bilibili.com' in domain:
        return {
            'type': 'bilibili',
            'name': 'B站',
            'referer': 'https://www.bilibili.com/'
        }
    elif 'youtube' in domain or 'youtu.be' in domain:
        return {
            'type': 'youtube',
            'name': 'YouTube',
            'referer': 'https://www.youtube.com/'
        }
    elif 'kuaishou' in domain or 'kuaishou.com' in domain:
        return {
            'type': 'kuaishou',
            'name': '快手',
            'referer': 'https://www.kuaishou.com/'
        }
    elif 'xiaohongshu' in domain or 'xiaohongshu.com' in domain:
        return {
            'type': 'xiaohongshu',
            'name': '小红书',
            'referer': 'https://www.xiaohongshu.com/'
        }
    elif 'weibo' in domain or 'weibo.com' in domain:
        return {
            'type': 'weibo',
            'name': '微博',
            'referer': 'https://weibo.com/'
        }
    elif 'tiktok' in domain:
        return {
            'type': 'tiktok',
            'name': 'TikTok',
            'referer': 'https://www.tiktok.com/'
        }
    
    return {
        'type': 'other',
        'name': '其他',
        'referer': f'{parsed.scheme}://{domain}/'
    }

def get_global_headers(site_info):
    headers = [
        'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8',
        'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        f'Referer: {site_info["referer"]}'
    ]
    return headers

def get_user_agent():
    return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'

@app.route('/api/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        url = data.get('url', '')
        
        if not url:
            return jsonify({'error': '请输入视频链接'}), 400
        
        clean_url = extract_url(url)
        
        if not clean_url or 'http' not in clean_url:
            return jsonify({'error': '请输入有效的视频链接'}), 400
        
        video_id = str(uuid.uuid4())
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{video_id}.%(ext)s')
        
        site_info = get_site_info(clean_url)
        site_type = site_info['type']
        
        ydl_opts = {
            'format': 'bestvideo[ext=mp4][height<=2160]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_path,
            'quiet': False,
            'no_warnings': True,
            'user_agent': get_user_agent(),
            'http_headers': {
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Referer': site_info['referer'],
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
            },
            'ignoreerrors': False,
            'retries': 3,
            'merge_output_format': 'mp4',
            'timeout': 120,
            'extractor_args': {},
        }
        
        if site_type == 'bilibili':
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4][height<=2160]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            })
        elif site_type == 'douyin':
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            })
            ydl_opts['extractor_args']['douyin'] = ['--no-check-certificate']
        elif site_type == 'youtube':
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
            })
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=True)
            
            if not info:
                return jsonify({'error': '无法获取视频信息'}), 500
            
            video_title = info.get('title', '视频')
            video_ext = info.get('ext', 'mp4')
            video_file = os.path.join(app.config['UPLOAD_FOLDER'], f'{video_id}.{video_ext}')
            
            thumbnail = info.get('thumbnail', '')
            if thumbnail:
                if not thumbnail.startswith('http'):
                    thumbnail = ''
            
            video_url = f'/download/{video_id}.{video_ext}'
            
            if os.path.exists(video_file):
                file_size = os.path.getsize(video_file)
                resolution = info.get('height', '')
                return jsonify({
                    'success': True,
                    'videoUrl': video_url,
                    'title': video_title,
                    'author': info.get('uploader', ''),
                    'ext': video_ext,
                    'thumbnail': thumbnail,
                    'fileSize': file_size,
                    'resolution': resolution,
                    'version': APP_VERSION,
                    'nodeAvailable': NODE_AVAILABLE,
                    'siteType': site_type,
                    'siteName': site_info['name']
                })
            else:
                return jsonify({'error': '视频下载失败'}), 500
                
    except Exception as e:
        error_msg = str(e)
        error_lower = error_msg.lower()
        
        if 'sign token' in error_lower or 'captcha' in error_lower or '风控' in error_msg:
            error_msg = '⚠️ 当前 IP 触发风控，请稍后再试或更换网络'
        elif 'cookies' in error_lower or 'cookie' in error_lower:
            if not NODE_AVAILABLE:
                error_msg = '⚠️ 服务器 Node.js 环境未配置，无法解析抖音加密参数'
            else:
                error_msg = '⚠️ 该视频需要登录才能下载，请尝试其他视频'
        elif 'format' in error_lower and 'available' in error_lower:
            return download_fallback(clean_url, video_id)
        
        return jsonify({'error': error_msg}), 500

def download_fallback(url, video_id):
    try:
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{video_id}_fallback.%(ext)s')
        site_info = get_site_info(url)
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': output_path,
            'quiet': False,
            'no_warnings': True,
            'user_agent': get_user_agent(),
            'http_headers': {
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Referer': site_info['referer'],
            },
            'retries': 1,
            'timeout': 60,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            if not info:
                return jsonify({'error': '无法获取视频信息'}), 500
            
            video_title = info.get('title', '视频')
            video_ext = info.get('ext', 'mp4')
            video_file = os.path.join(app.config['UPLOAD_FOLDER'], f'{video_id}_fallback.{video_ext}')
            
            thumbnail = info.get('thumbnail', '')
            if thumbnail and not thumbnail.startswith('http'):
                thumbnail = ''
            
            if os.path.exists(video_file):
                file_size = os.path.getsize(video_file)
                return jsonify({
                    'success': True,
                    'videoUrl': f'/download/{video_id}_fallback.{video_ext}',
                    'title': video_title,
                    'author': info.get('uploader', ''),
                    'ext': video_ext,
                    'thumbnail': thumbnail,
                    'fileSize': file_size,
                    'version': APP_VERSION,
                    'nodeAvailable': NODE_AVAILABLE
                })
            else:
                return jsonify({'error': '视频下载失败'}), 500
    except Exception as e:
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

@app.route('/download/<filename>')
def serve_download(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=True)