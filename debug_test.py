import requests
import re

MOBILE_UA = 'Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile Safari/537.36'

def test_short_url():
    """测试短链接解析"""
    url = 'https://v.douyin.com/MpeyIZyxMTA/'
    
    print(f"测试链接: {url}")
    
    # 提取token
    match = re.search(r'v\.douyin\.com/([a-zA-Z0-9_-]+)', url)
    if match:
        token = match.group(1)
        print(f"提取的token: {token}")
        
        # 尝试解析短链接
        headers = {'User-Agent': MOBILE_UA}
        try:
            response = requests.get(f'https://v.douyin.com/{token}/', headers=headers, allow_redirects=True, timeout=15)
            print(f"HTTP状态码: {response.status_code}")
            print(f"重定向后的URL: {response.url}")
            
            # 检查是否包含视频ID
            video_match = re.search(r'/video/(\d+)', response.url)
            if video_match:
                print(f"提取到视频ID: {video_match.group(1)}")
                return video_match.group(1)
            else:
                print("未找到视频ID")
                print(f"响应内容前500字符: {response.text[:500]}")
                
        except Exception as e:
            print(f"请求失败: {e}")
    else:
        print("无法提取token")
    
    return None

def test_api(aweme_id):
    """测试API获取视频信息"""
    if not aweme_id:
        print("没有视频ID，无法测试API")
        return
    
    headers = {
        'User-Agent': MOBILE_UA,
        'Accept': 'application/json',
        'Referer': 'https://www.douyin.com/',
    }
    
    api_url = f'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={aweme_id}'
    print(f"API URL: {api_url}")
    
    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        print(f"API状态码: {response.status_code}")
        print(f"API响应: {response.text[:1000]}")
        
        data = response.json()
        if data.get('status_code') == 0 and data.get('item_list'):
            print("API返回成功")
        else:
            print("API返回失败")
            
    except Exception as e:
        print(f"API请求失败: {e}")

if __name__ == '__main__':
    print("="*50)
    print("测试短链接解析")
    print("="*50)
    aweme_id = test_short_url()
    
    print("\n" + "="*50)
    print("测试API获取视频信息")
    print("="*50)
    test_api(aweme_id)