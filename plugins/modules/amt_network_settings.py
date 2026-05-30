#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026
# GNU General Public License v3.0 or later (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: amt_network_settings
short_description: Configure Intel AMT network settings
version_added: "1.0.0"
description:
    - Configure network settings for Intel AMT interface.
    - Supports static IP or DHCP configuration.
    - Can configure IP address, subnet mask, gateway, and DNS servers.
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
    dhcp_enabled:
        description:
            - Enable DHCP for automatic IP configuration.
            - When true, static IP settings are ignored.
        required: false
        type: bool
    ip_address:
        description:
            - Static IP address for AMT interface.
            - Required when dhcp_enabled is false.
        required: false
        type: str
    subnet_mask:
        description:
            - Subnet mask for static IP configuration.
            - Required when dhcp_enabled is false.
        required: false
        type: str
    gateway:
        description:
            - Default gateway for static IP configuration.
            - Required when dhcp_enabled is false.
        required: false
        type: str
    primary_dns:
        description:
            - Primary DNS server.
        required: false
        type: str
    secondary_dns:
        description:
            - Secondary DNS server.
        required: false
        type: str
    ping_response_enabled:
        description:
            - Enable AMT to respond to ICMP ping requests.
            - Useful for network monitoring and availability checks.
        required: false
        type: bool
    ipv6_enabled:
        description:
            - Enable IPv6 on the AMT interface.
        required: false
        type: bool
    ipv6_address:
        description:
            - Static IPv6 address for AMT interface.
            - Required when ipv6_enabled is true and ipv6_dhcp_enabled is false.
        required: false
        type: str
    ipv6_prefix_length:
        description:
            - IPv6 prefix length (e.g., 64 for /64 network).
            - Required when ipv6_enabled is true and ipv6_dhcp_enabled is false.
        required: false
        type: int
    ipv6_gateway:
        description:
            - IPv6 default gateway.
            - Required when ipv6_enabled is true and ipv6_dhcp_enabled is false.
        required: false
        type: str
    ipv6_dhcp_enabled:
        description:
            - Enable DHCPv6 for automatic IPv6 configuration.
            - When true, static IPv6 settings are ignored.
        required: false
        type: bool
    ipv6_dns_primary:
        description:
            - Primary IPv6 DNS server.
        required: false
        type: str
    ipv6_dns_secondary:
        description:
            - Secondary IPv6 DNS server.
        required: false
        type: str
author:
    - parmstro
notes:
    - Network configuration changes require AMT firmware to apply them.
    - After changing IP address, reconnect using the new address.
    - DHCP mode will override any static IP settings.
'''

EXAMPLES = r'''
# Enable DHCP
- name: Configure AMT to use DHCP
  parmstro.intel_amt.amt_network_settings:
    host: 192.168.1.100
    username: admin
    password: "{{ amt_password }}"
    use_tls: false
    dhcp_enabled: true

# Set static IP
- name: Configure AMT with static IP
  parmstro.intel_amt.amt_network_settings:
    host: nuc01.amt.example.com
    username: admin
    password: "{{ amt_password }}"
    use_tls: false
    dhcp_enabled: false
    ip_address: 192.168.254.100
    subnet_mask: 255.255.255.0
    gateway: 192.168.254.1
    primary_dns: 8.8.8.8
    secondary_dns: 8.8.4.4

# Update DNS servers only (keep existing IP)
- name: Update DNS servers
  parmstro.intel_amt.amt_network_settings:
    host: 192.168.254.100
    username: admin
    password: "{{ amt_password }}"
    use_tls: false
    primary_dns: 192.168.1.1
    secondary_dns: 192.168.1.2

# Enable ping response for monitoring
- name: Enable AMT ping response
  parmstro.intel_amt.amt_network_settings:
    host: 192.168.254.100
    username: admin
    password: "{{ amt_password }}"
    use_tls: false
    ping_response_enabled: true

# Configure IPv6 with DHCPv6
- name: Enable IPv6 with DHCPv6
  parmstro.intel_amt.amt_network_settings:
    host: 192.168.254.100
    username: admin
    password: "{{ amt_password }}"
    use_tls: false
    ipv6_enabled: true
    ipv6_dhcp_enabled: true

