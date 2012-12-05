#! /usr/bin/env python

import polkit_permission

if __name__ == "__main__":
    permission = polkit_permission.new("org.freedesktop.accounts.user-administration")
    permission.get_allowed()

