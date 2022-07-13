from controller import Controller
from global_kits import link_dict, MAX_SEARCH_LAYERS, ACTIVE_LOCKS, LINK_DICT_LOCK
from analyzer import Analyzer

al = Analyzer()
al.update_link("https://www.ccu.edu.cn/")
al.sync_img()
al.sync_link()

for i in link_dict.copy():
    al.update_link(i)
    al.sync_img()
    al.sync_link()


col = Controller()
col.ImgDownloadAll(al.get_level())

