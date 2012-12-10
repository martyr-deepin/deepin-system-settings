#!/usr/bin/env python
#-*- coding:utf-8  -*-

import pexpect
import time

if __name__ == "__main__":
    user = "ceshi"
    old = "yilang2007lw"
    new = "yilang2008lw"
    
    passwd = pexpect.spawn("/usr/bin/passwd %s" %user)
    time.sleep(0.1)
    try:	
    	if passwd.expect("当前"):
	    print "current"
	    passwd.sendline(old)
	    time.sleep(0.1)
    
    	if passwd.expect("新的"):
	    print "new"
	    passwd.sendline(new)
	    time.sleep(0.1)
    
    	if passwd.expect("重新"):
	    print "confirm"
	    passwd.sendline(new)	
    
    	if passwd.expect("成功"):
	    print "succeed"
    
    	if passwd.expect("错误"):
	    print "failed"
    
    except:
    	print "failed"
