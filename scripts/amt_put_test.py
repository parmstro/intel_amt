#!/usr/bin/env python3
"""
Test WSMAN Put operation on AMT 10.0.56
This will modify AMT_GeneralSettings to test write capabilities
"""
import sys
import requests
from requests.auth import HTTPDigestAuth
from lxml import etree
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_envelope(action, resource_uri, body=None, selector_set=None):
    SOAP_NS = 'http://www.w3.org/2003/05/soap-envelope'
    WSA_NS = 'http://schemas.xmlsoap.org/ws/2004/08/addressing'
    WSMAN_NS = 'http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd'

    envelope = etree.Element(f'{{{SOAP_NS}}}Envelope',
        nsmap={'s': SOAP_NS, 'a': WSA_NS, 'w': WSMAN_NS})

    header = etree.SubElement(envelope, f'{{{SOAP_NS}}}Header')

    action_elem = etree.SubElement(header, f'{{{WSA_NS}}}Action',
        {f'{{{SOAP_NS}}}mustUnderstand': 'true'})
    action_elem.text = action

    to_elem = etree.SubElement(header, f'{{{WSA_NS}}}To',
        {f'{{{SOAP_NS}}}mustUnderstand': 'true'})
    to_elem.text = sys.argv[1]  # base_url

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

def get_resource(base_url, username, password, resource_uri, selector_set):
    """Get current resource"""
    action = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Get'
    envelope = create_envelope(action, resource_uri, selector_set=selector_set)
    xml_data = etree.tostring(envelope, encoding='utf-8', xml_declaration=True)

    headers = {'Content-Type': 'application/soap+xml;charset=UTF-8'}
    auth = HTTPDigestAuth(username, password)

    response = requests.post(base_url, data=xml_data, headers=headers,
                           auth=auth, verify=False, timeout=10)
    response.raise_for_status()

    root = etree.fromstring(response.content)
    body = root.find('.//{http://www.w3.org/2003/05/soap-envelope}Body')
    resource_data = list(body)[0] if len(body) > 0 else None

    return resource_data

def put_resource(base_url, username, password, resource_uri, selector_set, resource_body):
    """Put modified resource"""
    action = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Put'
    envelope = create_envelope(action, resource_uri, body=resource_body, selector_set=selector_set)
    xml_data = etree.tostring(envelope, encoding='utf-8', xml_declaration=True)

    headers = {'Content-Type': 'application/soap+xml;charset=UTF-8'}
    auth = HTTPDigestAuth(username, password)

    response = requests.post(base_url, data=xml_data, headers=headers,
                           auth=auth, verify=False, timeout=10)

    return {
        'status_code': response.status_code,
        'success': response.status_code == 200,
        'response': response.text
    }

def test_hostname_change(base_url, username, password, new_hostname):
    """Test changing hostname in AMT_GeneralSettings"""
    resource_uri = 'http://intel.com/wbem/wscim/1/amt-schema/1/AMT_GeneralSettings'
    selector_set = {'InstanceID': 'Intel(r) AMT: General Settings'}

    print("Step 1: Getting current settings...")
    current = get_resource(base_url, username, password, resource_uri, selector_set)

    # Extract current hostname
    current_hostname = current.find('.//{http://intel.com/wbem/wscim/1/amt-schema/1/AMT_GeneralSettings}HostName')
    old_hostname = current_hostname.text if current_hostname is not None else "Unknown"
    print(f"  Current hostname: {old_hostname}")

    # Modify hostname
    print(f"Step 2: Modifying hostname to: {new_hostname}")
    current_hostname.text = new_hostname

    # Put back
    print("Step 3: Writing modified settings back to AMT...")
    result = put_resource(base_url, username, password, resource_uri, selector_set, current)
    print(f"  Status: {result['status_code']}")
    print(f"  Success: {result['success']}")

    if result['success']:
        # Verify
        print("Step 4: Verifying change...")
        verify = get_resource(base_url, username, password, resource_uri, selector_set)
        verify_hostname = verify.find('.//{http://intel.com/wbem/wscim/1/amt-schema/1/AMT_GeneralSettings}HostName')
        new_name = verify_hostname.text if verify_hostname is not None else "Unknown"
        print(f"  Verified hostname: {new_name}")

        return {
            'success': True,
            'old_hostname': old_hostname,
            'new_hostname': new_name,
            'changed': old_hostname != new_name
        }
    else:
        return {
            'success': False,
            'error': result['response']
        }

if __name__ == '__main__':
    # Args: base_url, username, password, new_hostname
    if len(sys.argv) < 5:
        print("Usage: amt_put_test.py <base_url> <username> <password> <new_hostname>")
        sys.exit(1)

    base_url = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    new_hostname = sys.argv[4]

    try:
        result = test_hostname_change(base_url, username, password, new_hostname)
        print("\nResult:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
