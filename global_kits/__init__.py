"""
LOGGER
"""
import logging

# 引用了logging作为日志模块
Logger = logging.getLogger("CCUSpider_Logger")
# 日志名称为"CCUSpider_Logger"
file_handler = logging.FileHandler("RuntimeLog", encoding="utf-8")  # 向文件输出的日志对象
# meta log format: unit = [space]%s\t|
fmt = logging.Formatter(" %(asctime)s\t| %(levelname)s\t| %(name)s\t| %(message)s\t")
# 格式化要输出内容的格式：  日期 | 层级名
stream_handler = logging.StreamHandler()  # 向控制台输出的日志对象
file_handler.setFormatter(fmt)
stream_handler.setFormatter(fmt)
Logger.addHandler(file_handler)
Logger.addHandler(stream_handler)
Logger.setLevel("DEBUG")  # 设置需要记录的等级，只记录比这个严重的日志等级
# 低于这个等级的内容都会被忽略

"""
CONTROLLER PART
"""
MAX_SEARCH_LAYERS = 2  # 最大搜索层数 （广义的BFS层数）
"""
SIGNALS
"""
SIG_DOWNLOADING = False
SIG_CONTROLLER = False
"""
SYNC DICT
"""
img_dict = {}
"""
img_dict要保存的是图片资源链接
结构是：
{
    {img_url: bool}, 
    # img_url是获取到的图片链接，bool如果是True,
    # 说明该链接的图片已经被下载过了，反之没被下载
    {img_url: bool},
    {img_url: bool},
    ...
}
"""

link_dict = {}
"""
link_dict要保存的是链接资源
结构和上面一样
"""

"""
THREADING LOCKS
"""
IMG_DICT_LOCK = False
LINK_DICT_LOCK = False
ACTIVE_LOCKS = False


def setControl():
    global SIG_CONTROLLER  # 引入信号
    SIG_CONTROLLER = ~SIG_CONTROLLER  # 将信号反转


def setDownloading():
    global SIG_DOWNLOADING
    SIG_DOWNLOADING = ~SIG_DOWNLOADING
