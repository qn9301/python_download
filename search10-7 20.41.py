# -*-coding:utf-8-*-
from bs4 import BeautifulSoup
import requests
import re
import os
import urllib
import shutil
# 在代码中使用html.text时用于解决下载的文件乱码的问题
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

'''
功能：传入域名，对网站进行整个下载
功能：根据href的域名进行文件夹的创建
正则匹配标签里的href和src
每次得到href的时候，要做缓存，判断是否进入过这个页面
'''
# 保存已经进入的超链接
hasindex = ['http://blog.hwmorelove.com/']
replace_hrefs = []
nums = 0
# 主函数
def get_content(url):
    html = requests.get(url)
    p = get_host(url)
    content = str(html.content)
    # 这里需要将文件中的超链接的地址都进行下载，这里要使用递归
    hrefs = get_all_href(content, p["host"])
    # 要将本域名下的所有东西都改成相对路径把域名更换成相对路径
    content = replace_all_hrefs(content, hrefs, p["host"])
    check_create_folder(p, content)
    # 下载脚本文件和图片
    hrefso = hrefs["js"] + hrefs["css"] + hrefs["img"]
    for j in hrefso:
        if j:
            # print j
            o = get_host(j)
            ohtml = requests.get(j,verify=False)
            ocontent = str(ohtml.content)
            check_create_folder(o,ocontent)
    # 开始递归
    for i in hrefs["a"]:
        if i:
            get_content(i)
    # return True

# 匹配文件中的所有超链接，只匹配递归a标签中的页面
def get_all_href(content,host):
    # 初始化链接的容器，把a标签中需要递归的链接和其他不需要递归的链接分离
    hrefs = {}
    hrefs["a"] = []  # a标签中的链接
    hrefs["js"] = []  # 其他的链接，包括js、css、img
    hrefs["css"] = []  # 其他的链接，包括js、css、img
    hrefs["img"] = []  # 其他的链接，包括js、css、img
    soup = BeautifulSoup(content,"lxml")
    As = soup.find_all("a")
    for item in As:
        # 得到每一个超链接
        i = str(item["href"])
        # 得到可以递归的超链接超链接
        i = deal_hrefs(i,host)
        if i:
            hrefs["a"].append(i)
    Links = soup.find_all("link",attrs={"rel":"stylesheet"})
    Scripts = soup.find_all("script")
    Imgs = soup.find_all("img")
    for item in Links:
        if re.search("^(//)",item["href"]):
            ihref = re.subn("^(//)","http://",item["href"])
            ihref = ihref[0]
        else:
            ihref = item["href"]
        if ihref in hasindex:
            continue
        else:
            hrefs["css"].append(ihref)
            hasindex.append(ihref)
            h = rule_of_url_replace(ihref, "css")
            replace_hrefs.append(h)
    for item in Scripts:
        if not item.string:
            if item["src"] in hasindex:
                continue
            else:
                hrefs["js"].append(item["src"])
                hasindex.append(item["src"])
                h = rule_of_url_replace(item["src"], "js")
                replace_hrefs.append(h)
    for item in Imgs:
        if item["src"] in hasindex:
            continue
        else:
            hrefs["img"].append(item["src"])
            hasindex.append(item["src"])
            h = rule_of_url_replace(item["src"], "img")
            replace_hrefs.append(h)
    return hrefs

# 处理超链接，删除里面的锚点，将/aaa这种绝对路径加上域名
def deal_hrefs(href,host):
    href = re.subn("^("+ host +"/|/)",host+"/",href)
    if href[1]:
        if href[0] not in hasindex:
            # 储存被列入访问的链接地址
            hasindex.append(href[0])
            return href[0]

# 创建文件夹的函数
def check_create_folder(info,str):
    # 判断是否有这个文件，没有就创建
    # 如果路径是/表示当前文件夹下，直接创建文件
    if info["path"]:
        #文件夹不存在
        path = unicode(urllib.unquote("."+info["path"]),"utf8")
        if not os.path.isdir(path):
            os.makedirs(path)
    else:
        path="."+info["path"]
    fp = open(path + "/" + info["file"],"wb")
    fp.write(str)
    fp.close()


