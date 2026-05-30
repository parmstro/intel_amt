#!/usr/bin/env python3
import sys
import requests
from requests.auth import HTTPDigestAuth
from lxml import etree
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_envelope(action, resource_uri, selector_set=None):
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

    body = etree.SubElement(envelope, f'{{{SOAP_NS}}}Body')
    return envelope

def probe_resource(base_url, username, password, resource_uri, selector_set=None):
    action = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Get'
    envelope = create_envelope(action, resource_uri, selector_set)
    xml_data = etree.tostring(envelope, encoding='utf-8', xml_declaration=True)

    headers = {'Content-Type': 'application/soap+xml;charset=UTF-8'}
    auth = HTTPDigestAuth(username, password)

    try:
        response = requests.post(base_url, data=xml_data, headers=headers,
                               auth=auth, verify=False, timeout=10)

        result = {
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'error': None,
            'data': None
        }

        if response.status_code == 200:
            # Parse response to extract useful data
            root = etree.fromstring(response.content)
            # Extract body content
            body = root.find('.//{http://www.w3.org/2003/05/soap-envelope}Body')
            if body is not None:
                # Get first child of body (the actual resource data)
                resource_data = list(body)[0] if len(body) > 0 else None
                if resource_data is not None:
                    result['data'] = etree.tostring(resource_data, encoding='unicode')
        else:
            result['error'] = f"HTTP {response.status_code}"

        return result

    except Exception as e:
        return {
            'status_code': 0,
            'success': False,
            'error': str(e),
            'data': None
        }

if __name__ == '__main__':
    # Args: base_url, username, password, resource_uri, [selector_name, selector_value]
    base_url = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    resource_uri = sys.argv[4]

    selector_set = None
    if len(sys.argv) > 6:
        selector_set = {sys.argv[5]: sys.argv[6]}

    result = probe_resource(base_url, username, password, resource_uri, selector_set)
    print(json.dumps(result))
