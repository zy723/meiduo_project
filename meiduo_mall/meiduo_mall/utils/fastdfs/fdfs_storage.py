from django.conf import settings
from django.core.files.storage import Storage


class FastDFSStorage(Storage):
    """
    自定义文件存储类
    """

    def __init__(self, fdfs_base_url=None):
        """
        文件存储类的初始方法
        """
        self.fdfs_base_url = fdfs_base_url or settings.FDFS_BASE_URL

    def _open(self, name, mode='rb'):
        """
        打开文件时候被掉用, 文档指明必须重写该方法
        :param name: 文件路径
        :param mode: 文件打开方式
        :return:
        """
        pass

    def _save(self, name, content):
        """
        PS：将来后台管理系统中，需要在这个方法中实现文件上传到FastDFS服务器
        保存文件时会被调用的：文档告诉我必须重写
        :param name: 文件路径
        :param content: 文件二进制内容
        :return: None
        """
        pass

    def url(self, name):
        """
        返回文件的全路径
        :param name: 文件的相对路径
        :return: 文件的全路径名 eg:http://192.168.103.158:8888/group1/M00/00/00/wKhnnlxw_gmAcoWmAAEXU5wmjPs35.jpeg
        """
        return self.fdfs_base_url + name
