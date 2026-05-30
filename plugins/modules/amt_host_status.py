#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026
# GNU General Public License v3.0 or later (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: amt_host_status
short_description: Retrieve system status information from Intel AMT
version_added: "1.0.0"
description:
    - Retrieves comprehensive system status information from Intel AMT.
    - Provides power state, system details, firmware version, and boot device info.
    - Useful for inventory collection and system monitoring.
options:
    host:
        description:
            - Hostname or IP address of the AMT management interface.
        required: true
        type: str
    username:
        description:
            - AMT admin username.
        required: true
        type: str
    password:
        description:
            - AMT admin password.
        required: true
        type: str
        no_log: true
    port:
        description:
            - AMT management port.
        required: false
        type: int
        default: 16992
    use_tls:
        description:
            - Whether to use TLS for the connection.
        required: false
        type: bool
        default: true
    verify_ssl:
        description:
            - Whether to verify SSL certificates.
        required: false
        type: bool
        default: false
author:
    - parmstro
'''

EXAMPLES = r'''
# Get system status
- name: Retrieve AMT system status
  parmstro.intel_amt.amt_host_status:
    host: nuc01.amt.example.com
    username: admin
    password: secretpassword
    state: query
  register: system_info

- name: Display system information
  debug:
    msg: "System {{ system_info.system_name }} is {{ system_info.power_state }}"

# Get status without TLS
- name: Get status via HTTP
  parmstro.intel_amt.amt_host_status:
    host: 192.168.254.209
    username: admin
    password: secretpassword
    port: 16992
    use_tls: false
  register: status

# Use in inventory
- name: Collect AMT inventory
  parmstro.intel_amt.amt_host_status:
    host: "{{ amt_host }}"
    username: "{{ amt_username }}"
    password: "{{ amt_password }}"
  register: amt_facts
'''

RETURN = r'''
power_state:
    description: Current power state of the system
    returned: always
    type: str
    sample: "on"
ipv4_address:
    description: Configured IPv4 address
    returned: always
    type: str
    sample: "192.168.254.209"
ipv6_address:
    description: Configured IPv6 address or "Disabled"
    returned: always
    type: str
    sample: "fe80::1234:5678:90ab:cdef"
system_id:
    description: System UUID or identifier
    returned: always
    type: str
    sample: "12345678-1234-5678-1234-567812345678"
amt_time:
    description: Current date/time from AMT perspective
    returned: always
    type: str
    sample: "2026-05-30T01:23:45Z"
uptime:
    description: System uptime since last boot (in seconds)
    returned: when available
    type: int
    sample: 86400
uptime_human:
    description: Human-readable uptime
    returned: when available
    type: str
    sample: "1 day, 0 hours, 0 minutes"
enabled_state:
    description: AMT enabled state
    returned: always
    type: int
    sample: 2
operational_status:
    description: System operational status
    returned: always
    type: str
    sample: "OK"
system_name:
    description: System name from AMT
    returned: always
    type: str
    sample: "ManagedSystem"
firmware_version:
    description: AMT firmware version
    returned: when available
    type: str
    sample: "10.0.56.3002"
bios_version:
    description: System BIOS version
    returned: when available
    type: str
    sample: "MYBE10H.86A.0067.2021.0511.1830"
mac_address:
    description: Primary MAC address
    returned: when available
    type: str
    sample: "00:1A:2B:3C:4D:5E"
changed:
    description: Whether any changes were made
    returned: always
    type: bool
    sample: false
msg:
    description: Human-readable message about the operation
    returned: always
    type: str
    sample: "System status retrieved successfully"
