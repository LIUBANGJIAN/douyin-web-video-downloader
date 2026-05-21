# 简单测试脚本
print("测试输出 1")
print("测试输出 2")

# 写入文件
with open('test_output.txt', 'w') as f:
    f.write("测试文件内容\n")
    f.write("这是一个测试\n")

print("测试完成")