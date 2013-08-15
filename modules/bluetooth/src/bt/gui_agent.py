#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Long Wei
#
# Author:     Long Wei <yilang2007lw@gmail.com>
# Maintainer: Long Wei <yilang2007lw@gmail.com>
#             Zhai Xiang <zhaixiang@linuxdeepin.com>
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

import gobject
import dbus
import dbus.service
import dbus.mainloop.glib
import gtk
from dtk.ui.constant import ALIGN_MIDDLE
from dtk.ui.label import Label
from dtk.ui.button import Button
from dtk.ui.dialog import DIALOG_MASK_SINGLE_PAGE, DialogBox
from bluetooth_dialog import BluetoothInputDialog
from constant import *
from nls import _

class AgentDialog(DialogBox):
    def __init__(self,
                 title,
                 message,
                 default_width=400,
                 default_height=220,
                 confirm_callback=None,
                 cancel_callback=None,
                 confirm_button_text="Yes",
                 cancel_button_text="No"):
        DialogBox.__init__(self, "", default_width, default_height, DIALOG_MASK_SINGLE_PAGE)
        self.confirm_callback = confirm_callback
        self.cancel_callback = cancel_callback

        self.title_align = gtk.Alignment()
        self.title_align.set(0, 0, 0, 0)
        self.title_align.set_padding(0, 0, FRAME_LEFT_PADDING, 8)
        self.title_label = Label(title, wrap_width=300)

        self.label_align = gtk.Alignment()
        self.label_align.set(0.5, 0.5, 0, 0)
        self.label_align.set_padding(0, 0, 8, 8)
        self.label = Label(message, text_x_align=ALIGN_MIDDLE, text_size=55)

        self.confirm_button = Button(confirm_button_text)
        self.cancel_button = Button(cancel_button_text)

        self.confirm_button.connect("clicked", lambda w: self.click_confirm_button())
        self.cancel_button.connect("clicked", lambda w: self.click_cancel_button())

        self.body_box.pack_start(self.title_align, False, False)
        self.title_align.add(self.title_label)
        self.body_box.pack_start(self.label_align, True, True)
        self.label_align.add(self.label)

        self.right_button_box.set_buttons([self.cancel_button, self.confirm_button])

    def click_confirm_button(self):
        if self.confirm_callback != None:
            self.confirm_callback()

        self.destroy()

    def click_cancel_button(self):
        if self.cancel_callback != None:
            self.cancel_callback()

        self.destroy()

gobject.type_register(AgentDialog)

def ask(prompt):
    try:
        return raw_input(prompt)
    except:
        return input(prompt)

class Rejected(dbus.DBusException):
    _dbus_error_name = "org.bluez.Error.Rejected"

def raise_rejected(err_message):
    raise Rejected(err_message)

class GuiAgent(dbus.service.Object):
    def __init__(self,
                 device_name,
                 path = "/com/deepin/bluetooth/agent",
                 bus = None):
        self.device_name = device_name
        self.agent_path = path
        if bus is None:
            bus = dbus.SystemBus()

        dbus.service.Object.__init__(self, bus, path)

        self.exit_on_release = True
        self.__is_rejected = False

    def is_rejected(self):
        return self.__is_rejected
        
    def set_rejected(self, value):
        self.__is_rejected = value

    def set_exit_on_release(self, exit_on_release):
        self.exit_on_release = exit_on_release

    @dbus.service.method("org.bluez.Agent",
                         in_signature="", out_signature="")
    def Release(self):
        print("Release")
        if self.exit_on_release:
            mainloop.quit()

    @dbus.service.method("org.bluez.Agent",
                         in_signature="os", out_signature="")
    def Authorize(self, device, uuid):
        print("Authorize (%s, %s)" % (device, uuid))
        authorize = ask("Authorize connection (yes/no): ")
        if (authorize == "yes"):
            return
        raise Rejected("Connection rejected by user")

    @dbus.service.method("org.bluez.Agent",
                         in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        print("RequestPinCode (%s)" % (device))
        # return ask("Enter PIN Code: ")
        
        dlg = gtk.Dialog()
        input_d = BluetoothInputDialog("Enter PIN code:", "")
        input_d.show_all()
        # dlg.set_position(10000, 10000)
        response = dlg.run()
        dlg.destroy()

        print response
        return ""

    @dbus.service.method("org.bluez.Agent",
                         in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        print("RequestPasskey (%s)" % (device))
        passkey = ask("Enter passkey: ")
        return dbus.UInt32(passkey)

    @dbus.service.method("org.bluez.Agent",
                         in_signature="ou", out_signature="")
    def DisplayPasskey(self, device, passkey):
        print("DisplayPasskey (%s, %06d)" % (device, passkey))

    @dbus.service.method("org.bluez.Agent",
                         in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode):
        print("DisplayPinCode (%s, %s)" % (device, pincode))

    @dbus.service.method("org.bluez.Agent",
                         in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        print("RequestConfirmation (%s, %06d)" % (device, passkey))

        dialog = AgentDialog(_("Please confirm %s pin match as below") % self.device_name,
                             str(passkey),
                             confirm_button_text = _("Yes"),
                             cancel_button_text = _("No"),
                             confirm_callback = lambda : self.set_rejected(False),
                             cancel_callback = lambda : self.set_rejected(True)
                             )
        dialog.show_all()

    @dbus.service.method("org.bluez.Agent",
                         in_signature="s", out_signature="")
    def ConfirmModeChange(self, mode):
        print("ConfirmModeChange (%s)" % (mode))
        authorize = ask("Authorize mode change (yes/no): ")
        if (authorize == "yes"):
            return
        raise Rejected("Mode change by user")

    @dbus.service.method("org.bluez.Agent",
                         in_signature="", out_signature="")
    def Cancel(self):
        print("Cancel")
