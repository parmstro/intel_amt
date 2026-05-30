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
module: amt_log_clear
short_description: Clear Intel AMT event logs
version_added: "1.0.0"
description:
    - Clears the Intel AMT event log.
    - Can clear specific log types or all logs.
    - Useful for maintenance and troubleshooting.
    - Supports check mode to preview without clearing.
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
    log_type:
        description:
            - Type of log to clear.
        required: false
        type: str
        choices: ['message', 'provisioning', 'all']
        default: 'message'
author:
    - parmstro
'''

EXAMPLES = r'''
# Clear the message log
- name: Clear AMT message log
  parmstro.intel_amt.amt_log_clear:
    host: nuc01.amt.example.com
    username: admin
    password: secretpassword

# Clear all logs
- name: Clear all AMT logs
  parmstro.intel_amt.amt_log_clear:
    host: nuc01.amt.example.com
    username: admin
    password: secretpassword
    log_type: all

# Check mode - preview without clearing
- name: Check what would be cleared
  parmstro.intel_amt.amt_log_clear:
    host: nuc01.amt.example.com
    username: admin
    password: secretpassword
  check_mode: true

# Clear logs on fleet
- name: Clear logs on all NUCs
  parmstro.intel_amt.amt_log_clear:
    host: "{{ amt_host }}"
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
  loop: "{{ groups['nucs'] }}"
'''

RETURN = r'''
log_type:
    description: Type of log that was cleared
    returned: always
    type: str
    sample: "message"
records_before:
    description: Number of records before clearing
    returned: when available
    type: int
    sample: 42
changed:
    description: Whether the log was cleared
    returned: always
    type: bool
    sample: true
msg:
    description: Human-readable message about the operation
    returned: always
    type: str
    sample: "AMT message log cleared successfully"
'''

from ansible.module_utils.basic import AnsibleModule
import requests
from requests.auth import HTTPDigestAuth
from lxml import etree
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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

    def get_log_info(self, log_type='message'):
        """Get log information before clearing"""
        if log_type == 'message':
            resource_uri = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_MessageLog'
        elif log_type == 'provisioning':
            resource_uri = 'http://intel.com/wbem/wscim/1/ips-schema/1/IPS_ProvisioningRecordLog'
        else:
            return None

        action = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Get'
        envelope = self._create_envelope(action, resource_uri)

        try:
            return self._send_request(envelope)
        except Exception:
            return None

    def clear_log(self, log_type='message'):
        """Clear the specified log"""
        if log_type == 'message':
            resource_uri = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_MessageLog'
            action = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_MessageLog/ClearLog'
        elif log_type == 'provisioning':
            resource_uri = 'http://intel.com/wbem/wscim/1/ips-schema/1/IPS_ProvisioningRecordLog'
            action = 'http://intel.com/wbem/wscim/1/ips-schema/1/IPS_ProvisioningRecordLog/ClearLog'
        else:
            raise ValueError(f"Invalid log type: {log_type}")

        # Create ClearLog request
        if log_type == 'message':
            AMT_NS = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_MessageLog'
        else:
            AMT_NS = 'http://intel.com/wbem/wscim/1/ips-schema/1/IPS_ProvisioningRecordLog'

        body = etree.Element(f'{{{AMT_NS}}}ClearLog_INPUT')

        envelope = self._create_envelope(action, resource_uri, body)
        return self._send_request(envelope)


def parse_xml_response(root, tag_name):
    """Parse XML response and extract tag value"""
    for elem in root.iter():
        if elem.tag.endswith(tag_name):
            return elem.text
    return None


def run_module():
    module_args = dict(
        host=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        port=dict(type='int', required=False, default=16992),
        use_tls=dict(type='bool', required=False, default=True),
        verify_ssl=dict(type='bool', required=False, default=False),
        log_type=dict(type='str', required=False, default='message',
                     choices=['message', 'provisioning', 'all']),
    )

    result = dict(
        changed=False,
        log_type='',
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

        log_type = module.params['log_type']
        logs_to_clear = []

        if log_type == 'all':
            logs_to_clear = ['message', 'provisioning']
        else:
            logs_to_clear = [log_type]

        # Get log info before clearing
        for log in logs_to_clear:
            log_info = client.get_log_info(log)
            if log_info:
                num_records = parse_xml_response(log_info, 'CurrentNumberOfRecords')
                if num_records:
                    result[f'{log}_records_before'] = int(num_records)

        if module.check_mode:
            result['changed'] = True
            result['log_type'] = log_type
            result['msg'] = f"Would clear {log_type} log(s) (check mode)"
            module.exit_json(**result)

        # Actually clear the logs
        cleared_logs = []
        for log in logs_to_clear:
            try:
                response = client.clear_log(log)
                # Check return value
                return_value = parse_xml_response(response, 'ReturnValue')
                if return_value == '0':
                    cleared_logs.append(log)
                else:
                    module.warn(f"Clear {log} log returned non-zero: {return_value}")
            except Exception as e:
                module.warn(f"Failed to clear {log} log: {str(e)}")

        if cleared_logs:
            result['changed'] = True
            result['log_type'] = log_type
            if len(cleared_logs) == 1:
                result['msg'] = f"AMT {cleared_logs[0]} log cleared successfully"
            else:
                result['msg'] = f"AMT logs cleared: {', '.join(cleared_logs)}"
        else:
            result['msg'] = "No logs were cleared"

        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=str(e), **result)


def main():
    run_module()


if __name__ == '__main__':
    main()
