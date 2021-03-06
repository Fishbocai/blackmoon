
import pycurl
import sys
import urllib2
import gzip
import StringIO
from bs4 import *
from bmplugin import *

info={'desc':"get ip list object use www.zoomeye.org for search keys",
      'cve':'',
      'init':0,  #0 maual init 1 init on start the program
      'link':"https://www.zoomeye.org/help/manual"} 

def init_plugin(main):
    zoomeye.main=main
    active=main.maintive
    active.regcommand('zoomse',zoom_search_print)
    #zoom=zoomeye()
    #return "zoomeye",zoom

class zoomeye:
    main=None
    def __init__(self,debugable=0,proxy=None):
        self.helplink="https://www.zoomeye.org/help/manual"
        self.useragent=self.main.pcf.getconfig('zoomeye','useragent')
        self.zoomc=pycurl.Curl()
        self.cookie=self.main.pcf.getconfig('zoomeye','cookie')
        self.zoomc.setopt(pycurl.SSL_VERIFYPEER, 0)     #https
        self.zoomc.setopt(pycurl.SSL_VERIFYHOST, 0)
        opts={pycurl.USERAGENT:self.useragent,\
              pycurl.COOKIE:self.cookie,\
              pycurl.HTTPHEADER:["Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",\
                                 "Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",\
                                 "Accept-Encoding: gzip, deflate",\
                                 "Connection: keep-alive"]\
              }
        for key,value in opts.iteritems():
            self.zoomc.setopt(key,value)
        if proxy:
            self.zoomc.setopt(pycurl.PROXY,proxy)
        self.initzoomeye()
        
    def getzoomtoken(self):
        useragent=raw_input("please input the User-Agent:")
        if useragent:
            self.zoomc.setopt(pycurl.USERAGENT,useragent)
            self.useragent=useragent
        cookie=raw_input("please input the zoom cookie token:")
        if cookie:
            self.zoomc.setopt(pycurl.COOKIE,cookie)
            self.cookie=cookie
    
    def isvaildzoom(self):
        try:
            head,body=lib_http.getdata4info("https://www.zoomeye.org",objc=self.zoomc)
        except Exception:
            lib_func.printstr("Time Out",1)
            return 0
        #print head
        hdt=lib_http.parsehttphead(head)
        if hdt['code']=='521':
            return 0
        return 1
        
    def initzoomeye(self):
        flag=0
        while 1:
            if not self.isvaildzoom():
                self.getzoomtoken()
                flag=1
            else:
                break
        if flag:
            self.main.pcf.setconfig('zoomeye','useragent',self.useragent)
            self.main.pcf.setconfig('zoomeye','cookie',self.cookie)
            
    def zoomsearch(self,sstr,limit=20):
        sstr=urllib2.quote(sstr)
        surl="https://www.zoomeye.org/search?q="+sstr
        devices=self.getzoomsrs(surl,limit)
        return devices
    
    def getzoomsrs(self,surl,limit):
        p=1
        deviceALL=[]
        while 1:
            url="%s&p=%d" %(surl,p)
            body=self.getzoom4url(url)
            zoomdevs=self.parsezoom4body(body)
            if len(zoomdevs)<10 or (len(deviceALL)+10)>limit:
                deviceALL.extend(zoomdevs)
                return deviceALL
            deviceALL.extend(zoomdevs)
            p+=1
            
    def getzoom4url(self,url):
        while 1:
            head,body=lib_http.getdata4info(url,{pycurl.URL:url},self.zoomc)
            hdt=lib_http.parsehttphead(head)
            if hdt['code']=='521':
                self.initzoomeye()
            else:
                return lib_http.gethttpresponse(hdt,body)
            
     
    def parsezoom4body(self,body):
        soup=BeautifulSoup(body)
        zoomdevs=[]
        #rs=soup.find("ul",{"class":"result device"})
        #devices=rs.findAll('li')
        ips=soup.findAll('a',{'class':'ip'})
        for ip in ips:
            device=ip.parent.parent
            zoomdevs.append(self.parsedevice2dict(device))
        return zoomdevs
    
    def parsedevice2dict(self,device):
        devdit={}
        try:
            devdit['ip']=device.find('a',{"class":"ip"}).contents[0]
            devdit['app']=device.find('li',{"class":"app"}).a.contents[0].strip()
            devdit['country']=device.find('a',{"class":"country"}).contents[2].strip()
            devdit['city']=device.find('a',{"class":"city"}).contents[0].strip()
            devdit['server']=device.header.s.a.contents[0].strip()
            devdit['port']=device.header.i.a.contents[0].strip()
            devdit['address']="%s:%s" %(devdit['ip'],devdit['port'])
        except Exception:
            pass
        return devdit
    
    def printdevinfo(self,devs):
        print "==============="
        print "Found about %d results" %len(devs)
        for dev in devs:
            for key,value in dev.iteritems():
                print key,value
            print  '============'


def zoom_search_print(paras):
    zoom=zoomeye()
    if not paras:
        paras="site:baidu.com"
    devs=zoom.zoomsearch(paras)
    zoom.printdevinfo(devs)
#zoom=zoomeye()
#devs=zoom.zoomsearch("esgcc.com.cn")
#zoom.printdevinfo(devs)
