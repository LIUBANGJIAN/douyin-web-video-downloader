"""抖音 Cookie：二维码登录、写入 Evil0ctal 配置、健康检查。"""
import base64
import os
import re
import threading
import time

import requests
import yaml

CONFIG_PATH = os.environ.get('DOUYIN_CONFIG_PATH', '/data/douyin/config.yaml')
DOUYIN_API_URL = os.environ.get('DOUYIN_API_URL', '').rstrip('/')
TEST_URL = os.environ.get(
    'DOUYIN_COOKIE_TEST_URL',
    'https://v.douyin.com/MpeyIZyxMTA/',
)
CHECK_INTERVAL = int(os.environ.get('COOKIE_CHECK_INTERVAL', '300'))


def _get_api_urls():
    if DOUYIN_API_URL:
        yield DOUYIN_API_URL
        return

    yield 'http://127.0.0.1:80'
    yield 'http://127.0.0.1:8080'
    yield 'http://localhost:80'
    yield 'http://localhost:8080'
    yield 'http://douyin-api:80'


def _request_douyin_api(path, params=None):
    errors = []
    for base_url in _get_api_urls():
        url = f'{base_url}{path}'
        try:
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as exc:
            errors.append(f'{base_url}: {exc}')
            if DOUYIN_API_URL:
                break

    raise RuntimeError(
        '解析服务不可用，请检查 DOUYIN_API_URL 或后端服务是否已启动。'
        f' 尝试地址: {", ".join(_get_api_urls())}; 错误: {" | ".join(errors)}'
    )


def _post_douyin_api(path, json_data=None):
    errors = []
    for base_url in _get_api_urls():
        url = f'{base_url}{path}'
        try:
            resp = requests.post(url, json=json_data, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as exc:
            errors.append(f'{base_url}: {exc}')
            if DOUYIN_API_URL:
                break

    raise RuntimeError(
        '后端更新 Cookie 失败，请检查 DOUYIN_API_URL 或后端服务是否已启动。'
        f' 尝试地址: {", ".join(_get_api_urls())}; 错误: {" | ".join(errors)}'
    )


def _sync_cookie_to_backend(cookie_header):
    body = _post_douyin_api(
        '/api/hybrid/update_cookie',
        json_data={'service': 'douyin', 'cookie': cookie_header},
    )
    code = body.get('code', body.get('status_code', 0))
    if code not in (200, '200', 0):
        raise RuntimeError(body.get('message') or body.get('msg') or f'API 错误: {code}')
    return True

_lock = threading.Lock()
_status = 'checking'  # checking | valid | invalid | scanning
_qr_base64 = ''
_message = ''
_login_thread = None


def _ensure_config_dir():
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)


def _load_config():
    if not os.path.isfile(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def _save_config(config_data):
    _ensure_config_dir()
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config_data, f, allow_unicode=True, sort_keys=False)


def _load_template_config():
    template_path = os.path.join(os.path.dirname(__file__), 'douyin_config_template.yaml')
    if not os.path.isfile(template_path):
        return {}
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def _get_cookie_header_from_config(config_data):
    if not isinstance(config_data, dict):
        return ''
    cookie = config_data.get('Cookie')
    if cookie:
        return str(cookie).strip()
    token_manager = config_data.get('TokenManager', {})
    if not isinstance(token_manager, dict):
        return ''
    douyin_config = token_manager.get('douyin', {})
    if not isinstance(douyin_config, dict):
        return ''
    headers = douyin_config.get('headers', {})
    if not isinstance(headers, dict):
        return ''
    return str(headers.get('Cookie') or '').strip()


def _cookies_to_header(cookies):
    parts = []
    for c in cookies:
        domain = c.get('domain', '')
        if 'douyin' not in domain and domain not in ('', '.douyin.com'):
            continue
        name = c.get('name', '')
        value = c.get('value', '')
        if name and value is not None:
            parts.append(f'{name}={value}')
    return '; '.join(parts)


def _write_config(cookie_header):
    config_data = _load_config()
    template = _load_template_config()

    if not isinstance(config_data.get('TokenManager'), dict):
        config_data = template if isinstance(template, dict) else {}

    token_manager = config_data.setdefault('TokenManager', {})
    if not isinstance(token_manager, dict):
        token_manager = {}
        config_data['TokenManager'] = token_manager

    douyin_config = token_manager.setdefault('douyin', {})
    if not isinstance(douyin_config, dict):
        douyin_config = {}
        token_manager['douyin'] = douyin_config

    headers = douyin_config.setdefault('headers', {})
    if not isinstance(headers, dict):
        headers = {}
        douyin_config['headers'] = headers

    headers['Cookie'] = cookie_header
    config_data.pop('Cookie', None)
    _save_config(config_data)


def _read_cookie_header():
    config_data = _load_config()
    return _get_cookie_header_from_config(config_data)


def _test_cookie_with_api():
    cookie = _read_cookie_header()
    if not cookie or len(cookie) < 20:
        return False, '未配置 Cookie'
    try:
        body = _request_douyin_api(
            '/api/hybrid/video_data',
            params={'url': TEST_URL, 'minimal': 'true'},
        )
        code = body.get('code', body.get('status_code', 0))
        if code in (200, '200', 0):
            return True, 'Cookie 有效'
        msg = body.get('message') or body.get('msg') or str(body)[:200]
        if 'cookie' in str(msg).lower():
            return False, 'Cookie 已失效'
        return False, msg
    except Exception as e:
        return False, f'解析服务不可用: {e}'


