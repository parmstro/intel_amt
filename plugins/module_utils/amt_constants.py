#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026
# GNU General Public License v3.0 or later (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Intel AMT constants and resource URIs
Shared configuration for all AMT modules
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

# Default port numbers
AMT_HTTP_PORT = 16992
AMT_HTTPS_PORT = 16993

# Common WSMAN namespaces
NS_SOAP = 'http://www.w3.org/2003/05/soap-envelope'
NS_WSA = 'http://schemas.xmlsoap.org/ws/2004/08/addressing'
NS_WSMAN = 'http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd'

# Intel AMT resource URIs
AMT_GENERAL_SETTINGS = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_GeneralSettings'
AMT_ETHERNET_PORT_SETTINGS = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_EthernetPortSettings'
AMT_SETUP_AND_CONFIG_SERVICE = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_SetupAndConfigurationService'
AMT_AUTHORIZATION_SERVICE = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_AuthorizationService'
AMT_TLS_SETTINGS = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_TLSSettingData'
AMT_TLS_CREDENTIAL_CONTEXT = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_TLSCredentialContext'
AMT_PUBLIC_KEY_MANAGEMENT = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_PublicKeyManagementService'

# CIM (DMTF) resource URIs
CIM_POWER_MANAGEMENT_SERVICE = 'http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_PowerManagementService'
CIM_ASSOCIATED_POWER_MANAGEMENT_SERVICE = 'http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_AssociatedPowerManagementService'
CIM_BOOT_CONFIG_SETTING = 'http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_BootConfigSetting'
CIM_BOOT_SERVICE = 'http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_BootService'

# Common selectors
SELECTOR_GENERAL_SETTINGS = {'InstanceID': 'Intel(r) AMT: General Settings'}
SELECTOR_ETHERNET_PORT_0 = {'InstanceID': 'Intel(r) AMT Ethernet Port Settings 0'}
SELECTOR_POWER_MANAGEMENT_SERVICE = {'Name': 'Intel(r) AMT Power Management Service'}

# WSMAN Actions
ACTION_GET = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Get'
ACTION_PUT = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Put'
ACTION_CREATE = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Create'
ACTION_DELETE = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Delete'
ACTION_ENUMERATE = 'http://schemas.xmlsoap.org/ws/2004/09/enumeration/Enumerate'
ACTION_PULL = 'http://schemas.xmlsoap.org/ws/2004/09/enumeration/Pull'

# Power states (CIM_PowerManagementService)
POWER_STATE_ON = 2
POWER_STATE_SLEEP_LIGHT = 3
POWER_STATE_SLEEP_DEEP = 4
POWER_STATE_POWER_CYCLE_HARD = 5
POWER_STATE_OFF_HARD = 8
POWER_STATE_HIBERNATE = 7
POWER_STATE_OFF_SOFT = 9
POWER_STATE_POWER_CYCLE_SOFT = 10
POWER_STATE_MASTER_BUS_RESET = 11
POWER_STATE_DIAGNOSTIC_INTERRUPT = 12
POWER_STATE_OFF_SOFT_GRACEFUL = 13
POWER_STATE_OFF_HARD_GRACEFUL = 14
POWER_STATE_MASTER_BUS_RESET_GRACEFUL = 15
POWER_STATE_POWER_CYCLE_SOFT_GRACEFUL = 16
POWER_STATE_POWER_CYCLE_HARD_GRACEFUL = 17

# Power state mappings
POWER_STATE_MAP = {
    'on': POWER_STATE_ON,
    'off': POWER_STATE_OFF_SOFT_GRACEFUL,
    'reboot': POWER_STATE_POWER_CYCLE_SOFT_GRACEFUL,
    'cycle': POWER_STATE_POWER_CYCLE_HARD,
    'reset': POWER_STATE_MASTER_BUS_RESET,
}

# Link policy values (AMT_EthernetPortSettings)
LINK_POLICY_S0_AC = 1          # S0 (powered on) AC
LINK_POLICY_SX_AC = 2          # Sx (sleep/hibernate) AC
LINK_POLICY_S0_DC = 14         # S0 (powered on) DC
LINK_POLICY_SX_DC = 15         # Sx (sleep/hibernate) DC
LINK_POLICY_ALWAYS_ON = 16     # Network link always on (enables WoL)

# Common argument spec for all modules
COMMON_ARG_SPEC = {
    'host': {'type': 'str', 'required': True},
    'username': {'type': 'str', 'required': True},
    'password': {'type': 'str', 'required': True, 'no_log': True},
    'port': {'type': 'int', 'required': False, 'default': AMT_HTTP_PORT},
    'use_tls': {'type': 'bool', 'required': False, 'default': True},
    'verify_ssl': {'type': 'bool', 'required': False, 'default': False},
}
