#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: amt_power
short_description: Manage power state of Intel AMT systems
version_added: "1.0.0"
description:
    - Power on, power off, reboot, or check power state of systems with Intel AMT.
    - Uses WS-Management protocol to communicate with Intel AMT firmware.
    - Suitable for managing Intel NUC and other AMT-enabled systems.
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
    state:
        description:
            - Desired power state.
            - C(on) powers on the system.
            - C(off) gracefully powers off the system.
            - C(reboot) reboots the system.
            - C(cycle) performs a hard power cycle.
            - C(query) checks the current power state without changing it.
        required: true
        type: str
        choices: ['on', 'off', 'reboot', 'cycle', 'query']
author:
    - Your Name
'''

EXAMPLES = r'''
# Power on a system
- name: Power on NUC
  parmstro.intel_amt.amt_power:
    host: 192.168.1.100
    username: admin
    password: secretpassword
    state: 'on'

# Reboot a system
- name: Reboot NUC
  parmstro.intel_amt.amt_power:
    host: nuc01.example.com
    username: admin
    password: secretpassword
    state: reboot

# Check power state
- name: Query power state
  parmstro.intel_amt.amt_power:
    host: 192.168.1.100
    username: admin
    password: secretpassword
    state: query
  register: power_status

# Power off with non-TLS connection
- name: Power off NUC
  parmstro.intel_amt.amt_power:
    host: 192.168.1.100
    username: admin
    password: secretpassword
    port: 16993
    use_tls: false
    state: 'off'
'''

RETURN = r'''
power_state:
    description: Current power state of the system
    returned: always
    type: str
    sample: "on"
changed:
    description: Whether the power state was changed
    returned: always
    type: bool
    sample: true
msg:
    description: Human-readable message about the operation
    returned: always
    type: str
    sample: "System powered on successfully"
'''

from ansible.module_utils.basic import AnsibleModule
import requests
from requests.auth import HTTPDigestAuth
from lxml import etree
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# AMT Power States
POWER_STATES = {
    'on': 2,
    'sleep': 3,
    'cycle': 5,
    'off_hard': 6,
    'off': 8,
    'cycle_hard': 9,
    'reboot': 10,
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

    def _create_envelope(self, action, resource_uri, body=None, selector_set=None):
        """Create SOAP envelope for WSMAN request"""
        SOAP_NS = 'http://www.w3.org/2003/05/soap-envelope'
        WSA_NS = 'http://schemas.xmlsoap.org/ws/2004/08/addressing'
        WSMAN_NS = 'http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd'

        envelope = etree.Element(
            f'{{{SOAP_NS}}}Envelope',
            nsmap={'s': SOAP_NS,
                   'a': WSA_NS,
                   'w': WSMAN_NS}
        )

        header = etree.SubElement(envelope, f'{{{SOAP_NS}}}Header')

        # Action with mustUnderstand
        action_elem = etree.SubElement(header, f'{{{WSA_NS}}}Action',
                                       {f'{{{SOAP_NS}}}mustUnderstand': 'true'})
        action_elem.text = action

        # To with mustUnderstand
        to_elem = etree.SubElement(header, f'{{{WSA_NS}}}To',
                                   {f'{{{SOAP_NS}}}mustUnderstand': 'true'})
        to_elem.text = self.base_url

        # ResourceURI with mustUnderstand
        resource_elem = etree.SubElement(header, f'{{{WSMAN_NS}}}ResourceURI',
                                        {f'{{{SOAP_NS}}}mustUnderstand': 'true'})
        resource_elem.text = resource_uri

        # MessageID with mustUnderstand
        msg_id = etree.SubElement(header, f'{{{WSA_NS}}}MessageID',
                                 {f'{{{SOAP_NS}}}mustUnderstand': 'true'})
        msg_id.text = 'uuid:00000000-8086-8086-8086-000000000001'

        # ReplyTo
        reply_to = etree.SubElement(header, f'{{{WSA_NS}}}ReplyTo')
        address = etree.SubElement(reply_to, f'{{{WSA_NS}}}Address')
        address.text = 'http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous'

        # SelectorSet if provided
        if selector_set:
            sel_set = etree.SubElement(header, f'{{{WSMAN_NS}}}SelectorSet')
            for name, value in selector_set.items():
                selector = etree.SubElement(sel_set, f'{{{WSMAN_NS}}}Selector', Name=name)
                selector.text = value

        # Body
        body_elem = etree.SubElement(envelope, f'{{{SOAP_NS}}}Body')
        if body is not None:
            body_elem.append(body)

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

    def get_power_state(self):
        """Get current power state"""
        resource_uri = 'http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_AssociatedPowerManagementService'
        action = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Get'

        envelope = self._create_envelope(action, resource_uri)
        response = self._send_request(envelope)
        return response

    def set_power_state(self, state):
        """Set power state"""
        if state not in POWER_STATES:
            raise ValueError(f"Invalid power state: {state}")

        CIM_NS = 'http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_PowerManagementService'
        WSA_NS = 'http://schemas.xmlsoap.org/ws/2004/08/addressing'
        WSMAN_NS = 'http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd'

        resource_uri = CIM_NS
        action = f'{CIM_NS}/RequestPowerStateChange'

        # Selector for the PowerManagementService
        selector_set = {'Name': 'Intel(r) AMT Power Management Service'}

        # Create body with proper namespace prefix
        body = etree.Element(
            f'{{{CIM_NS}}}RequestPowerStateChange_INPUT',
            nsmap={'p': CIM_NS, 'a': WSA_NS, 'w': WSMAN_NS}
        )

        power_state_elem = etree.SubElement(body, f'{{{CIM_NS}}}PowerState')
        power_state_elem.text = str(POWER_STATES[state])

        managed_elem = etree.SubElement(body, f'{{{CIM_NS}}}ManagedElement')
        address = etree.SubElement(managed_elem, f'{{{WSA_NS}}}Address')
        address.text = 'http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous'
        reference_params = etree.SubElement(managed_elem, f'{{{WSA_NS}}}ReferenceParameters')
        resource_uri_elem = etree.SubElement(reference_params, f'{{{WSMAN_NS}}}ResourceURI')
        resource_uri_elem.text = 'http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ComputerSystem'
        selector_set_body = etree.SubElement(reference_params, f'{{{WSMAN_NS}}}SelectorSet')
        selector = etree.SubElement(selector_set_body, f'{{{WSMAN_NS}}}Selector', Name='Name')
        selector.text = 'ManagedSystem'

        envelope = self._create_envelope(action, resource_uri, body, selector_set)
        response = self._send_request(envelope)
        return response


def run_module():
    module_args = dict(
        host=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        port=dict(type='int', required=False, default=16992),
        use_tls=dict(type='bool', required=False, default=True),
        verify_ssl=dict(type='bool', required=False, default=False),
        state=dict(type='str', required=True, choices=['on', 'off', 'reboot', 'cycle', 'query']),
    )

    result = dict(
        changed=False,
        power_state='unknown',
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

        state = module.params['state']

        if state == 'query':
            # Just query current state
            response = client.get_power_state()
            result['msg'] = 'Power state queried successfully'
            result['changed'] = False
        elif module.check_mode:
            # In check mode, don't actually change anything
            result['msg'] = f'Would change power state to {state}'
            result['changed'] = True
        else:
            # Actually change the power state
            response = client.set_power_state(state)
            result['msg'] = f'Power state changed to {state}'
            result['changed'] = True
            result['power_state'] = state

        module.exit_json(**result)

    except Exception as e:
        result["msg"] = str(e)
    module.fail_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
