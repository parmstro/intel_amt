#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026
# GNU General Public License v3.0 or later (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: amt_power_policy
short_description: Manage Intel AMT power policy settings
version_added: "1.0.0"
description:
    - Configure power policy settings for Intel AMT systems.
    - Manage wake-on-LAN settings, idle timeouts, and power packages.
    - Control power-saving features and wake capabilities.
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
    wake_on_lan:
        description:
            - Enable or disable Wake-on-LAN functionality.
        required: false
        type: bool
    wake_on_alarm:
        description:
            - Enable or disable Wake-on-Alarm (scheduled wake).
        required: false
        type: bool
    idle_timeout:
        description:
            - Idle timeout in seconds before power state changes.
            - Set to 0 to disable idle timeout.
        required: false
        type: int
    link_policy:
        description:
            - Network link power policy.
            - C(always_on) keeps network active.
            - C(power_save) allows network to enter low power mode.
        required: false
        type: str
        choices: ['always_on', 'power_save']
author:
    - parmstro
notes:
    - Changes to power policy may require system reboot to take full effect.
    - Wake-on-LAN requires proper network configuration.
    - Power policies apply to the management interface.
'''

EXAMPLES = r'''
# Query current power policy
- name: Get current power policy settings
  parmstro.intel_amt.amt_power_policy:
    host: 192.168.254.209
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
  register: power_policy

- name: Display power policy
  ansible.builtin.debug:
    msg: "Idle timeout: {{ power_policy.idle_timeout }}s, Link policy: {{ power_policy.link_policy }}"

# Configure idle timeout (in seconds)
- name: Set idle timeout to 5 minutes
  parmstro.intel_amt.amt_power_policy:
    host: 192.168.254.209
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    idle_timeout: 300

# Disable idle timeout
- name: Disable idle wake timeout
  parmstro.intel_amt.amt_power_policy:
    host: c1s2n2.amt.parmstrong.ca
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    idle_timeout: 0

# Set network link to always-on (enables Wake-on-LAN capability)
- name: Configure always-on link policy
  parmstro.intel_amt.amt_power_policy:
    host: 192.168.254.209
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    link_policy: always_on

# Set power-saving link policy
- name: Enable network power saving
  parmstro.intel_amt.amt_power_policy:
    host: 192.168.254.209
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    link_policy: power_save

# Configure both idle timeout and link policy
- name: Set complete power policy
  parmstro.intel_amt.amt_power_policy:
    host: 192.168.254.209
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    idle_timeout: 1
    link_policy: always_on
'''

RETURN = r'''
changed:
    description: Whether the power policy was changed
    returned: always
    type: bool
    sample: true
wake_on_lan:
    description: Current Wake-on-LAN setting
    returned: always
    type: bool
    sample: true
wake_on_alarm:
    description: Current Wake-on-Alarm setting
    returned: always
    type: bool
    sample: true
idle_timeout:
    description: Current idle timeout in seconds
    returned: always
    type: int
    sample: 1800
link_policy:
    description: Current network link policy
    returned: always
    type: str
    sample: "always_on"