# Configure IPv6 with static address
- name: Configure static IPv6
  parmstro.intel_amt.amt_network_settings:
    host: 192.168.254.100
    username: admin
    password: "{{ amt_password }}"
    use_tls: false
    ipv6_enabled: true
    ipv6_dhcp_enabled: false
    ipv6_address: "2001:db8::100"
    ipv6_prefix_length: 64
    ipv6_gateway: "2001:db8::1"
    ipv6_dns_primary: "2001:4860:4860::8888"
    ipv6_dns_secondary: "2001:4860:4860::8844"

# Disable IPv6
- name: Disable IPv6 on AMT
  parmstro.intel_amt.amt_network_settings:
    host: 192.168.254.100
    username: admin
    password: "{{ amt_password }}"
    use_tls: false
    ipv6_enabled: false
'''

RETURN = r'''
changed:
    description: Whether configuration was changed
    returned: always
    type: bool
    sample: true
previous_config:
    description: Previous network configuration
    returned: always
    type: dict
    contains:
        dhcp_enabled:
            description: Previous DHCP status
            type: bool
        ip_address:
            description: Previous IP address
            type: str
        subnet_mask:
            description: Previous subnet mask
            type: str
        gateway:
            description: Previous gateway
            type: str
new_config:
    description: New network configuration
    returned: when changed
    type: dict
    contains:
        dhcp_enabled:
            description: New DHCP status
            type: bool
        ip_address:
            description: New IP address
            type: str
        subnet_mask:
            description: New subnet mask
            type: str
        gateway:
            description: New gateway
            type: str
msg:
    description: Status message
    returned: always
    type: str
    sample: "Network settings updated successfully"
