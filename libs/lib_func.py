#coding : utf-8
import md5
import hashlib 
import os
import subprocess
import sys
import getopt
import lib_func

def execShell(cmd):
    p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    return p.stdout.read(),p.stderr.read()

def getMD5(fname):
    if sys.platform=='win32' and os.path.isfile(fname):
        rs=execShell('certutil -hashfile %s MD5' %fname)
        md5s=rs.split('\r\n')[1].replace(' ','')
        return md5s
    
def printstr(s,flag=0):
    fd={0:'INFO:',1:"WARING:",2:"ERROR:"}
    print fd[flag],s
    
def printlist(ablist,flag=0):
    for i in ablist:
        if flag:
            print i
        else:
            print i,
    if not flag:
        print ''
    
def getparasdict(matparas,formats,formatm=[]):
    plist=matparas.split(' ')
    try:
        opts,args=getopt.getopt(plist,formats,formatm)
        pd={}
        for item in opts:
            pd[mystrip(item[0])]=item[1]
        return pd
    except Exception:
        lib_func.printstr("parameter string is error for you formats",2)
        
def mystrip(s,c='-'):
    return s.replace(c,"")