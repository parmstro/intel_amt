#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026
# GNU General Public License v3.0 or later (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: amt_system_settings
short_description: Manage Intel AMT system name and general settings
version_added: "1.0.0"
description:
    - Configure Intel AMT system name and hostname settings.
    - Manage general AMT configuration parameters.
    - Set domain and FQDN for AMT management interface.
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
    system_name:
        description:
            - System hostname for AMT.
            - This is the hostname reported by AMT, not the OS hostname.
        required: false
        type: str
    domain_name:
        description:
            - Domain name for AMT system.
            - Used to construct FQDN.
        required: false
        type: str
author:
    - parmstro
notes:
    - System name changes may require AMT service restart.
    - FQDN is constructed from system_name and domain_name.
    - Settings apply to AMT management interface, not OS configuration.
'''

EXAMPLES = r'''
# Query current system settings
- name: Get current AMT system settings
  parmstro.intel_amt.amt_system_settings:
    host: 192.168.254.209
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
  register: amt_settings

- name: Display settings
  ansible.builtin.debug:
    msg: "Hostname: {{ amt_settings.system_name }}, Domain: {{ amt_settings.domain_name }}"

# Set system name and domain (idempotent)
- name: Configure AMT FQDN
  parmstro.intel_amt.amt_system_settings:
    host: 192.168.254.209
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    system_name: c1s2n2
    domain_name: amt.parmstrong.ca

# Update hostname only
- name: Set AMT hostname
  parmstro.intel_amt.amt_system_settings:
    host: c1s2n2.amt.parmstrong.ca
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    system_name: c1s2n2

# Configure hostname across NUC fleet
- name: Set hostnames for all NUCs
  parmstro.intel_amt.amt_system_settings:
    host: "{{ item.amt_ip }}"
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    system_name: "c{{ item.chassis }}s{{ item.stack }}n{{ item.node }}"
    domain_name: amt.parmstrong.ca
  loop:
    - { amt_ip: "192.168.254.209", chassis: 1, stack: 2, node: 2 }
    - { amt_ip: "192.168.254.210", chassis: 1, stack: 2, node: 3 }
'''

RETURN = r'''
changed:
    description: Whether the system settings were changed
    returned: always
    type: bool
    sample: true
system_name:
    description: Current system name
    returned: always
    type: str
    sample: "c1s2n2"
domain_name:
    description: Current domain name
    returned: always
    type: str
    sample: "amt.parmstrong.ca"
fqdn:
    description: Fully qualified domain name
    returned: always
    type: str
    sample: "c1s2n2.amt.parmstrong.ca"
msg:
    description: Human-readable message about the operation
    returned: always
    type: str
    sample: "System settings updated successfully"
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
        headers = {'Content-Type': 'application/soap+xml;charset=UTF-8'}

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

    def get_general_settings(self):
        """Get current AMT_GeneralSettings"""
        resource_uri = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_GeneralSettings'
        selector_set = {'InstanceID': 'Intel(r) AMT: General Settings'}
        action = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Get'

        envelope = self._create_envelope(action, resource_uri, selector_set=selector_set)
        root = self._send_request(envelope)

        # Extract resource from body
        body = root.find('.//{http://www.w3.org/2003/05/soap-envelope}Body')
        if body is None or len(body) == 0:
            raise Exception("No data in WSMAN response body")

        return list(body)[0]

    def put_general_settings(self, resource_body):
        """Put modified AMT_GeneralSettings"""
        resource_uri = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_GeneralSettings'
        selector_set = {'InstanceID': 'Intel(r) AMT: General Settings'}
        action = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Put'

        envelope = self._create_envelope(action, resource_uri, body=resource_body, selector_set=selector_set)
        self._send_request(envelope)

    def configure_system_settings(self, system_name=None, domain_name=None):
        """Configure system name and domain settings via WSMAN"""
        AMT_NS = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_GeneralSettings'

        # Get current settings
        current = self.get_general_settings()

        # Extract current values
        current_hostname = current.find(f'.//{{{AMT_NS}}}HostName')
        current_domain = current.find(f'.//{{{AMT_NS}}}DomainName')

        old_hostname = current_hostname.text if current_hostname is not None else ''
        old_domain = current_domain.text if current_domain is not None else ''

        # Determine if changes needed
        changed = False

        if system_name is not None and system_name != old_hostname:
            current_hostname.text = system_name
            changed = True

        if domain_name is not None and domain_name != old_domain:
            current_domain.text = domain_name
            changed = True

        # Apply changes if needed
        if changed:
            self.put_general_settings(current)
            # Verify by reading back
            verify = self.get_general_settings()
            verify_hostname = verify.find(f'.//{{{AMT_NS}}}HostName')
            verify_domain = verify.find(f'.//{{{AMT_NS}}}DomainName')
            final_hostname = verify_hostname.text if verify_hostname is not None else ''
            final_domain = verify_domain.text if verify_domain is not None else ''
        else:
            final_hostname = old_hostname
            final_domain = old_domain

        # Construct FQDN
        if final_hostname and final_domain:
            fqdn = f"{final_hostname}.{final_domain}"
        elif final_hostname:
            fqdn = final_hostname
        else:
            fqdn = ''

        return {
            'system_name': final_hostname,
            'domain_name': final_domain,
            'fqdn': fqdn,
            'changed': changed
        }


def run_module():
    module_args = dict(
        host=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        port=dict(type='int', required=False, default=16992),
        use_tls=dict(type='bool', required=False, default=True),
        verify_ssl=dict(type='bool', required=False, default=False),
        system_name=dict(type='str', required=False),
        domain_name=dict(type='str', required=False),
    )

    result = dict(
        changed=False,
        system_name='',
        domain_name='',
        fqdn='',
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

        if module.check_mode:
            result['msg'] = 'Would configure system settings (check mode)'
            module.exit_json(**result)

        settings_result = client.configure_system_settings(
            system_name=module.params.get('system_name'),
            domain_name=module.params.get('domain_name')
        )

        result.update(settings_result)
        if result['changed']:
            result['msg'] = f"System settings updated: hostname={result['system_name']}, domain={result['domain_name']}"
        else:
            result['msg'] = f"System settings unchanged: hostname={result['system_name']}, domain={result['domain_name']}"

        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=str(e), **result)


def main():
    run_module()


if __name__ == '__main__':
    main()
