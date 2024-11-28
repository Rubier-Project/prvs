from src.phub import Client
from src.phub import Quality
import time
import os
import sys
import threading

os.system("")

commands: dict = {}

class BufferList(object):
    def __init__(self,
                 List: list = [],
                 ):
        
        self.list = List
        
    def parse(self):
        bfd = {}

        for i in range(len(self.list)):
            bfd["_"+str(i+1)] = self.list[i]

        return bfd
    
    def isexists(self, target):
        if target in self.list:
            return True
        else:return False
    
    def indexexists(self, target):
        if target in self.list:
            return self.list.index(target)
        else:return False

    def isinfrontof(self, target, indexes):
        isit = False

        if target in self.list:
            try:
                indx = self.list.index(target)
                if indx == indexes:
                    isit = True
                else:isit = False
            except Exception as e:return e
        
        return isit

class BufferConsole(object):
    def __init__(self):

        self.data = []

    def __setcommands__(self, __key, __value):
        commands[__key] = __value
        return commands
    
    def getDictArgv(self):
        return BufferList(sys.argv).parse()
    
    def addFlag(self, *flags, mode: str = "in_front_of"):
        flg = list(flags)
        for i in range(len(flg)):
            self.__setcommands__(str(i+1), flg[i])

        if mode == "in_front_of":
            for key, val in BufferConsole().getDictArgv().items():
                if str(val) in flg:
                    keyx = int(str(key).replace("_", ""))
                    keyx += 1
                    if not f"_{keyx}" in BufferConsole().getDictArgv().keys():
                        self.data.append("Null")
                        pass
                    else:
                        self.data.append(BufferConsole().getDictArgv()[f"_{keyx}"])
                        pass
                
                else:
                    pass

            return self.data

class console(object):
    WHITE = "\001\033[0;38;5;231m\002"
    YELLOW = "\001\033[0;38;5;226m\002"
    GREEN = "\001\033[0;38;5;82m\002"
    RED = "\001\033[0;38;5;196m\002"
    ORANGE = "\001\033[0;38;5;208m\002"

    def log(msg: str = ""):
        t = time.strftime("%H:%M:%S")
        print(f"{console.WHITE}[{console.YELLOW}{t}{console.WHITE}] [{console.GREEN}INFO{console.WHITE}] {msg}")
    
    def err(msg: str = ""):
        t = time.strftime("%H:%M:%S")
        print(f"{console.WHITE}[{console.YELLOW}{t}{console.WHITE}] [{console.RED}UNIN{console.WHITE}] {msg}")

    def warn(msg: str = ""):
        t = time.strftime("%H:%M:%S")
        print(f"{console.WHITE}[{console.YELLOW}{t}{console.WHITE}] [{console.ORANGE}WARN{console.WHITE}] {msg}")

class SunGlass(object):
    def __init__(self):
        pass

    def helpLogger(self):
        console.log(""":: %s [ -h / --help ] [options...] [values...]
  -h / --help: Show this message::Optional
  -u: Give url for Download::Necessary
  -q: Give Quality for Download::Optional::[ best, worst, half ]
  -v / --verbose: Verbose Process::Optional""" % sys.argv[0].split(".")[0] if "." in sys.argv[0] else sys.argv[0])
        
    def tryToDownload(self, url: str, qul: str):
        assert qul.lower() in (
            "best",
            "worst",
            "half"
        )

        console.warn("if your region is blocked for pornhub please enable your VPN or DNS".title())

        try:
            app = Client()
            console.log("main value seted".title()) if "--verbose" in sys.argv or "-v" in sys.argv else True
            console.warn("try to download ...".title()) if "--verbose" in sys.argv or "-v" in sys.argv else True
            stat = app.get(url).download(".", eval(f"Quality('{qul}').{qul.upper()}") if not qul == "None" else Quality('best').BEST)
            console.log("video downloaded on path ".title()+stat)
        except Exception as ER:
            console.warn("error detected".title()) if "--verbose" in sys.argv or "-v" in sys.argv else True
            console.err(str(ER))

hflag = BufferConsole().addFlag("-h", "--help")
uflag = BufferConsole().addFlag("-u")
qflag = BufferConsole().addFlag("-q")
sun = SunGlass()

if len(hflag) >= 1:
    sun.helpLogger()

else:
    if len(uflag) >= 1:
        url = uflag[0]
        if url == "Null" or url == "-q" or url == "-v" or url == "--verbose" or url == "-u":
            console.err("Url not detected".title())
            exit(1)
        else:
            if len(qflag) >= 1:
                quality = qflag[0]
                if quality == "Null" or quality == "-u" or quality == "-v" or quality == "--verbose" or quality == "-q":
                    console.err("Quality not detected".title())
                    console.warn("Continue with Best Quality".title())

                    #sun.tryToDownload(url=url, qul="best")
                    th = threading.Thread(target=sun.tryToDownload, args=(url, "best"))
                    th.start()

                else:
                    console.log("Url: "+ url) if "--verbose" in sys.argv or "-v" in sys.argv else True
                    console.log("Quality: "+quality.upper()) if "--verbose" in sys.argv or "-v" in sys.argv else True

                    th = threading.Thread(target=sun.tryToDownload, args=(url, quality.lower()))
                    th.start()