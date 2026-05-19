from flask import Flask, jsonify, request, send_file, Response
from yt_dlp import YoutubeDL
import re
import os
import uuid
import subprocess
from urllib.parse import urlparse
import requests
import time
import threading
import base64
import json

app = Flask(__name__)

APP_VERSION = 'v2.1.0'
app.config['UPLOAD_FOLDER'] = os.environ.get('DOWNLOAD_DIR', '/app/downloads')
app.config['PORT'] = int(os.environ.get('PORT', 8787))
app.config['COOKIES_FILE'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.txt')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

NODE_AVAILABLE = False
NODE_VERSION = ""
YTDLP_VERSION = ""
DOUYIN_COOKIES = {}
LAST_COOKIES_UPDATE = 0
PLAYWRIGHT_AVAILABLE = False

def check_nodejs():
    global NODE_AVAILABLE, NODE_VERSION
    try:
        result = subprocess.run(['node', '-v'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            NODE_AVAILABLE = True
            NODE_VERSION = result.stdout.strip()
            app.logger.info(f"✅ Node.js 可用: {NODE_VERSION}")
        else:
            app.logger.warning("❌ Node.js 不可用")
    except FileNotFoundError:
        app.logger.warning("❌ Node.js 未找到")
    except Exception as e:
        app.logger.warning(f"❌ 检查 Node.js 失败: {str(e)}")

def check_ytdlp():
    global YTDLP_VERSION
    try:
        import yt_dlp
        YTDLP_VERSION = yt_dlp.version.__version__
        app.logger.info(f"✅ yt-dlp 版本: {YTDLP_VERSION}")
    except Exception as e:
        YTDLP_VERSION = "未知"
        app.logger.warning(f"❌ 获取 yt-dlp 版本失败: {str(e)}")

def check_playwright():
    global PLAYWRIGHT_AVAILABLE
    try:
        from playwright.sync_api import sync_playwright
        PLAYWRIGHT_AVAILABLE = True
        app.logger.info("✅ Playwright 可用")
    except ImportError:
        app.logger.warning("❌ Playwright 未安装")
    except Exception as e:
        app.logger.warning(f"❌ 检查 Playwright 失败: {str(e)}")

check_nodejs()
check_ytdlp()
check_playwright()

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'

COMMON_HEADERS = {
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
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
}

SITE_REFERERS = {
    'douyin': 'https://www.douyin.com/',
    'bilibili': 'https://www.bilibili.com/',
    'youtube': 'https://www.youtube.com/',
    'kuaishou': 'https://www.kuaishou.com/',
    'xiaohongshu': 'https://www.xiaohongshu.com/',
    'weibo': 'https://weibo.com/',
    'tiktok': 'https://www.tiktok.com/',
    'instagram': 'https://www.instagram.com/',
    'twitter': 'https://twitter.com/',
}

def get_site_info(url):
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    for site, referer in SITE_REFERERS.items():
        if site in domain:
            return {'type': site, 'referer': referer}

    return {'type': 'other', 'referer': f'{parsed.scheme}://{domain}/'}

def get_headers(url):
    site_info = get_site_info(url)
    headers = COMMON_HEADERS.copy()
    headers['Referer'] = site_info['referer']
    return headers

def _sanitize_url(text):
    if not text or not isinstance(text, str):
        return ''
    return text.strip()

def _extract_url_from_text(text):
    if not text or not isinstance(text, str):
        return ''
    t = text.strip()
    if t.startswith('http://') or t.startswith('https://'):
        return t
    m = re.search(r"https?://[\w\-\./?%&=+#~:;,'()]+", text)
    if m:
        return m.group(0)
    return ''

def _quality_format(quality):
    q = str(quality or '').strip()
    if q.lower() in ('best', 'worst', 'source'):
        return q.lower()
    if q.isdigit():
        return f'bestvideo[height<={q}]+bestaudio/best'
    return q or 'best'

def _extract_info(video_url):
    if not video_url:
        raise ValueError('请输入视频链接或包含链接的文本')

    site_info = get_site_info(video_url)
    headers = get_headers(video_url)

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'noplaylist': True,
        'user_agent': USER_AGENT,
        'http_headers': headers,
    }
    
    cookies_file = app.config['COOKIES_FILE']
    if os.path.exists(cookies_file):
        ydl_opts['cookiefile'] = cookies_file

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)

    if info.get('_type') == 'playlist':
        entries = info.get('entries') or []
        if not entries:
            raise ValueError('无法解析视频信息')
        info = entries[0]

    if not info:
        raise ValueError('无法解析视频信息')

    title = info.get('title') or '视频'
    author = info.get('creator') or info.get('uploader') or info.get('uploader_id') or ''
    thumbnail = info.get('thumbnail') or ''
    duration = info.get('duration')

    formats = info.get('formats') or []
    heights = set()
    for fmt in formats:
        if fmt.get('vcodec') == 'none' or fmt.get('height') is None:
            continue
        heights.add(int(fmt['height']))

    qualities = [str(h) for h in sorted(heights, reverse=True)]
    if not qualities:
        qualities = ['best']

    return {
        'url': video_url,
        'title': title,
        'author': author,
        'thumbnail': thumbnail,
        'duration': duration,
        'qualities': qualities,
        'defaultQuality': qualities[0],
        'siteType': site_info['type'],
    }

def _download_video(url, quality, dest_path):
    format_str = _quality_format(quality)
    site_info = get_site_info(url)
    headers = get_headers(url)

    ydl_opts = {
        'format': format_str,
        'outtmpl': dest_path,
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'user_agent': USER_AGENT,
        'http_headers': headers,
        'merge_output_format': 'mp4',
    }
    
    cookies_file = app.config['COOKIES_FILE']
    if os.path.exists(cookies_file):
        ydl_opts['cookiefile'] = cookies_file

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
    return info

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/version')
def version():
    cookies_valid = os.path.exists(app.config['COOKIES_FILE']) and (time.time() - LAST_COOKIES_UPDATE) < 3600 * 24
    return jsonify({
        'version': APP_VERSION,
        'backend': 'yt-dlp',
        'node_available': NODE_AVAILABLE,
        'node_version': NODE_VERSION,
        'ytdlp_version': YTDLP_VERSION,
        'playwright_available': PLAYWRIGHT_AVAILABLE,
        'cookies_valid': cookies_valid,
        'cookies_updated': LAST_COOKIES_UPDATE,
    })

@app.route('/api/info', methods=['POST'])
def video_info():
    data = request.get_json() or {}
    raw = data.get('url', '')
    url = _extract_url_from_text(_sanitize_url(raw))
    if not url:
        return jsonify({'error': '请输入有效的视频链接或将包含链接的文本粘贴到输入框'}), 400
    try:
        info = _extract_info(url)
        return jsonify({'success': True, **info})
    except Exception as e:
        error_msg = str(e)
        if 'sign token' in error_msg.lower() or 'captcha' in error_msg.lower():
            if not NODE_AVAILABLE:
                error_msg = '⚠️ 服务器 Node.js 环境未配置，无法解析抖音加密参数'
            else:
                error_msg = '⚠️ 该视频需要登录才能下载，请先扫码获取Cookie'
        elif 'Fresh cookies' in error_msg:
            error_msg = '⚠️ 需要新鲜的抖音Cookie，请点击"扫码获取Cookie"按钮登录'
        return jsonify({'error': error_msg}), 500

@app.route('/api/download', methods=['POST'])
def download_video():
    data = request.get_json() or {}
    raw = data.get('url', '')
    url = _extract_url_from_text(_sanitize_url(raw))
    quality = data.get('quality', 'best')
    if not url:
        return jsonify({'error': '请输入有效的视频链接或将包含链接的文本粘贴到输入框'}), 400

    video_id = str(uuid.uuid4())
    dest = os.path.join(app.config['UPLOAD_FOLDER'], f'{video_id}.mp4')

    try:
        info = _download_video(url, quality, dest)
        file_size = os.path.getsize(dest) if os.path.isfile(dest) else 0
        return jsonify({
            'success': True,
            'videoUrl': f'/download/{video_id}.mp4',
            'title': info.get('title') or '',
            'author': info.get('creator') or info.get('uploader') or '',
            'thumbnail': info.get('thumbnail') or '',
            'fileSize': file_size,
            'quality': quality,
            'version': APP_VERSION,
        })
    except Exception as e:
        error_msg = str(e)
        if 'sign token' in error_msg.lower() or 'captcha' in error_msg.lower():
            if not NODE_AVAILABLE:
                error_msg = '⚠️ 服务器 Node.js 环境未配置，无法解析抖音加密参数'
            else:
                error_msg = '⚠️ 该视频需要登录才能下载，请先扫码获取Cookie'
        elif 'Fresh cookies' in error_msg:
            error_msg = '⚠️ 需要新鲜的抖音Cookie，请点击"扫码获取Cookie"按钮登录'
        return jsonify({'error': error_msg}), 500

@app.route('/download/<filename>')
def serve_download(filename):
    safe = os.path.basename(filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], safe)
    if not os.path.isfile(path):
        return jsonify({'error': '文件不存在'}), 404
    return send_file(path, as_attachment=True)

