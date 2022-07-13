from downloader import ImgDownloader
from global_kits import setControl, setDownloading, img_dict
from urllib.parse import urlparse


class Controller(object):
    def __init__(self):
        setControl()  # 每次这个对象被建立出来，就将setControl 翻转
        # 只能有一个控制器
        # 如有有两个控制器，也只有一个能够使用变量

    def ImgDownloadAll(self, path):
        setDownloading()  # 设置当前正在执行下载操作的信号
        dlr = ImgDownloader()   # 创建一个图片下载器对象
        tempDict = img_dict.copy().keys()
        for i in tempDict:   # 遍历的是所有的全局img字典
            dlr.setUrl(i)           # img链接本身作为url传进去
            dlr.setSavePath(path)   # 传入的路径是用户给定的
            filename = urlparse(i).netloc + str(urlparse(i).path).replace('/', '-')
                        # 网络 + 路径（被替换过的路径）
            # https://www.ccu.edu.cn/info/1024/3891.htm
            # https:--www.ccu.edu.cn-info-1024-3891.htm
            dlr.setFileName(filename)
            # 再将文件名传入
            dlr.activeDownload()
            # 开始下载
        setDownloading()  # 信号还原