'''

import traceback
from ansible.module_utils.basic import AnsibleModule

try:
    import requests
    from requests.auth import HTTPDigestAuth
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False


class WSMANClient:
    """WS-Management client for Intel AMT network configuration"""

    def __init__(self, host, username, password, port=16992, use_tls=True, verify_ssl=False):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.use_tls = use_tls
        self.verify_ssl = verify_ssl
        self.base_url = f"{'https' if use_tls else 'http'}://{host}:{port}/wsman"
        self.auth = HTTPDigestAuth(username, password)

    def _create_envelope(self, action, resource_uri, selector_set=None, body_content=None):
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
        if body_content is not None:
            body_elem.append(body_content)

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

    def get_ethernet_settings(self):
        """Get current AMT ethernet settings"""
        resource_uri = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_EthernetPortSettings'
        action = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Get'
        selector_set = {'InstanceID': 'Intel(r) AMT Ethernet Port Settings 0'}

        envelope = self._create_envelope(action, resource_uri, selector_set)
        return self._send_request(envelope)

    def put_ethernet_settings(self, settings_element):
        """Update AMT ethernet settings"""
        resource_uri = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_EthernetPortSettings'
        action = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Put'
        selector_set = {'InstanceID': 'Intel(r) AMT Ethernet Port Settings 0'}

        envelope = self._create_envelope(action, resource_uri, selector_set, settings_element)
        return self._send_request(envelope)


def parse_ethernet_settings(root):
    """Parse ethernet settings from XML response"""
    settings = {}

    for elem in root.iter():
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

        # IPv4 settings
        if tag == 'DHCPEnabled':
            settings['dhcp_enabled'] = elem.text.lower() == 'true'
        elif tag == 'IPAddress':
            settings['ip_address'] = elem.text
        elif tag == 'SubnetMask':
            settings['subnet_mask'] = elem.text
        elif tag == 'DefaultGateway':
            settings['gateway'] = elem.text
        elif tag == 'PrimaryDNS':
            settings['primary_dns'] = elem.text
        elif tag == 'SecondaryDNS':
            settings['secondary_dns'] = elem.text
        elif tag == 'IpSyncEnabled':
            settings['ping_response_enabled'] = elem.text.lower() == 'true'

        # IPv6 settings
        elif tag == 'IPv6Enable':
            settings['ipv6_enabled'] = elem.text.lower() == 'true'
        elif tag == 'IPv6Address':
            settings['ipv6_address'] = elem.text
        elif tag == 'IPv6PrefixLength':
            try:
                settings['ipv6_prefix_length'] = int(elem.text) if elem.text else None
            except (ValueError, TypeError):
                pass
        elif tag == 'IPv6DefaultGateway':
            settings['ipv6_gateway'] = elem.text
        elif tag == 'IPv6DHCPEnabled':
            settings['ipv6_dhcp_enabled'] = elem.text.lower() == 'true'
        elif tag == 'IPv6PrimaryDNS':
            settings['ipv6_dns_primary'] = elem.text
        elif tag == 'IPv6SecondaryDNS':
            settings['ipv6_dns_secondary'] = elem.text

    return settings


def create_settings_element(current_root, params):
    """Create updated settings element from current settings and params"""
    AMT_NS = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_EthernetPortSettings'

    # Find the current settings element
    for elem in current_root.iter():
        if elem.tag.endswith('AMT_EthernetPortSettings'):
            # Clone the element
            new_elem = etree.Element(elem.tag, nsmap=elem.nsmap)

            # Copy all child elements, updating as needed
            for child in elem:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                new_child = etree.SubElement(new_elem, child.tag)

                # Update values based on params
                if tag == 'DHCPEnabled' and params.get('dhcp_enabled') is not None:
                    new_child.text = 'true' if params['dhcp_enabled'] else 'false'
                elif tag == 'IPAddress' and params.get('ip_address'):
                    new_child.text = params['ip_address']
                elif tag == 'SubnetMask' and params.get('subnet_mask'):
                    new_child.text = params['subnet_mask']
                elif tag == 'DefaultGateway' and params.get('gateway'):
                    new_child.text = params['gateway']
                elif tag == 'PrimaryDNS' and params.get('primary_dns'):
                    new_child.text = params['primary_dns']
                elif tag == 'SecondaryDNS' and params.get('secondary_dns'):
                    new_child.text = params['secondary_dns']
                elif tag == 'IpSyncEnabled' and params.get('ping_response_enabled') is not None:
                    new_child.text = 'true' if params['ping_response_enabled'] else 'false'

                # IPv6 settings
                elif tag == 'IPv6Enable' and params.get('ipv6_enabled') is not None:
                    new_child.text = 'true' if params['ipv6_enabled'] else 'false'
                elif tag == 'IPv6Address' and params.get('ipv6_address'):
                    new_child.text = params['ipv6_address']
                elif tag == 'IPv6PrefixLength' and params.get('ipv6_prefix_length') is not None:
                    new_child.text = str(params['ipv6_prefix_length'])
                elif tag == 'IPv6DefaultGateway' and params.get('ipv6_gateway'):
                    new_child.text = params['ipv6_gateway']
                elif tag == 'IPv6DHCPEnabled' and params.get('ipv6_dhcp_enabled') is not None:
                    new_child.text = 'true' if params['ipv6_dhcp_enabled'] else 'false'
                elif tag == 'IPv6PrimaryDNS' and params.get('ipv6_dns_primary'):
                    new_child.text = params['ipv6_dns_primary']
                elif tag == 'IPv6SecondaryDNS' and params.get('ipv6_dns_secondary'):
                    new_child.text = params['ipv6_dns_secondary']
                else:
                    # Keep existing value
                    new_child.text = child.text
                    # Copy attributes
                    for attr, val in child.attrib.items():
                        new_child.set(attr, val)

            return new_elem

    raise Exception("Could not find AMT_EthernetPortSettings in response")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(type='str', required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            port=dict(type='int', default=16992),
            use_tls=dict(type='bool', default=True),
            verify_ssl=dict(type='bool', default=False),
            dhcp_enabled=dict(type='bool', required=False),
            ip_address=dict(type='str', required=False),
            subnet_mask=dict(type='str', required=False),
            gateway=dict(type='str', required=False),
            primary_dns=dict(type='str', required=False),
            secondary_dns=dict(type='str', required=False),
            ping_response_enabled=dict(type='bool', required=False),
            ipv6_enabled=dict(type='bool', required=False),
            ipv6_address=dict(type='str', required=False),
            ipv6_prefix_length=dict(type='int', required=False),
            ipv6_gateway=dict(type='str', required=False),
            ipv6_dhcp_enabled=dict(type='bool', required=False),
            ipv6_dns_primary=dict(type='str', required=False),
            ipv6_dns_secondary=dict(type='str', required=False),
        ),
        required_if=[
            ('dhcp_enabled', False, ['ip_address', 'subnet_mask', 'gateway']),
            ('ipv6_enabled', True, ['ipv6_dhcp_enabled']),
        ],
        required_together=[
            ['ipv6_address', 'ipv6_prefix_length', 'ipv6_gateway'],
        ],
        supports_check_mode=True,
    )

    if not HAS_REQUESTS:
        module.fail_json(msg='requests library is required for this module')

    if not HAS_LXML:
        module.fail_json(msg='lxml library is required for this module')

    # Create client
    client = WSMANClient(
        module.params['host'],
        module.params['username'],
        module.params['password'],
        module.params['port'],
        module.params['use_tls'],
        module.params['verify_ssl']
    )

    try:
        # Get current settings
        current_response = client.get_ethernet_settings()
        current_settings = parse_ethernet_settings(current_response)

        # Determine what needs to change
        changes = {}
        if module.params['dhcp_enabled'] is not None:
            changes['dhcp_enabled'] = module.params['dhcp_enabled']
        if module.params['ip_address']:
            changes['ip_address'] = module.params['ip_address']
        if module.params['subnet_mask']:
            changes['subnet_mask'] = module.params['subnet_mask']
        if module.params['gateway']:
            changes['gateway'] = module.params['gateway']
        if module.params['primary_dns']:
            changes['primary_dns'] = module.params['primary_dns']
        if module.params['secondary_dns']:
            changes['secondary_dns'] = module.params['secondary_dns']
        if module.params['ping_response_enabled'] is not None:
            changes['ping_response_enabled'] = module.params['ping_response_enabled']

        # IPv6 settings
        if module.params['ipv6_enabled'] is not None:
            changes['ipv6_enabled'] = module.params['ipv6_enabled']
        if module.params['ipv6_address']:
            changes['ipv6_address'] = module.params['ipv6_address']
        if module.params['ipv6_prefix_length'] is not None:
            changes['ipv6_prefix_length'] = module.params['ipv6_prefix_length']
        if module.params['ipv6_gateway']:
            changes['ipv6_gateway'] = module.params['ipv6_gateway']
        if module.params['ipv6_dhcp_enabled'] is not None:
            changes['ipv6_dhcp_enabled'] = module.params['ipv6_dhcp_enabled']
        if module.params['ipv6_dns_primary']:
            changes['ipv6_dns_primary'] = module.params['ipv6_dns_primary']
        if module.params['ipv6_dns_secondary']:
            changes['ipv6_dns_secondary'] = module.params['ipv6_dns_secondary']

        # Check if changes are needed
        needs_change = False
        for key, new_value in changes.items():
            if current_settings.get(key) != new_value:
                needs_change = True
                break

        if not needs_change:
            module.exit_json(
                changed=False,
                msg='Network settings already match desired state',
                previous_config=current_settings
            )

        # Apply changes
        if module.check_mode:
            module.exit_json(
                changed=True,
                msg='Would update network settings (check mode)',
                previous_config=current_settings,
                new_config={**current_settings, **changes}
            )

        # Create updated settings element
        updated_element = create_settings_element(current_response, changes)

        # Send PUT request
        client.put_ethernet_settings(updated_element)

        # Verify changes
        verify_response = client.get_ethernet_settings()
        new_settings = parse_ethernet_settings(verify_response)

        module.exit_json(
            changed=True,
            msg='Network settings updated successfully',
            previous_config=current_settings,
            new_config=new_settings
        )

    except Exception as e:
        module.fail_json(msg=f"Failed to configure network settings: {str(e)}")


if __name__ == '__main__':
    main()
