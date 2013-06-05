#import logging
#def get_logger():
    #logging.basicConfig(level=logging.NOTSET,
                        #format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        #datefmt='%m-%d %H:%M',)
    ## define a Handler which writes INFO messages or higher to the sys.stderr
    #console = logging.StreamHandler()
    #console.setLevel(logging.INFO)
    ## set a format which is simpler for console use
    #formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    ## tell the handler to use this format
    #console.setFormatter(formatter)
    ## add the handler to the root logger
    #logging.getLogger().addHandler(console)
import os
import time
import inspect
import sys

DSS_LOG_PATH = "/tmp/network.log"
TRAY_LOG_PATH = "/tmp/network.tray.log"
class Mylogger(object):

    def __init__(self, file_name):
        self.file_name = file_name
        if os.path.exists(self.file_name):
            os.remove(self.file_name)

        open(self.file_name, 'w').close()

    def set_level(self, level):
        self.level = level

    def verbose(self, string, level):

        if level >= self.level:
            print string

    def get_func_name(self):
        current = inspect.currentframe()
        current = inspect.getouterframes(current)
        return "(%s) %s"%(os.path.basename(current[2][1]), current[2][3])
        
    def info(self, *args):
        info = "[Info] %s %s:] %s"%(time.asctime(), self.get_func_name(), args)
        self.verbose(info, 0)
        with open(self.file_name, 'a') as logger:
            logger.write(info + "\n")

    def debug(self, *args):
        info = "[Debug] %s %s:] %s"%(time.asctime(), self.get_func_name(), args)
        self.verbose(info, -1)
        with open(self.file_name, 'a') as logger:
            logger.write(info + "\n")

    def warn(self, *args):
        info = "[Warn] %s %s:] %s"%(time.asctime(), self.get_func_name(), args)
        self.verbose(info, 1)
        with open(self.file_name, 'a') as logger:
            logger.write(info + "\n")

    def error(self, *args):
        info = "[Error] %s %s:] %s"%(time.asctime(), self.get_func_name(), args)
        self.verbose(info, 2)
        with open(self.file_name, 'a') as logger:
            logger.write(info + "\n")



#log.debug("this is a debug file")
#log.info("this is a info")
#get_logger()
#log = logging.getLogger()
#log.debug('sdfas')
