from flask import Flask, jsonify, request, send_file, redirect
import os
import uuid

app = Flask(__name__)

APP_VERSION = 'v3.0.0'
app.config['UPLOAD_FOLDER'] = os.environ.get('DOWNLOAD_DIR', '/app/downloads')
app.config['PORT'] = int(os.environ.get('PORT', 8787))

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 延迟导入 douyin_downloader
downloader = None
DOUYIN_DOWNLOADER_AVAILABLE = False

try:
    from douyin_downloader import DouyinDownloader
    downloader = DouyinDownloader()
    DOUYIN_DOWNLOADER_AVAILABLE = True
    print("✓ douyin_downloader 库加载成功")
except ImportError as e:
    print(f"✗ 无法加载 douyin_downloader: {e}")
    print("  请安装: pip install git+https://github.com/jiji262/douyin-downloader.git")

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/version')
def get_version():
    return jsonify({
        'version': APP_VERSION,
        'backend': 'douyin-downloader',
        'playwright': False,
        'douyin_downloader': DOUYIN_DOWNLOADER_AVAILABLE
    })

@app.route('/api/parse', methods=['POST'])
def parse_url():
    if not DOUYIN_DOWNLOADER_AVAILABLE:
        return jsonify({'success': False, 'message': 'douyin_downloader 库未安装'})
    
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
            return jsonify({'success': False, 'message': '解析失败，请检查链接是否有效'})
    
    except Exception as e:
        app.logger.error(f"解析失败: {str(e)}")
        return jsonify({'success': False, 'message': f'解析失败: {str(e)}'})

@app.route('/api/download', methods=['POST'])
def download_video():
    if not DOUYIN_DOWNLOADER_AVAILABLE:
        return jsonify({'success': False, 'message': 'douyin_downloader 库未安装'})
    
    try:
        data = request.get_json()
        url = data.get('url', '')
        
        if not url:
            return jsonify({'success': False, 'message': '请提供下载链接'})
        
        filename = downloader.download(url, save_path=app.config['UPLOAD_FOLDER'])
        
        if filename and os.path.exists(filename):
            return jsonify({
                'success': True,
                'filename': os.path.basename(filename),
                'download_url': f'/download/{os.path.basename(filename)}'
            })
        else:
            return jsonify({'success': False, 'message': '下载失败'})
    
    except Exception as e:
        app.logger.error(f"下载失败: {str(e)}")
        return jsonify({'success': False, 'message': f'下载失败: {str(e)}'})

@app.route('/download/<filename>')
def serve_download(filename):
    try:
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)
    except Exception as e:
        app.logger.error(f"文件下载失败: {str(e)}")
        return jsonify({'success': False, 'message': '文件不存在'}), 404

@app.route('/api/direct-download', methods=['GET'])
def direct_download():
    if not DOUYIN_DOWNLOADER_AVAILABLE:
        return jsonify({'success': False, 'message': 'douyin_downloader 库未安装'}), 500
    
    url = request.args.get('url', '')
    if not url:
        return jsonify({'success': False, 'message': '缺少url参数'}), 400
    
    try:
        filename = downloader.download(url, save_path=app.config['UPLOAD_FOLDER'])
        
        if filename and os.path.exists(filename):
            return send_file(filename, as_attachment=True)
        else:
            return jsonify({'success': False, 'message': '下载失败'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/quick-download', methods=['POST'])
def quick_download():
    if not DOUYIN_DOWNLOADER_AVAILABLE:
        return jsonify({'success': False, 'message': 'douyin_downloader 库未安装'}), 500
    
    data = request.get_json()
    url = data.get('url', '')
    
    if not url:
        return jsonify({'success': False, 'message': '缺少url参数'}), 400
    
    try:
        result = downloader.parse(url)
        
        if result:
            video_url = result.get('video_url', '')
            if video_url:
                return jsonify({
                    'success': True,
                    'video_url': video_url,
                    'title': result.get('title', ''),
                    'author': result.get('author', '')
                })
            else:
                return jsonify({'success': False, 'message': '未找到视频链接'})
        else:
            return jsonify({'success': False, 'message': '解析失败'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=True)