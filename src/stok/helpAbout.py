import sys, os

from stok import parameters


versionMajor = 1
versionMinor = 0
versionDev   = 1
date = "2020.3.23"

def strAbout():
    pathDirList = sys.argv[0].replace("\\", "/").split("/")
    pathDirList.pop()
    strPath = os.path.abspath("/".join(str(i) for i in pathDirList))
    if not os.path.exists(strPath+"/"+parameters.appIcon):
        pathDirList.pop()
        strPath = os.path.abspath("/".join(str(i) for i in pathDirList))
    strPath = strPath+"/"+parameters.strDataDirName
    return '''\
Python 3.5 + PyQt5<br><br>
<div><div>HamTool is a project create by george</div></div><br><br>

See more on <b><a href="http://www.github.com/">wzy</a></b><br><br>
Welcome to use our products<br><br>


'''
