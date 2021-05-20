from fdfs_client.client import Fdfs_client

if __name__ == '__main__':
    client = Fdfs_client('client.conf')
    ret = client.upload_by_file('/home/python/Pictures/Wallpapers/1.jpg')
    print(ret)