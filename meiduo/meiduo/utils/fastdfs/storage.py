from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings
from django.utils.deconstruct import deconstructible


@deconstructible
class FdfsStorage(Storage):
    def open(self, name, mode='rb'):
        pass

    def save(self, name, content, max_length=None):
        # content:请求报文中的文件对象
        # 创建一个fastDFS类的对象
        fdfs_client = Fdfs_client(settings.FDFS_CLIENT_CONF)
        # 读取请求报文中的文件对象，将来只要django里面用imagefield字段，这里就会自动读取
        # 这里就是上传文件到fastdfs了，然后给我们返回一个存在远程的文件名字
        ret = fdfs_client.upload_by_buffer(content.read())
        if ret['Status'] != 'Upload successed.':
            raise Exception('文件保存失败')
        return ret['Remote file_id']

    def exists(self, name):
        return False

    def url(self, name):
        return settings.FDFS_URL + name