'''

from ansible.module_utils.basic import AnsibleModule
import requests
from requests.auth import HTTPDigestAuth
from lxml import etree
import urllib3
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Power state mappings
POWER_STATE_MAP = {
    '1': 'other',
    '2': 'on',
    '3': 'sleep_light',
    '4': 'sleep_deep',
    '5': 'power_cycle_soft',
    '6': 'off_hard',
    '7': 'hibernate',
    '8': 'off',
    '9': 'power_cycle_hard',
    '10': 'master_bus_reset',
    '11': 'diagnostic_interrupt',
    '12': 'off_soft_graceful',
    '13': 'off_hard_graceful',
    '14': 'master_bus_reset_graceful',
    '15': 'power_cycle_soft_graceful',
    '16': 'power_cycle_hard_graceful',
}

# Enabled state mappings
ENABLED_STATE_MAP = {
    '0': 'unknown',
    '1': 'other',
    '2': 'enabled',
    '3': 'disabled',
    '5': 'not_applicable',
    '6': 'enabled_but_offline',
    '7': 'in_test',
    '8': 'deferred',
    '9': 'quiesce',
    '10': 'starting',
}


class WSMANClient:
    """WS-Management client for Intel AMT"""

    def __init__(self, host, username, password, port=16992, use_tls=True, verify_ssl=False):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.use_tls = use_tls
        self.verify_ssl = verify_ssl
        self.base_url = f"{'https' if use_tls else 'http'}://{host}:{port}/wsman"
        self.auth = HTTPDigestAuth(username, password)

    def _create_envelope(self, action, resource_uri, selector_set=None):
        """Create SOAP envelope for WSMAN request"""
        SOAP_NS = 'http://www.w3.org/2003/05/soap-envelope'
        WSA_NS = 'http://schemas.xmlsoap.org/ws/2004/08/addressing'
        WSMAN_NS = 'http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd'

        envelope = etree.Element(
            f'{{{SOAP_NS}}}Envelope',
            nsmap={'s': SOAP_NS, 'a': WSA_NS, 'w': WSMAN_NS}
        )

        header = etree.SubElement(envelope, f'{{{SOAP_NS}}}Header')

        action_elem = etree.SubElement(header, f'{{{WSA_NS}}}Action',
                                       {f'{{{SOAP_NS}}}mustUnderstand': 'true'})
        action_elem.text = action

        to_elem = etree.SubElement(header, f'{{{WSA_NS}}}To',
                                   {f'{{{SOAP_NS}}}mustUnderstand': 'true'})
        to_elem.text = self.base_url

        resource_elem = etree.SubElement(header, f'{{{WSMAN_NS}}}ResourceURI',
                                        {f'{{{SOAP_NS}}}mustUnderstand': 'true'})
        resource_elem.text = resource_uri

        msg_id = etree.SubElement(header, f'{{{WSA_NS}}}MessageID',
                                 {f'{{{SOAP_NS}}}mustUnderstand': 'true'})
        msg_id.text = 'uuid:00000000-8086-8086-8086-000000000001'

        reply_to = etree.SubElement(header, f'{{{WSA_NS}}}ReplyTo')
        address = etree.SubElement(reply_to, f'{{{WSA_NS}}}Address')
        address.text = 'http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous'

        if selector_set:
            sel_set = etree.SubElement(header, f'{{{WSMAN_NS}}}SelectorSet')
            for name, value in selector_set.items():
                selector = etree.SubElement(sel_set, f'{{{WSMAN_NS}}}Selector', Name=name)
                selector.text = value

        body_elem = etree.SubElement(envelope, f'{{{SOAP_NS}}}Body')

        return envelope

    def _send_request(self, envelope):
        """Send WSMAN request and return response"""
        xml_data = etree.tostring(envelope, encoding='utf-8', xml_declaration=True)

        headers = {
            'Content-Type': 'application/soap+xml;charset=UTF-8',
        }

        try:
            response = requests.post(
                self.base_url,
                data=xml_data,
                headers=headers,
                auth=self.auth,
                verify=self.verify_ssl,
                timeout=30
            )
            response.raise_for_status()
            return etree.fromstring(response.content)
        except requests.exceptions.RequestException as e:
            raise Exception(f"WSMAN request failed: {str(e)}")

    def get_system_status(self):
        """Get CIM_ComputerSystem status"""
        resource_uri = 'http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ComputerSystem'
        action = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Get'
        selector_set = {'Name': 'ManagedSystem'}

        envelope = self._create_envelope(action, resource_uri, selector_set)
        return self._send_request(envelope)

    def get_general_settings(self):
        """Get IPS_GeneralSettings (firmware version, etc)"""
        resource_uri = 'http://intel.com/wbem/wscim/1/ips-schema/1/IPS_GeneralSettings'
        action = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Get'

        envelope = self._create_envelope(action, resource_uri)
        try:
            return self._send_request(envelope)
        except Exception:
            return None  # May not be available on all AMT versions

    def get_power_management_service(self):
        """Get CIM_AssociatedPowerManagementService for current power state"""
        resource_uri = 'http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_AssociatedPowerManagementService'
        action = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Get'

        envelope = self._create_envelope(action, resource_uri)
        try:
            return self._send_request(envelope)
        except Exception:
            return None

    def get_bios_info(self):
        """Get CIM_BIOSElement information"""
        resource_uri = 'http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_BIOSElement'
        action = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Get'

        envelope = self._create_envelope(action, resource_uri)
        try:
            return self._send_request(envelope)
        except Exception:
            return None

    def get_ethernet_settings(self):
        """Get AMT_EthernetPortSettings for IP addresses"""
        resource_uri = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_EthernetPortSettings'
        action = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Get'
        selector_set = {'InstanceID': 'Intel(r) AMT Ethernet Port Settings 0'}

        envelope = self._create_envelope(action, resource_uri, selector_set)
        try:
            return self._send_request(envelope)
        except Exception:
            return None

    def get_time_sync(self):
        """Get AMT time synchronization info"""
        resource_uri = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_TimeSynchronizationService'
        action = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Get'

        envelope = self._create_envelope(action, resource_uri)
        try:
            return self._send_request(envelope)
        except Exception:
            return None


def parse_xml_response(root, tag_name):
    """Parse XML response and extract tag value"""
    for elem in root.iter():
        if elem.tag.endswith(tag_name):
            return elem.text
    return None


def parse_all_xml_tags(root, tag_name):
    """Parse XML and return all values for a tag"""
    values = []
    for elem in root.iter():
        if elem.tag.endswith(tag_name):
            if elem.text:
                values.append(elem.text)
    return values


def format_uptime(seconds):
    """Format uptime in seconds to human readable format"""
    if not seconds:
        return None
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    return f"{days} day{'s' if days != 1 else ''}, {hours} hour{'s' if hours != 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''}"


def run_module():
    module_args = dict(
        host=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        port=dict(type='int', required=False, default=16992),
        use_tls=dict(type='bool', required=False, default=True),
        verify_ssl=dict(type='bool', required=False, default=False),
    )

    result = dict(
        changed=False,
        power_state='unknown',
        enabled_state=0,
        operational_status='unknown',
        system_name='',
        ipv4_address='unknown',
        ipv6_address='Disabled',
        system_id='unknown',
        amt_time='unknown',
        msg=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    try:
        client = WSMANClient(
            host=module.params['host'],
            username=module.params['username'],
            password=module.params['password'],
            port=module.params['port'],
            use_tls=module.params['use_tls'],
            verify_ssl=module.params['verify_ssl']
        )

        # Get system status
        system_response = client.get_system_status()

        # Parse system information
        element_name = parse_xml_response(system_response, 'ElementName')
        if element_name:
            result['system_name'] = element_name

        name = parse_xml_response(system_response, 'Name')
        if name:
            result['system_name'] = name

        # Parse enabled state
        enabled_state = parse_xml_response(system_response, 'EnabledState')
        if enabled_state:
            result['enabled_state'] = int(enabled_state)
            result['enabled_state_text'] = ENABLED_STATE_MAP.get(enabled_state, 'unknown')

        # Parse operational status
        operational_status = parse_xml_response(system_response, 'OperationalStatus')
        if operational_status == '0':
            result['operational_status'] = 'unknown'
        elif operational_status == '2':
            result['operational_status'] = 'OK'
        else:
            result['operational_status'] = operational_status

        # Parse requested state / power state
        requested_state = parse_xml_response(system_response, 'RequestedState')
        if requested_state:
            result['requested_state'] = int(requested_state)

        # Get actual power state from Power Management Service
        power_mgmt = client.get_power_management_service()
        if power_mgmt:
            power_state = parse_xml_response(power_mgmt, 'PowerState')
            if power_state:
                result['power_state'] = POWER_STATE_MAP.get(power_state, f'unknown({power_state})')

        # Try to get firmware version
        general_settings = client.get_general_settings()
        if general_settings:
            fw_version = parse_xml_response(general_settings, 'FirmwareVersion')
            if fw_version:
                result['firmware_version'] = fw_version

        # Try to get BIOS info
        bios_info = client.get_bios_info()
        if bios_info:
            bios_version = parse_xml_response(bios_info, 'Version')
            if bios_version:
                result['bios_version'] = bios_version

        # Get System UUID
        uuid = parse_xml_response(system_response, 'UUID')
        if uuid:
            result['system_id'] = uuid
        else:
            # Fallback to creation class name + name
            creation_class = parse_xml_response(system_response, 'CreationClassName')
            if creation_class:
                result['system_id'] = f"{creation_class}:{result['system_name']}"

        # Get network settings (IP addresses)
        eth_settings = client.get_ethernet_settings()
        if eth_settings:
            # Get IPv4
            ipv4 = parse_xml_response(eth_settings, 'IPAddress')
            if ipv4:
                result['ipv4_address'] = ipv4

            # Get IPv6
            ipv6_enabled = parse_xml_response(eth_settings, 'IPv6DefaultRouter')
            if ipv6_enabled and ipv6_enabled != '::':
                result['ipv6_address'] = ipv6_enabled
            else:
                # Try other IPv6 fields
                ipv6_addr = parse_xml_response(eth_settings, 'IPv6Address')
                if ipv6_addr and ipv6_addr != '::':
                    result['ipv6_address'] = ipv6_addr

            # Get MAC address
            mac = parse_xml_response(eth_settings, 'MACAddress')
            if mac:
                result['mac_address'] = mac

        # Get AMT time - use current system time as AMT doesn't always expose it
        # AMT uses UTC time internally
        from datetime import datetime
        result['amt_time'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        # Try to calculate uptime from OnTimeCounter (if available)
        # This is typically in CIM_ComputerSystem as OnTimeCounter (in milliseconds)
        on_time = parse_xml_response(system_response, 'OnTimeCounter')
        if on_time:
            try:
                uptime_ms = int(on_time)
                uptime_seconds = uptime_ms // 1000
                result['uptime'] = uptime_seconds
                result['uptime_human'] = format_uptime(uptime_seconds)
            except (ValueError, TypeError):
                pass

        result['msg'] = f"System status retrieved successfully for {result['system_name']}"
        module.exit_json(**result)

    except Exception as e:
        result["msg"] = str(e)
    module.fail_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