login_thread = None
login_result = None
login_status = 'idle'

def do_browser_login():
    global login_result, login_status
    from playwright.sync_api import sync_playwright
    
    try:
        login_status = 'starting'
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=['--no-sandbox', '--disable-setuid-sandbox'])
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()
            
            login_status = 'navigating'
            page.goto('https://www.douyin.com', timeout=60000)
            page.wait_for_timeout(3000)
            
            login_status = 'waiting'
            start_time = time.time()
            while time.time() - start_time < 120:
                cookies = context.cookies()
                ttwid = None
                passport_csrf_token = None
                
                for cookie in cookies:
                    if cookie['name'] == 'ttwid':
                        ttwid = cookie['value']
                    if cookie['name'] == 'passport_csrf_token':
                        passport_csrf_token = cookie['value']
                
                if ttwid and passport_csrf_token:
                    login_status = 'success'
                    cookie_string = ''
                    for cookie in cookies:
                        cookie_string += f"{cookie['name']}={cookie['value']}; "
                    
                    with open(app.config['COOKIES_FILE'], 'w', encoding='utf-8') as f:
                        f.write(cookie_string.strip())
                    
                    global DOUYIN_COOKIES, LAST_COOKIES_UPDATE
                    DOUYIN_COOKIES = {c['name']: c['value'] for c in cookies}
                    LAST_COOKIES_UPDATE = time.time()
                    
                    login_result = {
                        'success': True,
                        'message': '登录成功，Cookie已保存',
                        'cookies_count': len(cookies),
                    }
                    break
                
                page.wait_for_timeout(2000)
            else:
                login_status = 'timeout'
                login_result = {'success': False, 'message': '登录超时，请重新尝试'}
            
            browser.close()
    except Exception as e:
        login_status = 'error'
        login_result = {'success': False, 'message': f'登录失败: {str(e)}'}

