import os
import requests
from global_kits import Logger
from global_kits import img_dict, link_dict, MAX_SEARCH_LAYERS
from requests.adapters import HTTPAdapter
from database import SqlServer
import base64

conf = {
    "mysql": {
        "user": "root",
        "passwd": "Carvinte616",
        "hostname": "localhost",
        "port": "3306",
        "charset": "utf-8",
        "database": "spider"
    }
}

G_SQL = SqlServer("conf.json")


class ImgDownloader(object):
    __target_url = ""
    __header = {}
    __save_path = ""
    __base64 = ""
    __filename = ""
    __active_signal = False
    __fileinfo = {}
    __base_path = ""
    __html = ""
    __file_suffix = ""

    def __init__(self):
        self.__fileinfo.update({"filename": ""})  # 不重要的
        self.__fileinfo.update({"filesize(kb)": "0"})  # 不重要的
        self.__base_path = os.getcwd()  # 获取当前路径
        self.__save_path = "img"  # 设置默认图片的保存路径

    def setUrl(self, url):
        self.__file_suffix = os.path.splitext(url)[-1]
        # 从URL中取后缀， 例如URL为：https://ccu.edu.cn/img/123.png ,那么self.__file_suffix就会是.png
        self.__target_url = str(url)
        # __target_url为未经改动过的url

    def setHeader(self, header):
        # 如果下载资源时，需要进行用户鉴定（鉴权）
        # header可以使用用户传递的cookie来进行包装
        if isinstance(header, dict):
            self.__header.update(header)
        else:  # 如果用户传递的值不是字典形式，那就无法发送，抛出错误
            raise Exception("Header should be a dict type")

    def setSavePath(self, path):
        #  self.__base_path + "\\" + str(path)
        #  系统当前运行的目录   + '\\' + path参数
        #  形式是 c:\\img\\path

        # os.path.exists判断上述文件夹是否存在，返回的是布尔值
        # 如果返回True,就说明目标文件夹存在，直接将路径写到self.__save_path中
        if os.path.exists(self.__base_path + "\\" + str(path)) is False:
            # 如果为False，系统找不到目标文件夹，就会使用os.mkdir来创建出新的文件夹
            os.mkdir(self.__base_path + "\\" + str(path))  # 全路径
        self.__save_path = str(path)  # 全路径

    def setFileName(self, name):
        # 若用户传进来的是文件的全名，则使用分隔符将文件名提取出来
        # name.split('.')[0]
        self.__filename = name

    def activeDownload(self):
        try:
            s = requests.Session()
            # 新建一个会话 ： request会话
            s.mount("http://", HTTPAdapter(max_retries=2))
            # 挂载一个设置：要求使用HTTP协议，最大尝试次数为2次
            s.mount("https://", HTTPAdapter(max_retries=2))
            # 挂载一个设置：要求使用HTTPS协议，最大尝试次数为2次
            r = s.get(self.__target_url, timeout=1)
            # 发送一个GET请求，最大时间为1s，如果超过1s，就放弃请求
        except Exception as e:
            Logger.warning(e)  # 如果上述的代码块出现错误，捕获错误之后，打印日志
            return

        try:
            if img_dict[r.url]:  # r.url是请求访问的链接，如果这个链接在img_dict能成功访问得到，且为True，就说明已经下载过了
                Logger.info("IMG Repeat skip: " + r.url)  # 写日志：已经下载过的，就不进行重复下载，跳过
                return
        except KeyError as e:  # 如果r.url连访问都没有访问到，就会抛出KeyError，说明字典里根本没有这个链接，更没下载过
            img_dict.update({str(r.url): False})  # 将没被下载过的链接，插入到字典中，因为还没有进行下载，赋值为False

        filename = self.__base_path + "\\" + self.__save_path + "\\" + self.__filename + self.__file_suffix  # 后缀名
        #          self.__base_path 当前系统路径，由系统提供
        #                                    self.__save_path 保存的文件夹名，由用户提供
        #                                                              self.__filename 也由用户提供，是下载到文件夹内的文件名
        # 1.保存路径 filename
        # imgs.保存url   self.__target_url
        # 3.保存base64 r.content -> base64
        # 4.保存文件名 self.__filename
        conn = r.content
        res = base64.b64encode(conn)

        sql = """
        INSERT INTO `data` (path, url, base, filename)VALUES (\'%s\',\'%s\',\'%s\',\'%s\',)
        """ % (
            filename, self.__target_url, res, self.__filename
        )
        # G_SQL.sql_post(sql)
        try:
            with open(filename, "wb+") as f:  # 用open以二进制形式打开一下,f是对象的指针，对应了C语言里面的FILE指针，被封装为文件对象
                f.write(conn)  # 使用f的write方法写入到本地磁盘， r是请求的对象，content是字节流形式， 已经下载成功
                img_dict.update({str(r.url): True})  # 将下载成功的url，在字典中更新为True，表示这个文件已经被成功下载
                Logger.info(filename + " Downloaded From URL: " + self.__target_url)  # 写日志，从某某某下载
        except Exception as e:
            Logger.warning(e)
            return


class HtmlDownloader(object):
    link = ""  # HTML的url
    html_content = ""  # HTML的内容
    __header = {}

    def DownloadLink(self, url):  # 这个下载方法要求传入url
        self.link = str(url)  # 将自身的成员变量赋值为url
        try:
            if link_dict[url]:  # 尝试访问url，如果为true，就说明访问过，写日志，跳过本次
                Logger.info("LINK Repeat skip: " + url)
                return
        except KeyError as e:
            link_dict.update({str(url): False})  # 没有下载过，就插入等待下载

        try:
            s = requests.Session()  # 获取会话
            s.mount("http://", HTTPAdapter(max_retries=2))  # 允许HTTP
            s.mount("https://", HTTPAdapter(max_retries=2))  # 允许HTTPS
            r = s.get(self.link, headers=self.__header, timeout=1)  # 获取到对象
            r.encoding = r.apparent_encoding  # 转码，转为utf-8
        except Exception as e:  # 没获取到，报错，写日志
            Logger.warning(e)
            return

        self.html_content = r.text  # 将成员变量赋值，为文本形式
        link_dict.update({str(r.url): True})  # 标为true表示已经下载过改链接（这个URL已经被访问过）
        Logger.info(str("AT:") + str(MAX_SEARCH_LAYERS) + " Downloaded HTML : " + url)
        # 标记当前递归所在的层数

    def setHeader(self, header):
        # 如果下载资源时，需要进行用户鉴定（鉴权）
        # header可以使用用户传递的cookie来进行包装
        if isinstance(header, dict):
            self.__header.update(header)
        else:  # 如果用户传递的值不是字典形式，那就无法发送，抛出错误
            raise Exception("Header should be a dict type")

    def getHTML(self):
        return self.html_content  # 获取当前对象的HTML内容，以便其他逻辑使用
