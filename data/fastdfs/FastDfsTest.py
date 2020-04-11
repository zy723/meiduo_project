from fdfs_client.client import Fdfs_client

# 导入配置文件：
# 注意：windows环境下绝对路径会发生转义，需要加上 "r" 说明是原生字符串
client = Fdfs_client(r'client.conf')

# 上传图片：
# 注意：windows环境下绝对路径会发生转义，需要加上 "r" 说明是原生字符串
conf = client.upload_by_filename(r'E:\Document And Settings2\zy\Desktop\收款码.png')
print(conf)

# 192.168.0.169:8888/group1/M00/00/00/wKgAqV6RYJWAS677AABtCxL_mKk331.png
