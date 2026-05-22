import os

download_path = "G:/trae/视频下载网站/downloads"

print(f"检查下载目录: {download_path}")
print(f"目录是否存在: {os.path.exists(download_path)}")

if os.path.exists(download_path):
    files = os.listdir(download_path)
    print(f"\n目录内容 ({len(files)} 个文件):")
    for f in files:
        fp = os.path.join(download_path, f)
        if os.path.isfile(fp):
            size = os.path.getsize(fp)
            print(f"  {f} - {size} bytes")
        elif os.path.isdir(fp):
            subfiles = os.listdir(fp)
            print(f"  {f}/ - 包含 {len(subfiles)} 个文件")
else:
    print("目录不存在")