msg:
    description: Human-readable message about the operation
    returned: always
    type: str
    sample: "Power policy updated successfully"
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
        """Get AMT_GeneralSettings for idle timeout"""
        resource_uri = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_GeneralSettings'
        selector_set = {'InstanceID': 'Intel(r) AMT: General Settings'}
        action = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Get'

        envelope = self._create_envelope(action, resource_uri, selector_set=selector_set)
        root = self._send_request(envelope)
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

    def get_ethernet_port_settings(self):
        """Get AMT_EthernetPortSettings for link policy"""
        resource_uri = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_EthernetPortSettings'
        selector_set = {'InstanceID': 'Intel(r) AMT Ethernet Port Settings 0'}
        action = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Get'

        envelope = self._create_envelope(action, resource_uri, selector_set=selector_set)
        root = self._send_request(envelope)
        body = root.find('.//{http://www.w3.org/2003/05/soap-envelope}Body')
        if body is None or len(body) == 0:
            raise Exception("No data in WSMAN response body")
        return list(body)[0]

    def put_ethernet_port_settings(self, resource_body):
        """Put modified AMT_EthernetPortSettings"""
        resource_uri = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_EthernetPortSettings'
        selector_set = {'InstanceID': 'Intel(r) AMT Ethernet Port Settings 0'}
        action = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Put'

        envelope = self._create_envelope(action, resource_uri, body=resource_body, selector_set=selector_set)
        self._send_request(envelope)

    def configure_power_policy(self, wake_on_lan=None, idle_timeout=None, link_policy=None):
        """Configure power policy settings via WSMAN"""
        AMT_GEN_NS = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_GeneralSettings'
        AMT_ETH_NS = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_EthernetPortSettings'
        changed = False

        # Get current general settings for idle timeout
        gen_settings = self.get_general_settings()
        idle_elem = gen_settings.find(f'.//{{{AMT_GEN_NS}}}IdleWakeTimeout')
        current_idle = int(idle_elem.text) if idle_elem is not None else 1

        # Get current ethernet settings for link policy
        eth_settings = self.get_ethernet_port_settings()
        link_policy_elem = eth_settings.find(f'.//{{{AMT_ETH_NS}}}LinkPolicy')
        current_link_policies = []
        if link_policy_elem is not None:
            for policy_val in link_policy_elem.findall(f'.//{{{AMT_ETH_NS}}}PolicyValue'):
                current_link_policies.append(int(policy_val.text))

        # Determine link policy string from current values
        # Based on discovered values: [1, 14, 16] where 16 = always on
        has_always_on = 16 in current_link_policies
        current_link_policy_str = 'always_on' if has_always_on else 'power_save'

        # Apply idle timeout change if specified
        if idle_timeout is not None and idle_timeout != current_idle:
            idle_elem.text = str(idle_timeout)
            self.put_general_settings(gen_settings)
            changed = True
            final_idle = idle_timeout
        else:
            final_idle = current_idle

        # Apply link policy change if specified
        if link_policy is not None and link_policy != current_link_policy_str:
            # Modify LinkPolicy based on desired state
            # always_on adds 16, power_save removes 16
            new_policies = [p for p in current_link_policies if p != 16]
            if link_policy == 'always_on':
                new_policies.append(16)

            # Rebuild LinkPolicy element
            link_policy_elem.clear()
            for policy_val in new_policies:
                policy_child = etree.SubElement(link_policy_elem, f'{{{AMT_ETH_NS}}}PolicyValue')
                policy_child.text = str(policy_val)

            self.put_ethernet_port_settings(eth_settings)
            changed = True
            final_link_policy = link_policy
        else:
            final_link_policy = current_link_policy_str

        # Wake-on-LAN status inferred from link policy (16 = WoL capable)
        final_wol = 16 in (current_link_policies if link_policy is None else
                          ([p for p in current_link_policies if p != 16] + ([16] if link_policy == 'always_on' else [])))

        return {
            'wake_on_lan': final_wol,
            'idle_timeout': final_idle,
            'link_policy': final_link_policy,
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
        wake_on_lan=dict(type='bool', required=False),
        idle_timeout=dict(type='int', required=False),
        link_policy=dict(type='str', required=False, choices=['always_on', 'power_save']),
    )

    result = dict(
        changed=False,
        wake_on_lan=False,
        idle_timeout=0,
        link_policy='always_on',
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
            result['msg'] = 'Would configure power policy (check mode)'
            module.exit_json(**result)

        # Configure power policy
        policy_result = client.configure_power_policy(
            wake_on_lan=module.params.get('wake_on_lan'),
            idle_timeout=module.params.get('idle_timeout'),
            link_policy=module.params.get('link_policy')
        )

        result.update(policy_result)
        if result['changed']:
            result['msg'] = f"Power policy updated: idle_timeout={result['idle_timeout']}, link_policy={result['link_policy']}"
        else:
            result['msg'] = f"Power policy unchanged: idle_timeout={result['idle_timeout']}, link_policy={result['link_policy']}"

        module.exit_json(**result)

    except Exception as e:
        module.fail_json(msg=str(e), **result)


def main():
    run_module()


if __name__ == '__main__':
    main()
