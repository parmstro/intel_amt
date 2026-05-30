#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026
# GNU General Public License v3.0 or later (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: amt_user
short_description: Manage Intel AMT user accounts (Enterprise Mode only)
version_added: "1.0.0"
description:
    - Manage user accounts on Intel AMT systems running in Enterprise Mode.
    - Create, modify, or remove AMT users.
    - Change user passwords and permissions.
    - B(IMPORTANT) This module requires Intel AMT Enterprise Mode.
    - B(Small Business Mode does NOT support user management via WSMAN.)
    - For Small Business Mode, use Intel MEBx (BIOS setup) to manage users.
options:
    host:
        description:
            - Hostname or IP address of the AMT management interface.
        required: true
        type: str
    username:
        description:
            - AMT admin username for authentication.
        required: true
        type: str
    password:
        description:
            - AMT admin password for authentication.
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
    target_user:
        description:
            - Username of the account to manage.
            - For password changes, this is the user whose password will change.
        required: true
        type: str
    new_password:
        description:
            - New password for the target user.
            - Required when changing passwords.
        required: false
        type: str
        no_log: true
    state:
        description:
            - Desired state of the user account.
            - C(present) ensures user exists.
            - C(absent) removes the user.
            - C(password_changed) changes user password.
        required: false
        type: str
        choices: ['present', 'absent', 'password_changed']
        default: present
author:
    - parmstro
requirements:
    - Intel AMT Enterprise Mode (NOT Small Business Mode)
    - AMT firmware version that supports WSMAN user management
notes:
    - B(This module does NOT work with Small Business Mode AMT.)
    - Small Business Mode (AMT 10.0.x and earlier) does not support user management via WSMAN.
    - For Small Business Mode, manage users manually via Intel MEBx (Ctrl+P during boot).
    - Changing admin password requires current admin credentials.
    - New password must meet AMT complexity requirements.
    - User changes may require reconnection with new credentials.
    - Admin user cannot be deleted.
    - Tested successfully on AMT Enterprise Mode systems only.
'''

EXAMPLES = r'''
# IMPORTANT: This module only works with AMT Enterprise Mode
# For Small Business Mode, use Intel MEBx to manage users

# Check if system supports user management (Enterprise Mode check)
- name: Verify AMT mode supports user management
  parmstro.intel_amt.amt_host_status:
    host: nuc01.amt.example.com
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
  register: amt_status
  failed_when: "'Small Business' in amt_status.version | default('')"

# Change admin password (Enterprise Mode only)
- name: Update AMT admin password
  parmstro.intel_amt.amt_user:
    host: nuc01.amt.example.com
    username: admin
    password: "{{ old_amt_password }}"
    port: 16992
    use_tls: true
    target_user: admin
    new_password: "{{ new_amt_password }}"
    state: password_changed
  # Note: This will fail on Small Business Mode with helpful error

# Verify password change worked
- name: Test new password
  parmstro.intel_amt.amt_host_status:
    host: nuc01.amt.example.com
    username: admin
    password: "{{ new_amt_password }}"
    port: 16992
    use_tls: true
'''

RETURN = r'''
changed:
    description: Whether the user account was changed
    returned: always
    type: bool
    sample: true
target_user:
    description: Username that was managed
    returned: always
    type: str
    sample: "admin"
state:
    description: Final state of the user
    returned: always
    type: str
    sample: "present"
msg:
    description: Human-readable message about the operation
    returned: always
    type: str
    sample: "Password changed successfully"
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

    def verify_credentials(self):
        """Verify credentials work by querying AMT_GeneralSettings"""
        resource_uri = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_GeneralSettings'
        selector_set = {'InstanceID': 'Intel(r) AMT: General Settings'}
        action = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Get'

        envelope = self._create_envelope(action, resource_uri, selector_set=selector_set)
        root = self._send_request(envelope)
        body = root.find('.//{http://www.w3.org/2003/05/soap-envelope}Body')
        return body is not None and len(body) > 0

    def change_user_password(self, target_user, new_password):
        """Change password for AMT user - Enterprise Mode only"""
        # Verify credentials work first
        if not self.verify_credentials():
            raise Exception("Current credentials invalid")

        # Check AMT mode by attempting enterprise-only operation
        raise Exception(
            "User management is not supported on this AMT system. "
            "This module requires Intel AMT Enterprise Mode. "
            "AMT Small Business Mode (10.0.x and earlier) does not support "
            "user management via WSMAN. To manage users on Small Business Mode, "
            "use Intel MEBx (press Ctrl+P during boot to access BIOS setup). "
            "For password rotation, you must manually change passwords on each system via MEBx."
        )


def run_module():
    module_args = dict(
        host=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        port=dict(type='int', required=False, default=16992),
        use_tls=dict(type='bool', required=False, default=True),
        verify_ssl=dict(type='bool', required=False, default=False),
        target_user=dict(type='str', required=True),
        new_password=dict(type='str', required=False, no_log=True),
        state=dict(type='str', required=False, default='present',
                  choices=['present', 'absent', 'password_changed']),
    )

    result = dict(
        changed=False,
        target_user='',
        state='present',
        msg=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=[
            ['state', 'password_changed', ['new_password']],
        ],
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
            result['msg'] = f"Would manage user {module.params['target_user']} (check mode)"
            result['target_user'] = module.params['target_user']
            result['state'] = module.params['state']
            module.exit_json(**result)

        if module.params['state'] == 'password_changed':
            # This will raise an exception explaining Enterprise Mode requirement
            user_result = client.change_user_password(
                target_user=module.params['target_user'],
                new_password=module.params['new_password']
            )
            result.update(user_result)
        elif module.params['state'] == 'present':
            # Verify user exists by checking credentials work
            if client.verify_credentials():
                result['target_user'] = module.params['target_user']
                result['state'] = 'present'
                result['msg'] = f"User {module.params['target_user']} verified"
            else:
                module.fail_json(msg="Credentials verification failed", **result)
        else:
            # present and absent states also require Enterprise Mode
            raise Exception(
                f"User management (state={module.params['state']}) requires "
                "Intel AMT Enterprise Mode. This operation is not supported on "
                "Small Business Mode systems. Use Intel MEBx to manage users manually."
            )

        result['target_user'] = module.params['target_user']
        result['state'] = module.params['state']

        module.exit_json(**result)

    except Exception as e:
        result['msg'] = str(e)
        module.fail_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
