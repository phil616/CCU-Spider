import os
from bs4 import BeautifulSoup
from downloader import HtmlDownloader
from urllib.parse import urlparse
from global_kits import img_dict, link_dict


def imgPathGetter(baseurl, relative):
    """
    传入的baseurl有三种可能：
    1. 直接带文件名的  例如https://www.ccu.edu.cn/info/1024/3891.htm
    imgs. 带/开头的    /local/...
    3. 携带了GET请求的参数  /_visitcount?siteId=imgs&type=3&articleId=47663

    relative相对地址，用户可能传入的有两种可能
    1. 以/开头的，表示当前域的内容 例如 /__local/1/4C/80/5855E5CDDCD5105F871B3BB9DD5_24217D30_17A1D.jpg
        我们需要构建的链接是 ：域名 + relative,域名的形式必须要纯域名，例如www.ccu.edu.cn 后面不能跟其它东西
    imgs. 以相对路径标注的内容， ../.././资源名

    :param baseurl: baseurl for this page
    :param relative: relative src-content for this image
    :return:
    """
    basic = urlparse(baseurl)  # urlparse可以对传入的URL进行分析和解剖，返回的是一个对象
    protocol_name = basic.scheme  # 获取的是URL的协议名，比如http或者https
    host_name = basic.hostname  # 这里获取的是hostname，也就是域名，例如 www.ccu.edu.cn
    if str(relative).find('/') == 0:  # 如果相对路径是带有/开头的
        return protocol_name + "://" + host_name + relative
        #  http         ://    www.ccu.edu.cn + /url
    else:
        pre_url = str(baseurl).removesuffix('/')  # 将baseurl后面带有的/去掉
        """
        1.例如 pre_url =  https://www.ccu.edu.cn/info/1024/3891.htm/
        imgs.那么需要先变为    https://www.ccu.edu.cn/info/1024/3891.htm
        3.然后再将文件名去掉 https://www.ccu.edu.cn/info/1024/
        这时，才能将相对路径的内容直接拼接，且不出现错误
        """
        root = os.path.dirname(pre_url)  # 将目录名提取出来 对应上面的 3 步骤
        if root.find('/') > 0:
            return str(root) + "/" + str(relative)
        #
        # 如果传入的是 http://dsjy.ccu.edu.cn/，那么从左往右找/就会>0
        # 直接拼接
        # 如果不是，就用preurl拼接
        else:
            return str(pre_url) + "/" + str(relative)


def hrefPathGetter(baseurl, relative):
    protocol_name = urlparse(relative).scheme.upper()
    if protocol_name == "HTTP" or protocol_name == "HTTPS":
        return relative
    else:
        if relative == '#' or relative == "None":
            return
        else:
            return str(baseurl) + "/" + str(relative)


class Analyzer(object):
    HTML = ""  # HTML内容跟
    current_link = ""  # 当前链接
    base_url = ""  # 基础url
    downloaded_img = {}  # 已经下载的img文件
    img_link_list = []  # 储存的是图片链接内容，以列表形式储存，是当前页面所包含的所有图片链接
    href_link_list = []  # 储存的是能点进去的超链接内容，以列表形式储存，是当前页面所包含的所有链接
    objActive = False
    filter_pool = {}  # 过滤池

    def __init__(self):
        self.objActive = True

    def domain_filter(self, url):
        target = url
        # 判断传入的url是否再过滤池中，如果过滤池集合没有，就说明访问到了外链，不进行访问
        self.filter_pool.get(target)
        return True

    def update_link(self, link):
        html = HtmlDownloader()  # 新建一个HTML下载对象
        self.current_link = link  # 将用户传进来的link保存到成员变量当中
        html.DownloadLink(link)  # 下载该HTML界面
        # 下载HTML页面
        soup = BeautifulSoup(html.getHTML(), "html.parser")
        # html.getHTML()，HTML的文本内容， "html.parser"分析器传入
        # 构建DOM结构
        img_tags = soup.find_all('img')  # 寻找IMG标签
        hyper_link = soup.find_all('a')  # 寻找hyperlink标签

        for img in img_tags:  # 遍历IMG标签
            self.img_link_list.append(imgPathGetter(link, img.get('src')))

        for href in hyper_link:
            self.href_link_list.append(hrefPathGetter(link, href.get('href')))

    def sync_img(self):
        """
        把刚刚获取到的列表内容，更新到全局变量中
        下载器就可以进行下载
        :return:
        """
        for i in self.img_link_list:
            if self.domain_filter(i) is False:
                return
            try:
                if img_dict[i] is True or img_dict[i] is False:
                    continue
            except KeyError as e:
                img_dict.update({str(i): False})

    def sync_link(self):
        """
        把刚刚获取到的列表内容，更新到全局变量中
        下载器就可以进行下载
        :return:
        """
        for i in self.href_link_list:
            if self.domain_filter(i) is False:
                return
            try:
                if link_dict[i] is True or link_dict[i] is False:
                    continue
            except KeyError as e:
                link_dict.update({str(i): False})

    def get_level(self):
        return str(2)
