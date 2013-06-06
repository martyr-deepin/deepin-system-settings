#!/usr/bin/env python

import os
import traceback
import getpass
import spwd
import crypt
from deepin_utils.file import get_parent_dir, get_current_dir

def is_deepin_livecd():
    try:
        username = getpass.getuser()
    except:
        traceback.print_exc()
        username = os.getlogin()

    if username == "root":
        username = os.getlogin()

    if username != "deepin":
        return False
    else:
        return verify_shadow()

def verify_shadow():
    try:
        shadow = spwd.getspnam("deepin")[1]
    except:
        traceback.print_exc()
        shadow = None

    if shadow == None or len(shadow) == 0:
        return False
    else:
        try:
            return crypt.crypt("",shadow) == shadow
        except:
            traceback.print_exc()
            return False

if __name__ == "__main__":
    if is_deepin_livecd():
        exit(0)
    else:
        exit(1)
