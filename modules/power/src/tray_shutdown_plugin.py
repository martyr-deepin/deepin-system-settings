#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 Deepin, Inc.
#               2012 Hailong Qiu
#
# Author:     Hailong Qiu <356752238@qq.com>
# Maintainer: Hailong Qiu <356752238@qq.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from tray_shutdown_gui import Gui
from tray_dialog import TrayDialog
from deepin_utils.process import run_command
import inhibit

from nls import _
import gtk
import os
import sys
import subprocess
sys.path.append("/usr/share/deepin-system-settings/modules/account/src")
from accounts import User
try:
    import deepin_gsettings
except ImportError:
    print "----------Please Install Deepin GSettings Python Binding----------"
    print "git clone git@github.com:linuxdeepin/deepin-gsettings.git"
    print "------------------------------------------------------------------"

power_settings = deepin_gsettings.new("org.gnome.settings-daemon.plugins.power")

DBUS_USER_STR = "/org/freedesktop/Accounts/User%s" % (os.getuid())

SHUTDOWN_TEXT = _("\n<span foreground='#FF0000'>Turn off</span> your computer \
now? \n\nThe system will shut down in %s seconds.")

RESTART_TEXT = _("\n<span foreground='#FF0000'>Restart</span> your computer now?\
\n\nThe system will restart in %s seconds.")

SUSPEND_TEXT = _("\n<span foreground='#FF0000'>Suspend</span> your computer now?\
\n\nThe system will suspend in %s seconds.")

LOGOUT_TEXT = _("\n<span foreground='#FF0000'>Log out</span> of your system now?\
\n\nYou will be automatically logged out in %s seconds.")

INHIBIT_HEAD = _("\n<span foreground='#FF0000'>A program is still running:</span>")
INHIBIT_HEAD_PLURAL = _("\n<span foreground='#FF0000'>%s programs are still running:</span>")
INHIBIT_TAIL = _("Waiting for applications to terminate. Interrupting these may \
cause unexpected results.")

RUN_DSS_COMMAND = "deepin-system-settings account"
RUN_SWITCH_TOGREETER = "switchtogreeter"
RUN_LOCK_COMMAND = "dlock"

DSC_WARNING_TEXT = _("\n<span foreground='#FF0000'>The Software Center is still running.</span>")

""" BACKEND_PID is define in deepin software center backend program. """
BACKEND_PID = "/tmp/deepin-software-center/backend_running.pid"  

def is_software_center_working():
    #return True
    return os.path.exists(BACKEND_PID)

