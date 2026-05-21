import sys
import os

os.environ['FLASK_ENV'] = 'production'

from app import app

if __name__ == '__main__':
    port = app.config['PORT']
    print(f"启动服务器在端口 {port}...")
    app.run(host='0.0.0.0', port=port, threaded=True, use_reloader=False)