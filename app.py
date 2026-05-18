from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
import uuid
import re

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = os.environ.get('DOWNLOAD_DIR', '/app/downloads')
app.config['PORT'] = int(os.environ.get('PORT', 8787))

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return send_file('index.html')

def extract_url(text):
    url_pattern = r'https?://[^\s]+'
    match = re.search(url_pattern, text)
    if match:
        return match.group(0).rstrip('.,')
    return text.strip()

@app.route('/api/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        url = data.get('url', '')
        
        if not url:
            return jsonify({'error': '请输入视频链接'}), 400
        
        clean_url = extract_url(url)
        
        if not clean_url:
            return jsonify({'error': '无法从文本中提取有效的视频链接'}), 400
        
        video_id = str(uuid.uuid4())
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{video_id}.%(ext)s')
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=True)
            
            video_title = info.get('title', '视频')
            video_ext = info.get('ext', 'mp4')
            video_file = os.path.join(app.config['UPLOAD_FOLDER'], f'{video_id}.{video_ext}')
            video_thumbnail = info.get('thumbnail', '')
            
            if os.path.exists(video_file):
                return jsonify({
                    'success': True,
                    'videoUrl': f'/download/{video_id}.{video_ext}',
                    'title': video_title,
                    'author': info.get('uploader', ''),
                    'ext': video_ext,
                    'thumbnail': video_thumbnail
                })
            else:
                return jsonify({'error': '视频下载失败'}), 500
                
    except Exception as e:
        error_msg = str(e)
        return jsonify({'error': error_msg}), 500

@app.route('/download/<filename>')
def serve_download(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=True)