@app.route('/api/douyin/qrcode', methods=['GET'])
def get_douyin_qrcode():
    global login_thread, login_result, login_status
    
    if not PLAYWRIGHT_AVAILABLE:
        return jsonify({'error': 'Playwright 未安装，请先安装: pip install playwright && playwright install chromium'}), 500
    
    if login_thread and login_thread.is_alive():
        return jsonify({'error': '已有登录会话进行中，请等待完成'}), 400
    
    login_result = None
    login_status = 'idle'
    
    login_thread = threading.Thread(target=do_browser_login)
    login_thread.daemon = True
    login_thread.start()
    
    return jsonify({
        'success': True,
        'message': '浏览器已启动，请在弹出的浏览器窗口中完成抖音登录',
        'status': 'starting',
    })

@app.route('/api/douyin/login_status', methods=['GET'])
def check_login_status():
    global login_status, login_result, login_thread
    
    if login_thread and login_thread.is_alive():
        return jsonify({
            'success': True,
            'status': login_status,
            'message': {
                'idle': '等待开始',
                'starting': '正在启动浏览器...',
                'navigating': '正在打开抖音页面...',
                'waiting': '等待用户登录（请在弹出的浏览器中扫码或登录）...',
            }.get(login_status, '未知状态'),
        })
    
    if login_result:
        return jsonify(login_result)
    
    return jsonify({'success': True, 'status': 'idle', 'message': '未开始登录'})

@app.route('/api/douyin/set_cookies', methods=['POST'])
def set_douyin_cookies():
    global DOUYIN_COOKIES, LAST_COOKIES_UPDATE
    try:
        data = request.get_json() or {}
        cookies_text = data.get('cookies', '').strip()
        
        if not cookies_text:
            return jsonify({'error': 'Cookie内容不能为空'}), 400
        
        with open(app.config['COOKIES_FILE'], 'w', encoding='utf-8') as f:
            f.write(cookies_text)
        
        DOUYIN_COOKIES = {}
        for cookie in cookies_text.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                name, value = cookie.split('=', 1)
                DOUYIN_COOKIES[name.strip()] = value.strip()
        
        LAST_COOKIES_UPDATE = time.time()
        
        return jsonify({
            'success': True,
            'message': 'Cookie已保存',
            'cookies_count': len(DOUYIN_COOKIES),
        })
    except Exception as e:
        app.logger.error(f'保存Cookie失败: {str(e)}')
        return jsonify({'error': f'保存Cookie失败: {str(e)}'}), 500

@app.route('/api/douyin/cookies_status', methods=['GET'])
def get_cookies_status():
    cookies_valid = os.path.exists(app.config['COOKIES_FILE'])
    if cookies_valid:
        file_time = os.path.getmtime(app.config['COOKIES_FILE'])
        age_hours = (time.time() - file_time) / 3600
        return jsonify({
            'success': True,
            'has_cookies': cookies_valid,
            'age_hours': round(age_hours, 1),
            'updated': file_time,
        })
    return jsonify({'success': True, 'has_cookies': False, 'age_hours': 0, 'updated': 0})

@app.route('/api/douyin/clear_cookies', methods=['POST'])
def clear_cookies():
    try:
        if os.path.exists(app.config['COOKIES_FILE']):
            os.remove(app.config['COOKIES_FILE'])
            global DOUYIN_COOKIES, LAST_COOKIES_UPDATE
            DOUYIN_COOKIES = {}
            LAST_COOKIES_UPDATE = 0
            return jsonify({'success': True, 'message': 'Cookie已清除'})
        return jsonify({'success': True, 'message': '没有Cookie可清除'})
    except Exception as e:
        return jsonify({'error': f'清除Cookie失败: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=False)