class TrayShutdownPlugin(object):
    def __init__(self):
        self.__xrandr_gsettings = deepin_gsettings.new("org.gnome.settings-daemon.plugins.xrandr")
        new_brightness = self.__xrandr_gsettings.get_double("brightness")
        if new_brightness > 0.1:
            self.__xrandr_gsettings.set_double("brightness", new_brightness)
        
        self.gui = Gui()
        self.dbus_user = User(DBUS_USER_STR)
        self.dialog = TrayDialog()

        self.resource_dict = {
                "deepin_shutdown": {
                    "info_text": SHUTDOWN_TEXT,
                    "ok_text": _("Shut down"),
                    "force_ok_text": _("Force shut down"),
                    "ok_exec": self.gui.cmd_dbus.new_stop,
                    },
                "deepin_restart": {
                    "info_text": RESTART_TEXT,
                    "ok_text": _("Restart"),
                    "force_ok_text": _("Force restart"),
                    "ok_exec": self.gui.cmd_dbus.new_restart,
                    },
                "deepin_suspend": {
                    "info_text": SUSPEND_TEXT,
                    "ok_text": _("Suspend"),
                    "force_ok_text": _("Force suspend"),
                    "ok_exec": self.gui.cmd_dbus.suspend,
                    },
                "deepin_hibernate": {
                    "info_text": LOGOUT_TEXT,
                    "ok_text": _("Log out"),
                    "force_ok_text": _("Force log out"),
                    "ok_exec": lambda:self.gui.cmd_dbus.logout(1),
                    },
                }

        self.gui.stop_btn.connect("clicked", self.check_system_app_running, 'deepin_shutdown')
        self.gui.restart_btn.connect("clicked", self.check_system_app_running, 'deepin_restart')
        self.gui.suspend_btn.connect("clicked", self.check_system_app_running, 'deepin_suspend')
        self.gui.logout_btn.connect("clicked", self.check_system_app_running, 'deepin_hibernate')
        self.gui.switch_btn.connect("clicked", self.switch_btn_clicked)
        self.gui.lock_btn.connect("clicked", self.lock_btn_clicked)
        self.gui.user_label_event.connect("button-press-event", self.user_label_clicked)

    def exec_command(self, command):
        subprocess.Popen(command, stderr=subprocess.STDOUT, shell=False)

    def check_system_app_running(self, widget, action_id):
        resource = self.resource_dict[action_id]
        if is_software_center_working():
            self.dialog.show_warning(DSC_WARNING_TEXT + "\n\n" + INHIBIT_TAIL,
                    ok_text=resource["force_ok_text"],
                    )
            self.dialog.run_exec = resource["ok_exec"]
            self.this.hide_menu()
        else:
            running_program = inhibit.get_inhibit_programs()
            if running_program:
                if len(running_program) == 1:
                    self.dialog.show_warning(INHIBIT_HEAD+"\n\n"+INHIBIT_TAIL,
                        ok_text=resource["force_ok_text"])
                else:
                    self.dialog.show_warning(INHIBIT_HEAD_PLURAL % len(running_program) 
                            +"\n\n"+INHIBIT_TAIL,
                        ok_text=resource["force_ok_text"])
                self.dialog.run_exec = resource["ok_exec"]
                self.this.hide_menu()
            else:
                self.dialog.show_dialog(action_id, resource["info_text"], resource["ok_text"])
                self.dialog.run_exec = resource["ok_exec"]
                self.this.hide_menu()

    def stop_btn_clicked(self, widget):
        self.dialog.show_dialog("deepin_shutdown", ok_text=_("Shut down"))
        self.dialog.run_exec = self.gui.cmd_dbus.new_stop
        self.this.hide_menu()
        #self.gui.cmd_dbus.stop()

    def restart_btn_clicked(self, widget):
        self.dialog.show_dialog("deepin_restart",
                                RESTART_TEXT,
                                ok_text=_("Restart"),
                                )
        self.dialog.run_exec = self.gui.cmd_dbus.new_restart
        self.this.hide_menu()
        #self.gui.cmd_dbus.stop()

    def suspend_btn_clicked(self, widget): 
        self.dialog.show_dialog("deepin_suspend",
                                SUSPEND_TEXT,
                                ok_text=_("Suspend"),
                                )
        self.dialog.run_exec = self.gui.cmd_dbus.suspend
        self.this.hide_menu()
        #self.gui.cmd_dbus.suspend()

    def logout_btn_clicked(self, widget):
        self.dialog.show_dialog("deepin_hibernate",
                                LOGOUT_TEXT,
                                ok_text=_("Log out"),
                                )
        self.dialog.run_exec = self.gui.cmd_dbus.logout
        self.dialog.argv = 1
        self.this.hide_menu()

    def user_label_clicked(self, widget, event):
        # run dss command.
        if event.button == 1:
            run_command(RUN_DSS_COMMAND)
            self.this.hide_menu()

    def switch_btn_clicked(self, widget):
        self.this.hide_menu()
        run_command(RUN_SWITCH_TOGREETER)

    def lock_btn_clicked(self, widget):
        self.this.hide_menu()
        run_command(RUN_LOCK_COMMAND)

    def init_values(self, this_list):
        self.this_list = this_list
        self.this = self.this_list[0]
        self.tray_icon = self.this_list[1]
        self.tray_icon.set_icon_theme("user")

    def set_user_icon(self):
        try:
            # set user icon.
            #print self.gui.cmd_dbus.get_user_image_path() 
            #self.gui.user_icon.set_from_file(self.gui.cmd_dbus.get_user_image_path())
            self.gui.user_icon.set_from_file(self.dbus_user.get_icon_file())
            #
            user_pixbuf = self.gui.user_icon.get_pixbuf()
            new_user_pixbuf = user_pixbuf.scale_simple(self.gui.icon_width, 
                                                       self.gui.icon_height, 
                                                       gtk.gdk.INTERP_BILINEAR)
        except Exception, e:
            try:
                user_pixbuf = self.gui.gui_theme.get_pixbuf("account/icon.png").get_pixbuf()
                new_user_pixbuf = user_pixbuf.scale_simple(self.gui.icon_width, 
                                                           self.gui.icon_height, 
                                                           gtk.gdk.INTERP_BILINEAR)
                print "set user icon [error]:", e
            except:
                new_user_pixbuf = self.tray_icon.load_icon("user")

        self.gui.user_icon.set_from_pixbuf(new_user_pixbuf)


    def run(self):
        return True

    def insert(self):
        return 1
        
    def id(self):
        return "tray-shutdown-plugin-hailongqiu"

    def plugin_widget(self):
        return self.gui 

    def show_menu(self):
        self.set_user_icon()
        self.this.set_size_request(160, 210)
        #print "shutdown show menu..."

    def hide_menu(self):
        #print "shutdown hide menu..."
        pass