def get_status():
    with _lock:
        return {
            'status': _status,
            'qrCode': _qr_base64,
            'message': _message,
            'hasCookie': bool(_read_cookie_header()),
        }


def check_validity(force=False):
    global _status, _message
    with _lock:
        if _status == 'scanning' and not force:
            return get_status()
        _status = 'checking'
        _message = '正在检查 Cookie...'

    ok, msg = _test_cookie_with_api()
    with _lock:
        _status = 'valid' if ok else 'invalid'
        _message = msg
    return get_status()


def _run_qr_login():
    global _status, _qr_base64, _message
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        with _lock:
            _status = 'invalid'
            _message = '未安装 Playwright，请重新构建 Docker 镜像'
            _qr_base64 = ''
        return

    try:
        print('[cookie_manager] QR login start')
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--no-zygote', '--single-process'],
            )
            print('[cookie_manager] browser launched')
            context = browser.new_context(
                user_agent=(
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
                ),
                viewport={'width': 1280, 'height': 900},
                locale='zh-CN',
                ignore_https_errors=True,
            )
            page = context.new_page()
            try:
                page.goto('https://www.douyin.com/login', wait_until='domcontentloaded', timeout=60000)
                print('[cookie_manager] navigated to login page', page.url)
            except Exception as e:
                print('[cookie_manager] login page navigation failed:', e)
                page.goto('https://www.douyin.com/', wait_until='domcontentloaded', timeout=60000)
                print('[cookie_manager] fallback to homepage', page.url)
            time.sleep(5)

            clicked = False
            for text in ('登录', '扫码登录', 'QR Code', '二维码'):
                try:
                    locator = page.get_by_text(text, exact=False)
                    if locator.count() > 0:
                        locator.first.click(timeout=3000)
                        time.sleep(2)
                        clicked = True
                        print(f'[cookie_manager] clicked login text: {text}')
                        break
                except Exception as e:
                    print(f'[cookie_manager] click text "{text}" failed: {e}')
                    continue

            if not clicked:
                print('[cookie_manager] did not click login button, continuing to screenshot')

            time.sleep(3)
            png = None
            selectors = [
                'img[src*="qr"]',
                '.login-qrcode img',
                'div[class*="qrcode"] img',
                'canvas',
                'img[src*="qrcode"]',
                'svg',
            ]
            for sel in selectors:
                try:
                    el = page.wait_for_selector(sel, timeout=5000)
                    if el:
                        png = el.screenshot(type='png')
                        print(f'[cookie_manager] captured qr through selector: {sel}')
                        break
                except Exception as e:
                    print(f'[cookie_manager] selector {sel} failed: {e}')
                    continue

            if not png:
                print('[cookie_manager] no qr selector matched, trying fallback screenshot')
                panel = page.query_selector('div[class*="login"]') or page.query_selector('div[class*="qr"]')
                png = panel.screenshot(type='png') if panel else page.screenshot(type='png')
                print('[cookie_manager] fallback screenshot done', 'panel' if panel else 'full page')

            with _lock:
                _qr_base64 = base64.b64encode(png).decode('ascii')
                _message = '请使用抖音 App 扫描二维码登录'

            logged_in = False
            for _ in range(180):
                cookies = context.cookies()
                names = {c.get('name', '') for c in cookies}
                if names & {'sessionid', 'sid_tt', 'uid_tt', 'passport_csrf_token'}:
                    header = _cookies_to_header(cookies)
                    if len(header) > 50:
                        _write_config(header)
                        try:
                            _sync_cookie_to_backend(header)
                            logged_in = True
                        except Exception as sync_exc:
                            print('[cookie_manager] sync cookie to backend failed:', sync_exc)
                            with _lock:
                                _status = 'invalid'
                                _qr_base64 = ''
                                _message = f'登录成功，Cookie 已保存，但无法同步到后端：{sync_exc}'
                            browser.close()
                            return
                        break
                time.sleep(1)

            browser.close()

            with _lock:
                if logged_in:
                    _status = 'valid'
                    _qr_base64 = ''
                    _message = '登录成功，Cookie 已更新'
                else:
                    _status = 'invalid'
                    _qr_base64 = ''
                    _message = '扫码超时或失败，请重试'

    except Exception as e:
        print('[cookie_manager] QR login failed:', e)
        with _lock:
            _status = 'invalid'
            _qr_base64 = ''
            _message = f'二维码登录失败: {e}'


def start_qr_login():
    global _login_thread, _status, _qr_base64, _message
    with _lock:
        if _status == 'scanning':
            return get_status()
        if _login_thread and _login_thread.is_alive():
            return get_status()
        _status = 'scanning'
        _qr_base64 = ''
        _message = '正在生成二维码...'

    _login_thread = threading.Thread(target=_run_qr_login, daemon=True)
    _login_thread.start()
    return get_status()


def start_monitor():
    def loop():
        time.sleep(10)
        while True:
            try:
                st = get_status()
                if st['status'] != 'scanning':
                    check_validity()
            except Exception:
                pass
            time.sleep(CHECK_INTERVAL)

    threading.Thread(target=loop, daemon=True).start()
