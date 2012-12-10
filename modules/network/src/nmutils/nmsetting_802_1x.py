#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 ~ 2013 Deepin, Inc.
#               2012 ~ 2013 Long Wei
#
# Author:     Long Wei <yilang2007lw@gmail.com>
# Maintainer: Long Wei <yilang2007lw@gmail.com>
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

import dbus
from nmsetting import NMSetting
from nmlib.nm_utils import TypeConvert

class NMSetting8021x (NMSetting):
    '''NMSetting8021x'''

    def __init__(self):
        NMSetting.__init__(self)
        self.name = "802-1x"

    @property
    def eap(self):
        if "eap" not in self.prop_dict.iterkeys():
            self.clear_eap_methods()
        return TypeConvert.dbus2py(self.prop_dict["eap"])

    @eap.setter
    def eap(self, new_eap):
        # if new_eap in ["leap", "md5", "tls", "peap", "ttls", "fast"]:
        self.prop_dict["eap"] = dbus.Array(new_eap, signature = dbus.Signature('s'))

    def add_eap_method(self, method):
        if method in ["leap", "md5", "tls", "peap", "ttls", "fast"] and method not in self.eap:
            self.prop_dict["eap"].append(method)

    def remove_eap_method(self, method):
        if method in self.prop_dict["eap"]:
            self.prop_dict["eap"].remove(method)

    def clear_eap_methods(self):
        self.prop_dict["eap"] = dbus.Array([], signature = dbus.Signature('s'))

    @property    
    def identity(self):
        if "identity" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["identity"])

    @identity.setter
    def identity(self, new_identity):
        self.prop_dict["identity"] = TypeConvert.py2_dbus_string(new_identity)

    @property
    def anonymous_identity(self):
        if "anonymous-identity" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["anonymous-identity"])

    @anonymous_identity.setter
    def anonymous_identity(self, new_anonymous_identity):
        self.prop_dict["anonymous-identity"] = TypeConvert.py2_dbus_string(new_anonymous_identity)

    @property
    def pac_file(self):
        if "pac-file" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["pac-file"])

    @pac_file.setter
    def pac_file(self, new_pac_file):
        self.prop_dict["pac-file"] = new_pac_file

    @property
    def ca_path(self):
        if "ca-path" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["ca-path"])

    @ca_path.setter
    def ca_path(self, new_ca_path):
        self.prop_dict["ca-path"] = TypeConvert.py2_dbus_string(new_ca_path)

    @property
    def system_ca_certs(self):###True or False###
        if "system-ca-certs" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["system-ca-certs"])

    @system_ca_certs.setter
    def system_ca_certs(self, new_system_ca_certs):
        self.prop_dict["system-ca-certs"] = TypeConvert.py2_dbus_boolean(new_system_ca_certs)

    # def ca_cert_scheme(self):
    #     return self._ca_cert_scheme

    # def get_ca_cert_blob(self):
    #     if self.get_ca_cert_scheme() == NMSetting8021xCKScheme.NM_SETTING_802_1X_CK_SCHEME_BLOB:
    #         return self.ca_cert

    # def get_ca_cert_path(self):
    #     if self.get_ca_cert_scheme() == NMSetting8021xCKScheme.NM_SETTING_802_1X_CK_SCHEME_PATH:
    #         return self.ca_cert.data + len(SCHEME_PATH)

    # def __path_to_scheme_value(self):
    #     pass

    @property
    def ca_cert(self):
        if "ca-cert" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["ca-cert"])

    @ca_cert.setter
    def ca_cert(self, new_ca_cert):
        self.prop_dict["ca-cert"] = TypeConvert.py2_dbus_bytearray(new_ca_cert)

    @property
    def subject_match(self):
        if "subject-match" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["subject-match"])

    @subject_match.setter
    def subject_match(self, new_subject_match):
        self.prop_dict["subject-match"] = TypeConvert.py2_dbus_string(new_subject_match)

    @property
    def altsubject_matches(self):
        if "altsubject-matches" not in self.prop_dict.iterkeys():
            self.clear_altsubject_matches()
        return TypeConvert.dbus2py(self.prop_dict["altsubject-matches"])

    @altsubject_matches.setter
    def altsubject_matches(self, new_altsubject_matches):
        self.prop_dict["altsubject-matches"] = dbus.Array(new_altsubject_matches, signature = dbus.Signature('s'))

    def add_altsubject_match(self, altsubject_match):
        if altsubject_match not in self.prop_dict["altsubject-matches"]:
            self.prop_dict["altsubject-matches"].append(altsubject_match)

    def remove_altsubject_match(self, altsubject_match):
        if altsubject_match in self.prop_dict["altsubject-matches"]:
            self.prop_dict["altsubject-matches"].remove(altsubject_match)

    def clear_altsubject_matches(self):
        self.prop_dict["altsubject-matches"] = dbus.Array([], signature = dbus.Signature('s'))

    @property
    def client_cert(self):
        if "client-cert" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["client-cert"])

    @client_cert.setter
    def client_cert(self, new_client_cert):
        self.prop_dict["client-cert"] = TypeConvert.py2_dbus_bytearray(new_client_cert)

    # def get_client_cert_scheme(self):
    #     return self.get_cert_scheme(self.client_cert)

    # def get_client_cert_blob(self):
    #     if self.get_client_cert_scheme() == NMSetting8021xCKScheme.NM_SETTING_802_1X_CK_SCHEME_BLOB:
    #         return self.client_cert

    # def get_client_cert_path(self):
    #     pass

    @property
    def phase1_peapver(self):
        if "phase1-peapver" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["phase1-peapver"])

    @phase1_peapver.setter
    def phase1_peapver(self, new_phase1_peapver):
        self.prop_dict["phase1-peapver"] = TypeConvert.py2_dbus_string(new_phase1_peapver)

    @property
    def phase1_peaplabel(self):
        if "phase1-peaplabel" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["phase1-peaplabel"])

    @phase1_peaplabel.setter
    def phase1_peaplabel(self, new_phase1_peaplabel):
        self.prop_dict["phase1-peaplabel"] = TypeConvert.py2_dbus_string(new_phase1_peaplabel)

    @property
    def phase1_fast_provisioning(self):
        if "phase1-fast-provisioning" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["phase1-fast-provisioning"])

    @phase1_fast_provisioning.setter
    def phase1_fast_provisioning(self, new_phase1_fast_provisioning):
        self.prop_dict["phase1-fast-provisioning"] = TypeConvert.py2_dbus_string(new_phase1_fast_provisioning)

    @property
    def phase2_auth(self):
        if "phase2-auth" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["phase2-auth"])

    @phase2_auth.setter
    def phase2_auth(self, new_phase2_auth):
        self.prop_dict["phase2-auth"] = TypeConvert.py2_dbus_string(new_phase2_auth)

    @property
    def phase2_autheap(self):
        if "phase2-autheap" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["phase2-autheap"])

    @phase2_autheap.setter
    def phase2_autheap(self, new_phase2_autheap):
        self.prop_dict["phase2-autheap"] = TypeConvert.py2_dbus_string(new_phase2_autheap)

    @property
    def phase2_ca_path(self):
        if "phase2-ca-path" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["phase2-ca-path"])

    @phase2_ca_path.setter
    def phase2_ca_path(self, new_phase2_ca_path):
        self.prop_dict["phase2-ca-path"] = TypeConvert.py2_dbus_string(new_phase2_ca_path)

    @property
    def phase2_ca_cert(self):
        if "phase2-ca-cert" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["phase2-ca-cert"])

    @phase2_ca_cert.setter
    def phase2_ca_cert(self, new_phase2_ca_cert):
        self.prop_dict["phase2-ca-cert"] = TypeConvert.py2_dbus_bytearray(new_phase2_ca_cert)

    # def get_phase2_ca_cert_scheme(self):
    #     return self.get_cert_scheme(self.phase2_ca_cert)

    # def get_phase2_ca_cert_blob(self):
    #     pass

    # def get_phase2_ca_cert_path(self):
    #     pass

    @property
    def phase2_subject_match(self):
        if "phase2-subject-match" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["phase2-subject-match"])

    @phase2_subject_match.setter
    def phase2_subject_match(self,new_phase2_subject_match):
        self.prop_dict["phase2-subject-match"] = TypeConvert.py2_dbus_string(new_phase2_subject_match)

    @property
    def phase2_altsubject_matches(self):
        if "phase2-altsubject-matches" not in self.prop_dict.iterkeys():
            self.clear_phase2_altsubject_matches()
        return TypeConvert.dbus2py(self.prop_dict["phase2-altsubject-matches"])

    @phase2_altsubject_matches.setter
    def phase2_altsubject_matches(self, new_phase2_altsubject_matches):
        self.prop_dict["phase2-altsubject-matches"] = TypeConvert.py2_dbus_array(new_phase2_altsubject_matches)

    def add_phase2_altsubject_match(self, phase2_altsubject_match):
        if phase2_altsubject_match not in self.prop_dict["phase2-altsubject-matches"]:
            self.prop_dict["phase2-altsubject-matches"].append(phase2_altsubject_match)

    def remove_phase2_altsubject_match(self, phase2_altsubject_match):
        if phase2_altsubject_match in self.prop_dict["phase2-altsubject-matches"]:
            self.prop_dict["phase2-altsubject-matches"].remove(phase2_altsubject_match)

    def clear_phase2_altsubject_matches(self):
        self.prop_dict["phase2-altsubject-matches"] = dbus.Array([], signature = dbus.Signature('s'))

    @property
    def phase2_client_cert(self):
        if "phase2-client-cert" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["phase2-client-cert"])

    @phase2_client_cert.setter
    def phase2_client_cert(self, new_phase2_client_cert):
        self.prop_dict["phase2-client-cert"] = TypeConvert.py2_dbus_bytearray(new_phase2_client_cert)

    # def get_phase2_client_cert_scheme(self):
    #     return self.get_cert_scheme(self.phase2_client_cert_scheme)

    # def get_phase2_client_cert_blob(self):
    #     pass

    # def get_phase2_client_cert_path(self):
    #     pass

    @property
    def password(self):
        if "password" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["password"])

    @password.setter
    def password(self, new_password):
        self.prop_dict["password"] = TypeConvert.py2_dbus_string(new_password)

    @property
    def password_flags(self):
        if "password-flags" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["password-flags"])

    @password_flags.setter
    def password_flags(self,new_password_flags):
        self.prop_dict["password-flags"] = TypeConvert.py2_dbus_uint32(new_password_flags)

    @property
    def password_raw(self):
        if "password-raw" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["password-raw"])

    @password_raw.setter
    def password_raw(self, new_password_raw):
        self.prop_dict["password-raw"] = TypeConvert.py2_dbus_bytearray(new_password_raw)

    @property
    def password_raw_flags(self):
        if "password-raw-flags" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["password-raw-flags"])

    @password_raw_flags.setter
    def password_raw_flags(self, new_password_raw_flags):
        self.prop_dict["password-raw-flags"] = TypeConvert.py2_dbus_uint32(new_password_raw_flags)

    @property
    def private_key(self):
        if "private-key" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["private-key"])

    @private_key.setter
    def private_key(self, new_private_key):
        self.prop_dict["private-key"] = TypeConvert.py2_dbus_bytearray(new_private_key)

    # def get_private_key_scheme(self):
    #     return self.get_cert_scheme(self.private_key)

    # def get_private_key_blob(self):
    #     pass

    # def get_private_key_path(self):
    #     pass

    @property
    def private_key_password(self):
        if "private-key-password" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["private-key-password"])

    @private_key_password.setter
    def private_key_password(self, new_private_key_password):
        self.prop_dict["private-key-password"] = TypeConvert.py2_dbus_string(new_private_key_password)

    @property
    def private_key_password_flags(self):
        if "private-key-password-flags" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["private-key-password-flags"])

    @private_key_password_flags.setter
    def private_key_password_flags(self, new_private_key_password_flags):
        self.prop_dict["private-key-password-flags"] = TypeConvert.py2_dbus_uint32(new_private_key_password_flags)

    # def get_private_key_format(self):
    #     pass

    @property
    def phase2_private_key_password(self):
        if "phase2-private-key-password" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["phase2-private-key-password"])

    @phase2_private_key_password.setter
    def phase2_private_key_password(self, new_phase2_private_key_password):
        self.prop_dict["phase2-private-key-password"] = TypeConvert.py2_dbus_string(new_phase2_private_key_password)

    @property
    def phase2_private_key_password_flags(self):
        if "phase2-private-key-password-flags" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["phase2-private-key-password-flags"])

    @phase2_private_key_password_flags.setter
    def phase2_private_key_password_flags(self, new_phase2_private_key_password_flags):
        self.prop_dict["phase2-private-key-password-flags"] = TypeConvert.py2_dbus_uint32(new_phase2_private_key_password_flags)

    @property
    def phase2_private_key(self):
        if "phase2-private-key" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["phase2-private-key"])

    @phase2_private_key.setter
    def phase2_private_key(self, new_phase2_private_key):
        self.prop_dict["phase2-private-key"] = TypeConvert.py2_dbus_bytearray(new_phase2_private_key)

    # def get_phase2_private_key_scheme(self):
    #     return self.get_cert_scheme(self.phase2_private_key)

    # def get_phase2_private_key_blob(self):
    #     pass

    # def get_phase2_private_key_path(self):
    #     pass

    # def set_phase2_private_key(self):
    #     pass

    # def get_phase2_private_key_format(self):
    #     pass

    @property
    def pin(self):
        if "pin" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["pin"])

    @pin.setter
    def pin(self, new_pin):
        self.prop_dict["pin"] = TypeConvert.py2_dbus_string(new_pin)

    @property
    def pin_flags(self):
        if "pin-flags" in self.prop_dict.iterkeys():
            return TypeConvert.dbus2py(self.prop_dict["pin-flags"])

    @pin_flags.setter
    def pin_flags(self ,new_pin_flags):
        self.prop_dict["pin-flags"] = TypeConvert.py2_dbus_uint32(new_pin_flags)


    def adapt_8021x_commit(self):
        if self.prop_dict["eap"][0] == "md5":
            self.adapt_eap_md5()
        elif self.prop_dict["eap"][0] == "tls":
            self.adapt_eap_tls()
        elif self.prop_dict["eap"][0] == "fast":
            self.adapt_eap_fast()
        elif self.prop_dict["eap"][0] == "ttls":
            self.adapt_eap_ttls()
        elif self.prop_dict["eap"][0] == "peap":
            self.adapt_eap_peap()
        else:
            pass

    def adapt_eap_md5(self):
        for key in self.prop_dict.iterkeys():
            if key not in ["eap", "identity", "password"]:
                del self.prop_dict[key]

    def adapt_eap_tls(self):
        for key in self.prop_dict.iterkeys():
            if key not in ["eap", "identity", "ca-cert", "client-cert","private-key", "private-key-password"]:
                del self.prop_dict[key]

    def adapt_eap_fast(self):
        for key in self.prop_dict.iterkeys():
            if key not in ["eap", "anonymous-identity", "identity", "phase1-fast-provisioning",
                           "phase2-auth", "password", "pac-file"]:
                del self.prop_dict[key]

    def adapt_eap_ttls(self):
        for key in self.prop_dict.iterkeys():
            if key not in ["eap", "anonymous-identity", "identity", "ca-cert", "phase2-auth", "password"]:
                del self.prop_dict[key]

    def adapt_eap_peap(self):
        for key in self.prop_dict.iterkeys():
            if key not in ["eap", "anonymous-identity", "identity", "ca-cert", "phase2-auth", "password", "phase1-peapver"]:
                del self.prop_dict[key]