def return_insert():
    return 1

def return_id():
    return "shutdown"

def return_plugin():
    return TrayShutdownPlugin 


if __name__ == "__main__":
    def ok_btn_clicked(widget):
        #
        if len(sys.argv) >= 2:
            if sys.argv[1] == 'logout':
                gui.cmd_dbus.logout(1)
            elif sys.argv[1] == 'shutdown':
                gui.cmd_dbus.new_stop()
            elif sys.argv[1] == 'suspend':
                gui.cmd_dbus.suspend()
    gui = Gui()
    dialog = TrayDialog()
    dialog.connect("hide", lambda w : gtk.main_quit())
    dialog.connect("destroy", lambda w : gtk.main_quit())
    dialog.ok_btn.connect("clicked", ok_btn_clicked)

    dialog.set_bg_pixbuf(gtk.gdk.pixbuf_new_from_file('/usr/share/deepin-system-tray/src/image/on_off_dialog/deepin_on_off_bg.png'))
    dialog.show_pixbuf = gtk.gdk.pixbuf_new_from_file('/usr/share/deepin-system-tray/src/image/on_off_dialog/deepin_hibernate.png')
    dialog.show_image.set_from_pixbuf(dialog.show_pixbuf)

    dialog.argv = 1
    if len(sys.argv) >= 2:
        if sys.argv[1] == 'shutdown':
            print "shutdown"
            dialog.show_dialog("deepin_shutdown")
            #dialog.run_exec = gui.cmd_dbus.shutdown
            dialog.show_all()
        elif sys.argv[1] == 'powerkey':
            print "powerkey"
            if power_settings.get_string("button-power") == "shutdown":
                print "show shutdown"
                sys.argv[1] = 'shutdown'
                dialog.show_dialog("deepin_shutdown")
                dialog.show_all()

            elif power_settings.get_string("button-power") == "suspend":
                print "show suspend"
                sys.argv[1] = 'suspend'
                dialog.show_dialog("deepin_suspend",
                                    SUSPEND_TEXT,
                                    )
                dialog.show_all()

            elif power_settings.get_string("button-power") == "logout":
                print "show logout"
                sys.argv[1] = 'logout'
                dialog.show_dialog("deepin_hibernate",
                                    LOGOUT_TEXT,
                                    )
                dialog.show_all()

            elif power_settings.get_string("button-power") == "nothing":
                print "show nothing"
                pass

            else:
                pass
        elif sys.argv[1] == 'logout':
            dialog.show_dialog("deepin_hibernate",
                                LOGOUT_TEXT,
                                )
            #dialog.run_exec = gui.cmd_dbus.logout
            dialog.show_all()

    gtk.main()
