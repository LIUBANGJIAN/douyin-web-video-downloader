import json
import os

def update_cookies():
    cookies_path = "G:/trae/视频下载网站/.cookies.json"
    
    # 示例 cookies（需要用户从浏览器获取真实的 cookies）
    cookies = {
        "ttwid": "替换为你的 ttwid",
        "odin_tt": "替换为你的 odin_tt",
        "passport_csrf_token": "替换为你的 passport_csrf_token"
    }
    
    with open(cookies_path, 'w', encoding='utf-8') as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)
    
    print(f"Cookies 文件已更新: {cookies_path}")
    print("请从浏览器获取真实的 cookies 并更新此文件")
    print("\n获取方法:")
    print("1. 打开浏览器登录抖音网页版")
    print("2. F12 打开开发者工具")
    print("3. 切换到 Application → Cookies → https://www.douyin.com")
    print("4. 复制 ttwid, odin_tt, passport_csrf_token 的值")

if __name__ == "__main__":
    update_cookies()
