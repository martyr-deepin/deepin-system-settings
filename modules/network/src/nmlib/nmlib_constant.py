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

class NMClientPermission ():

    	NM_CLIENT_PERMISSION_NONE = 0
	NM_CLIENT_PERMISSION_ENABLE_DISABLE_NETWORK = 1
	NM_CLIENT_PERMISSION_ENABLE_DISABLE_WIFI = 2
	NM_CLIENT_PERMISSION_ENABLE_DISABLE_WWAN = 3
	NM_CLIENT_PERMISSION_ENABLE_DISABLE_WIMAX = 4
	NM_CLIENT_PERMISSION_SLEEP_WAKE = 5
	NM_CLIENT_PERMISSION_NETWORK_CONTROL = 6
	NM_CLIENT_PERMISSION_WIFI_SHARE_PROTECTED = 7
	NM_CLIENT_PERMISSION_WIFI_SHARE_OPEN = 8
	NM_CLIENT_PERMISSION_SETTINGS_MODIFY_SYSTEM = 9
	NM_CLIENT_PERMISSION_SETTINGS_MODIFY_OWN = 10
	NM_CLIENT_PERMISSION_SETTINGS_MODIFY_HOSTNAME = 11
	NM_CLIENT_PERMISSION_LAST = NM_CLIENT_PERMISSION_SETTINGS_MODIFY_HOSTNAME

class NMClientPermissionResult ():
    
    	NM_CLIENT_PERMISSION_RESULT_UNKNOWN = 0
	NM_CLIENT_PERMISSION_RESULT_YES = 1
	NM_CLIENT_PERMISSION_RESULT_AUTH = 2
	NM_CLIENT_PERMISSION_RESULT_NO = 3

class NMWimaxNspNetworkType ():

	NM_WIMAX_NSP_NETWORK_TYPE_UNKNOWN         = 0
	NM_WIMAX_NSP_NETWORK_TYPE_HOME            = 1
	NM_WIMAX_NSP_NETWORK_TYPE_PARTNER         = 2
	NM_WIMAX_NSP_NETWORK_TYPE_ROAMING_PARTNER = 3

class NMSecretAgentError ():

	NM_SECRET_AGENT_ERROR_NOT_AUTHORIZED = 0
	NM_SECRET_AGENT_ERROR_INVALID_CONNECTION = 1
	NM_SECRET_AGENT_ERROR_USER_CANCELED = 2
	NM_SECRET_AGENT_ERROR_AGENT_CANCELED = 3 
	NM_SECRET_AGENT_ERROR_INTERNAL_ERROR = 4
	NM_SECRET_AGENT_ERROR_NO_SECRETS = 5

class NMSecretAgentGetSecretsFlags ():

	NM_SECRET_AGENT_GET_SECRETS_FLAG_NONE = 0x0
	NM_SECRET_AGENT_GET_SECRETS_FLAG_ALLOW_INTERACTION = 0x1
	NM_SECRET_AGENT_GET_SECRETS_FLAG_REQUEST_NEW = 0x2

if __name__ == "__main__":
    print NMClientPermissionResult.NM_CLIENT_PERMISSION_RESULT_NO
    print NMClientPermission.NM_CLIENT_PERMISSION_SETTINGS_MODIFY_HOSTNAME
    print NMClientPermission.NM_CLIENT_PERMISSION_SETTINGS_MODIFY_SYSTEM