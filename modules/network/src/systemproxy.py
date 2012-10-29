import dbus
from nmlib.nmobject import NMObject
from nmlib.nm_utils import TypeConvert
import pacparser

class SystemProxy(NMObject):
    '''SystemProxy'''

    def __init__(self):
        NMObject.__init__(self, object_path = "/", 
                          object_interface = "com.linuxdeepin.ProxyService",
                          service_name = "com.linuxdeepin.ProxyService",
                          bus = dbus.SystemBus())
        
        self.proxy_mode = "none"

    def __get_proxy(self, proxy_type):
        return TypeConvert.dbus2py(self.dbus_interface.get_proxy(proxy_type))

    def __set_no_proxy(self, new_no_proxy):
        return TypeConvert.dbus2py(self.dbus_interface.set_no_proxy(new_no_proxy)) 

    def __set_proxy(self, proxy_type, new_proxy):
        return TypeConvert.dbus2py(self.dbus_interface.set_proxy(proxy_type, new_proxy))

    def proxy2host(self, proxy_str):
        proxy_type = proxy_str.split(":")[0]
        host = proxy_str.split(":")[1][2:]
        port = int(proxy_str.split(":")[2][:-1])

        return (proxy_type, host, port)

    def host2proxy(self, proxy_type, host, port):
        return "%s://%s:%i/" % (proxy_type, host, int(port))

    def get_http_proxy(self):
        return self.proxy2host(self.__get_proxy("http"))

    def get_https_proxy(self):
        return self.proxy2host(self.__get_proxy("https"))

    def get_ftp_proxy(self):
        return self.proxy2host(self.__get_proxy("ftp"))

    def get_socks_proxy(self):
        return self.proxy2host(self.__get_proxy("socks"))
    
    def set_http_proxy(self, host, port):
        self.__set_proxy("http", self.host2proxy("http", host, port))

    def set_https_proxy(self, host, port):
        self.__set_proxy("https", self.host2proxy("https", host, port))

    def set_ftp_proxy(self, host, port):
        self.__set_proxy("ftp", self.host2proxy("ftp", host, port))

    def set_socks_proxy(self, host, port):
        self.__set_proxy("socks", self.host2proxy("socks", host, port))
        
    def clear_proxy(self):
        self.__set_proxy("http","")
        self.__set_proxy("https", "")
        self.__set_proxy("ftp", "")
        self.__set_proxy("socks", "")

    def save_proxy(self):
        pass

    def pac_parser(self, wpad_url):
        pacparser.init()
        pacparser.parse_pac(wpad_url)
        proxy = pacparser.find_proxy("http://www.manugarg.com")
        print proxy
        pacparser.cleanup()

systemproxy = SystemProxy()

if __name__ == "__main__":
    systemproxy.set_http_proxy("www.baidu.com", 80)