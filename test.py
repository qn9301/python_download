#-*-coding:utf-8-*-
from bs4 import BeautifulSoup
import requests
import re
def get_content(web,param):
    r = re.search("(^(http:\/\/|https:\/\/|\/\/)([^\/]*))\/?",web)
    perfix = r.group(1)+"/"
    cont = []
    html = requests.get(web,param)
    content = html.text
    soup = BeautifulSoup(content,"lxml")
    all = soup.find_all(class_="public")
    for item in all:
        a = item.find("a")
        newarr = {}
        newarr["href"] = a["href"]
        newarr["title"] = str(a.string.replace("\n","").replace("\r","").replace(" ",""))
        newre = re.search("^(http:\/\/|https:\/\/)",newarr["href"])
        if not newre :
            newarr["href"] = perfix+newarr["href"]
        cont.append(newarr)
    return cont
web2 = "https://github.com/ruanyf"
param2 = {"tab":"repositories","page":1}
data = []
while True:
    ans = get_content(web2,param2)
    if ans :
        param2["page"]= param2["page"] + 1
    else:
        break
    for i in range(len(ans)):
        data.append(ans[i])
print data