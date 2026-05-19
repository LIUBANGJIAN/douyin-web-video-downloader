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

APP_VERSION = 'v2.3.0'
app.config['UPLOAD_FOLDER'] = os.environ.get('DOWNLOAD_DIR', '/app/downloads')
app.config['PORT'] = int(os.environ.get('PORT', 8787))
app.config['COOKIES_FILE'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.txt')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

NODE_AVAILABLE = False
NODE_VERSION = ""
YTDLP_VERSION = ""
PLAYWRIGHT_AVAILABLE = False

login_status = 'idle'
login_result = None
login_qrcode_base64 = None
login_thread = None

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

check_nodejs()
check_ytdlp()

def check_playwright():
    global PLAYWRIGHT_AVAILABLE
    try:
        import playwright
        PLAYWRIGHT_AVAILABLE = True
        app.logger.info("✅ Playwright 可用")
    except ImportError:
        PLAYWRIGHT_AVAILABLE = False
        app.logger.warning("❌ Playwright 不可用")

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
    cookies_valid = os.path.exists(app.config['COOKIES_FILE'])
    cookies_updated = os.path.getmtime(app.config['COOKIES_FILE']) if cookies_valid else 0
    return jsonify({
        'version': APP_VERSION,
        'backend': 'yt-dlp',
        'node_available': NODE_AVAILABLE,
        'node_version': NODE_VERSION,
        'ytdlp_version': YTDLP_VERSION,
        'playwright_available': PLAYWRIGHT_AVAILABLE,
        'cookies_valid': cookies_valid,
        'cookies_updated': cookies_updated,
    })

@app.route('/api/douyin/qrcode')
def get_qrcode():
    global login_status, login_result, login_qrcode_base64, login_thread
    
    if not PLAYWRIGHT_AVAILABLE:
        return jsonify({'success': False, 'error': 'Playwright 未安装，请先安装 Playwright'})
    
    if login_status == 'starting' or login_status == 'waiting':
        return jsonify({'success': True, 'qrcode': login_qrcode_base64, 'message': '获取二维码中...'})
    
    login_status = 'starting'
    login_result = None
    login_qrcode_base64 = None
    
    login_thread = threading.Thread(target=do_qrcode_login)
    login_thread.daemon = True
    login_thread.start()
    
    return jsonify({'success': True, 'message': '正在启动浏览器...'})

@app.route('/api/douyin/login_status')
def login_status_api():
    global login_status, login_result, login_qrcode_base64
    
    if login_status == 'idle':
        return jsonify({'success': True, 'status': 'idle', 'message': '未开始登录'})
    
    return jsonify({
        'success': True,
        'status': login_status,
        'qrcode': login_qrcode_base64,
        'message': login_result.get('message') if login_result else None,
    })

@app.route('/api/douyin/cookies_status')
def cookies_status_api():
    if os.path.exists(app.config['COOKIES_FILE']):
        age_seconds = time.time() - os.path.getmtime(app.config['COOKIES_FILE'])
        return jsonify({
            'success': True,
            'has_cookies': True,
            'age_hours': round(age_seconds / 3600, 1),
        })
    return jsonify({'success': True, 'has_cookies': False, 'age_hours': 0})

def do_qrcode_login():
    global login_status, login_result, login_qrcode_base64
    
    from playwright.sync_api import sync_playwright
    
    try:
        app.logger.info("Starting QR code login process")
        login_status = 'starting'
        
        with sync_playwright() as p:
            app.logger.info("Launching browser")
            browser = p.chromium.launch(
                headless=False, 
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--disable-dev-shm-usage', '--disable-web-security']
            )
            
            context = browser.new_context(viewport={'width': 400, 'height': 600})
            page = context.new_page()
            
            app.logger.info("Navigating to douyin.com")
            page.goto('https://www.douyin.com', timeout=60000)
            
            page.wait_for_timeout(3000)
            
            login_button_selector = '//button[contains(text(), "登录")] | //a[contains(text(), "登录")] | //div[contains(@class, "login")]'
            try:
                login_button = page.wait_for_selector(login_button_selector, timeout=10000)
                app.logger.info("Found login button, clicking...")
                login_button.click()
            except:
                app.logger.info("Login button not found, continuing...")
            
            page.wait_for_timeout(3000)
            
            qrcode_selector = '//img[contains(@src, "qrcode")] | //div[contains(@class, "qrcode")] | //canvas'
            try:
                qrcode_element = page.wait_for_selector(qrcode_selector, timeout=15000)
                app.logger.info("Found QR code element")
                
                login_status = 'waiting'
                qrcode_screenshot = page.screenshot()
                login_qrcode_base64 = base64.b64encode(qrcode_screenshot).decode('utf-8')
                app.logger.info("QR code captured")
            except Exception as e:
                app.logger.error(f"Failed to find QR code: {str(e)}")
                page.wait_for_timeout(2000)
                qrcode_screenshot = page.screenshot()
                login_qrcode_base64 = base64.b64encode(qrcode_screenshot).decode('utf-8')
                login_status = 'waiting'
            
            max_wait_time = 180
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                try:
                    cookies = context.cookies()
                    session_cookies = [c for c in cookies if c['name'] in ['sessionid', 'sid_guard', 'uid_tt', 'uid_tt_ss']]
                    
                    if len(session_cookies) >= 2:
                        app.logger.info("Login successful, saving cookies...")
                        cookie_string = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
                        
                        with open(app.config['COOKIES_FILE'], 'w', encoding='utf-8') as f:
                            f.write(cookie_string)
                        
                        login_status = 'success'
                        login_result = {'success': True, 'message': '登录成功'}
                        browser.close()
                        app.logger.info("Login completed successfully")
                        return
                    
                    page.wait_for_timeout(2000)
                    
                    if login_qrcode_base64:
                        try:
                            qrcode_screenshot = page.screenshot()
                            login_qrcode_base64 = base64.b64encode(qrcode_screenshot).decode('utf-8')
                        except:
                            pass
                            
                except Exception as e:
                    app.logger.error(f"Error during login polling: {str(e)}")
                    page.wait_for_timeout(2000)
            
            browser.close()
            login_status = 'timeout'
            login_result = {'success': False, 'message': '登录超时'}
            app.logger.warning("Login timeout")
            
    except Exception as e:
        app.logger.error(f"Login failed with exception: {str(e)}")
        login_status = 'error'
        login_result = {'success': False, 'message': f'登录失败: {str(e)}'}

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
                error_msg = '⚠️ 该视频需要登录才能下载'
        elif 'Fresh cookies' in error_msg:
            error_msg = '⚠️ 需要登录抖音账号才能下载此视频'
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
                error_msg = '⚠️ 该视频需要登录才能下载'
        elif 'Fresh cookies' in error_msg:
            error_msg = '⚠️ 需要登录抖音账号才能下载此视频'
        return jsonify({'error': error_msg}), 500

@app.route('/download/<filename>')
def serve_download(filename):
    safe = os.path.basename(filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], safe)
    if not os.path.isfile(path):
        return jsonify({'error': '文件不存在'}), 404
    return send_file(path, as_attachment=True)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=False)