# 将文本中的路径全部替换为相对路径
def replace_all_hrefs(content, hrefs, host):
    # 处理js中的url
    for i in hrefs["js"]:
        # 得到host部分
        r = re.search("(^(http:\/\/|https:\/\/|\/\/)([^\/]*))",i)
        oldhost = str(r.group(1))
        content = content.replace(oldhost,host)
    for i in hrefs["css"]:
        # 得到host部分
        r = re.search("(^(http:\/\/|https:\/\/|\/\/)([^\/]*))",i)
        oldhost = str(r.group(1))
        content = content.replace(oldhost,host)
    for i in hrefs["img"]:
        # 得到host部分
        r = re.search("(^(http:\/\/|https:\/\/|\/\/)([^\/]*))",i)
        oldhost = str(r.group(1))
        content = content.replace(oldhost,host)
    # 再讲host替换成.
    content = content.replace(host, ".")
    return content
# 打包成压缩包的函数
# def pack_up():

# 定义路径替换的规则
def rule_of_url_replace(url, type):
    h = {}
    h["oldurl"] = url
    if type == "css":
        # //fonts.googleapis.com/css?family=Cabin%3A400%2C600%7COpen+Sans%3A400%2C300%2C600&#038;ver=4.5.3
        r = re.search("(^(http:\/\/|https:\/\/|\/\/)([^\/]*))",url)
        oldhost = str(r.group(1))
        # //fonts.googleapis.com/css?family=Cabin%3A400%2C600%7COpen+Sans%3A400%2C300%2C600&#038;ver=4.5.3
        newhost = url.replace(oldhost, ".")

    if type == "js":
        print 2

    if type == "img":
        print 3

# 得到域名和路径的方法
def get_host(url):
    newr = {}
    # newr["oldurl"] = url
    r = re.search("(^(http:\/\/|https:\/\/|\/\/)([^\/]*))(.*)\/([^\?]*)",url)
    if r :
        newr["host"] = str(r.group(1))
        newr["path"] = str(r.group(4))
        if str(r.group(5)):
            nfile = str(r.group(5))
            # 先判断是不是锚点
            res = re.search("^#",nfile)
            if res:
                newr["file"] = "index.html"
            else:
                res = re.search("\..+",nfile)
                if res:
                    newr["file"] = nfile
                else:
                    newr["file"] = nfile+".html"
        else :
            newr["file"] = "index.html"
    else:
        newr["host"] = url
        newr["path"] = "/"
        newr["file"] = "index.html"

    print newr
    return newr

# os.makedirs(r"./test")        # 可以创建相对路径的文件夹
# os.path.isdir("./test")       # 可以用这个判断文件夹存不存在
# os.getcwd()                   # 得到执行文件所在路径
# os.mknod("test.txt")          # 创建空文件
# fp = open("test.txt",w)       # 直接打开一个文件，如果文件不存在则创建文件
# fp.write(str)                 # 把str写到文件中，write()并不会在str后加上一个换行符
# fp.close()                    # 关闭文件
'''
1.替换所有匹配的子串用newstring替换subject中所有与正则表达式regex匹配的子串
result, number = re.subn(regex, newstring, subject)
2.替换所有匹配的子串（使 用正则表达式对象）
rereobj = re.compile(regex)
result, number = reobj.subn(newstring, subject)字符串拆分
'''
get_content("http://blog.hwmorelove.com/")


# print hasindex
print "下载成功"
# print urllib.unquote("./asd/adad/linux-%e4%b8%8b%e7%bc%96%e8%af%91%e5%ae%89%e8%a3%85-php-5-6")

'''
    问题：1.文件夹中文名的问题,期初以为是乱码，
        其实是url编码，用urllib.unquote()解码，
        然后变为真正的中文字符后才存在乱码，
        使用unicode(str,"utf8")进行字符编译解决编码问题
    问题：2.路径替换有点问题，替换的环节有问题
        解决方法，添加url的同时，计算出应该被替换的新url
        放在get_all_href中
'''

# os.makedirs("./"+unicode("奥奥奥奥","utf8"))

# //fonts.googleapis.com/css?family=Cabin%3A400%2C600%7COpen+Sans%3A400%2C300%2C600&#038;ver=4.5.3
str = "//fonts.googleapis.com/css?family=Cabin%3A400%2C600%7COpen+Sans%3A400%2C300%2C600&#038;ver=4.5.3"

r = re.search("(^(http:\/\/|https:\/\/|\/\/)([^\/]*))", str)
oldhost = r.group(1)
print oldhost
# content = content.replace(oldhost, host)
