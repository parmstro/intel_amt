#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2026
# GNU General Public License v3.0 or later (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
WS-Management client for Intel AMT
Shared utility for all AMT modules
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import requests
from requests.auth import HTTPDigestAuth
from lxml import etree
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class WSMANClient:
    """
    WS-Management client for Intel AMT

    Provides common SOAP/WSMAN functionality for all Intel AMT modules.
    Handles authentication, envelope creation, and request/response processing.
    """

    SOAP_NS = 'http://www.w3.org/2003/05/soap-envelope'
    WSA_NS = 'http://schemas.xmlsoap.org/ws/2004/08/addressing'
    WSMAN_NS = 'http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd'

    def __init__(self, host, username, password, port=16992, use_tls=True, verify_ssl=False):
        """
        Initialize WSMAN client

        Args:
            host: AMT hostname or IP address
            username: AMT admin username
            password: AMT admin password
            port: AMT management port (default 16992)
            use_tls: Use HTTPS if True, HTTP if False (default True)
            verify_ssl: Verify SSL certificates (default False)
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.use_tls = use_tls
        self.verify_ssl = verify_ssl
        self.base_url = f"{'https' if use_tls else 'http'}://{host}:{port}/wsman"
        self.auth = HTTPDigestAuth(username, password)

    def _create_envelope(self, action, resource_uri, body=None, selector_set=None):
        """
        Create SOAP envelope for WSMAN request

        Args:
            action: WSMAN action URI (Get, Put, Enumerate, etc.)
            resource_uri: CIM/AMT resource URI
            body: Optional XML body element
            selector_set: Optional dict of selectors {name: value}

        Returns:
            lxml.etree.Element: SOAP envelope
        """
        envelope = etree.Element(
            f'{{{self.SOAP_NS}}}Envelope',
            nsmap={'s': self.SOAP_NS, 'a': self.WSA_NS, 'w': self.WSMAN_NS}
        )

        header = etree.SubElement(envelope, f'{{{self.SOAP_NS}}}Header')

        # Action
        action_elem = etree.SubElement(
            header,
            f'{{{self.WSA_NS}}}Action',
            {f'{{{self.SOAP_NS}}}mustUnderstand': 'true'}
        )
        action_elem.text = action

        # To (destination URL)
        to_elem = etree.SubElement(
            header,
            f'{{{self.WSA_NS}}}To',
            {f'{{{self.SOAP_NS}}}mustUnderstand': 'true'}
        )
        to_elem.text = self.base_url

        # ResourceURI
        resource_elem = etree.SubElement(
            header,
            f'{{{self.WSMAN_NS}}}ResourceURI',
            {f'{{{self.SOAP_NS}}}mustUnderstand': 'true'}
        )
        resource_elem.text = resource_uri

        # MessageID
        msg_id = etree.SubElement(
            header,
            f'{{{self.WSA_NS}}}MessageID',
            {f'{{{self.SOAP_NS}}}mustUnderstand': 'true'}
        )
        msg_id.text = 'uuid:00000000-8086-8086-8086-000000000001'

        # ReplyTo
        reply_to = etree.SubElement(header, f'{{{self.WSA_NS}}}ReplyTo')
        address = etree.SubElement(reply_to, f'{{{self.WSA_NS}}}Address')
        address.text = 'http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous'

        # SelectorSet (if provided)
        if selector_set:
            sel_set = etree.SubElement(header, f'{{{self.WSMAN_NS}}}SelectorSet')
            for name, value in selector_set.items():
                selector = etree.SubElement(
                    sel_set,
                    f'{{{self.WSMAN_NS}}}Selector',
                    Name=name
                )
                selector.text = value

        # Body
        body_elem = etree.SubElement(envelope, f'{{{self.SOAP_NS}}}Body')
        if body is not None:
            body_elem.append(body)

        return envelope

    def _send_request(self, envelope):
        """
        Send WSMAN request and return parsed response

        Args:
            envelope: SOAP envelope (lxml.etree.Element)

        Returns:
            lxml.etree.Element: Parsed response root

        Raises:
            Exception: On request failure
        """
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

    def get(self, resource_uri, selector_set=None):
        """
        WSMAN Get operation

        Args:
            resource_uri: CIM/AMT resource URI
            selector_set: Optional dict of selectors

        Returns:
            lxml.etree.Element: Resource element from response body
        """
        action = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Get'
        envelope = self._create_envelope(action, resource_uri, selector_set=selector_set)
        root = self._send_request(envelope)

        body = root.find(f'.//{{{self.SOAP_NS}}}Body')
        if body is None or len(body) == 0:
            raise Exception("No data in WSMAN response body")

        return list(body)[0]

    def put(self, resource_uri, resource_body, selector_set=None):
        """
        WSMAN Put operation

        Args:
            resource_uri: CIM/AMT resource URI
            resource_body: Modified resource element
            selector_set: Optional dict of selectors
        """
        action = 'http://schemas.xmlsoap.org/ws/2004/09/transfer/Put'
        envelope = self._create_envelope(action, resource_uri, body=resource_body, selector_set=selector_set)
        self._send_request(envelope)

    def enumerate(self, resource_uri):
        """
        WSMAN Enumerate operation

        Args:
            resource_uri: CIM/AMT resource URI

        Returns:
            lxml.etree.Element: Response root
        """
        action = 'http://schemas.xmlsoap.org/ws/2004/09/enumeration/Enumerate'
        envelope = self._create_envelope(action, resource_uri)
        return self._send_request(envelope)
