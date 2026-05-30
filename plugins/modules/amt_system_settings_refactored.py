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

# Import shared utilities
try:
    from ansible_collections.parmstro.intel_amt.plugins.module_utils.wsman import WSMANClient
    from ansible_collections.parmstro.intel_amt.plugins.module_utils.amt_constants import (
        AMT_GENERAL_SETTINGS,
        SELECTOR_GENERAL_SETTINGS,
        COMMON_ARG_SPEC
    )
    HAS_MODULE_UTILS = True
except ImportError:
    HAS_MODULE_UTILS = False


def configure_system_settings(client, system_name=None, domain_name=None):
    """Configure system name and domain settings via WSMAN"""
    AMT_NS = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_GeneralSettings'

    # Get current settings
    current = client.get(AMT_GENERAL_SETTINGS, SELECTOR_GENERAL_SETTINGS)

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
        client.put(AMT_GENERAL_SETTINGS, current, SELECTOR_GENERAL_SETTINGS)
        # Verify by reading back
        verify = client.get(AMT_GENERAL_SETTINGS, SELECTOR_GENERAL_SETTINGS)
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
    # Combine common args with module-specific args
    module_args = COMMON_ARG_SPEC.copy()
    module_args.update({
        'system_name': {'type': 'str', 'required': False},
        'domain_name': {'type': 'str', 'required': False},
    })

    result = {
        'changed': False,
        'system_name': '',
        'domain_name': '',
        'fqdn': '',
        'msg': ''
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if not HAS_MODULE_UTILS:
        module.fail_json(msg='Required module_utils not found', **result)

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

        settings_result = configure_system_settings(
            client,
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
        result["msg"] = str(e)
    module.fail_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
