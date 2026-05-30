# amt_host_status - Retrieve System Status from Intel AMT

## Synopsis

- Retrieve comprehensive system status information from Intel AMT
- Returns power state, firmware version, BIOS version, and network configuration
- Useful for inventory collection and health monitoring
- Read-only operation with no side effects

## Parameters

| Parameter | Choices/Defaults | Comments |
|-----------|------------------|----------|
| **host**<br/>string / required | | Hostname or IP address of the AMT management interface |
| **username**<br/>string / required | | AMT admin username |
| **password**<br/>string / required | | AMT admin password<br/>(no_log: true) |
| **port**<br/>integer | Default: 16992 | AMT management port |
| **use_tls**<br/>boolean | Default: true | Whether to use TLS for the connection |
| **verify_ssl**<br/>boolean | Default: false | Whether to verify SSL certificates |

## Return Values

| Key | Type | Description | Sample |
|-----|------|-------------|--------|
| **power_state** | string | Current power state of the system | "on" |
| **amt_version** | string | Intel AMT firmware version | "10.0.56" |
| **bios_version** | string | System BIOS version | "MYBDWi5v.86A.0059.2022.0706.2207" |
| **hostname** | string | AMT hostname | "c1s2n2.amt.example.com" |
| **ipv4_address** | string | IPv4 address of AMT interface | "192.168.254.209" |
| **mac_address** | string | MAC address of AMT interface | "94-c6-91-a3-19-41" |
| **dhcp_enabled** | boolean | Whether DHCP is enabled | true |
| **changed** | boolean | Always false (read-only operation) | false |

## Examples

### Basic Status Query

```yaml
- name: Get system status
  parmstro.intel_amt.amt_host_status:
    host: nuc01.amt.example.com
    username: admin
    password: "{{ amt_password }}"
  register: status

- name: Display status
  ansible.builtin.debug:
    var: status
```

### Check Power State Before Operations

```yaml
- name: Retrieve current status
  parmstro.intel_amt.amt_host_status:
    host: "{{ amt_host }}"
    username: "{{ amt_username }}"
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
  register: current_status

- name: Power on only if currently off
  parmstro.intel_amt.amt_power:
    host: "{{ amt_host }}"
    username: "{{ amt_username }}"
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    state: on
  when: current_status.power_state == "off"
```

### Inventory Collection

```yaml
- name: Collect AMT inventory for fleet
  parmstro.intel_amt.amt_host_status:
    host: "{{ item }}"
    username: "{{ amt_username }}"
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
  loop: "{{ amt_hosts }}"
  register: fleet_inventory

- name: Generate inventory report
  ansible.builtin.template:
    src: inventory_report.j2
    dest: "/tmp/amt_inventory_{{ ansible_date_time.date }}.txt"
  vars:
    inventory: "{{ fleet_inventory.results }}"
```

### Health Check

```yaml
- name: Check AMT health
  block:
    - name: Get system status
      parmstro.intel_amt.amt_host_status:
        host: "{{ amt_host }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
      register: health

    - name: Verify AMT version
      ansible.builtin.assert:
        that:
          - health.amt_version is version('10.0.0', '>=')
        fail_msg: "AMT firmware version too old: {{ health.amt_version }}"
        success_msg: "AMT firmware version OK: {{ health.amt_version }}"

    - name: Verify system is accessible
      ansible.builtin.assert:
        that:
          - health.power_state is defined
        fail_msg: "Unable to retrieve power state"
        success_msg: "System accessible and responsive"
```

### Network Configuration Verification

```yaml
- name: Check AMT network settings
  parmstro.intel_amt.amt_host_status:
    host: "{{ amt_host }}"
    username: "{{ amt_username }}"
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
  register: net_status

- name: Display network configuration
  ansible.builtin.debug:
    msg:
      - "IP Address: {{ net_status.ipv4_address }}"
      - "MAC Address: {{ net_status.mac_address }}"
      - "DHCP: {{ 'Enabled' if net_status.dhcp_enabled else 'Disabled' }}"
```

## Use Cases

### Pre-Provisioning Validation

```yaml
- name: Validate system before provisioning
  block:
    - name: Get current status
      parmstro.intel_amt.amt_host_status:
        host: "{{ amt_host }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
      register: pre_check

    - name: Verify system requirements
      ansible.builtin.assert:
        that:
          - pre_check.amt_version is version('10.0.0', '>=')
          - pre_check.ipv4_address is defined
          - pre_check.mac_address is defined
        fail_msg: "System does not meet requirements"

    - name: Proceed with provisioning
      ansible.builtin.debug:
        msg: "System validated, proceeding with deployment"
```

### Monitoring Dashboard Data Collection

```yaml
- name: Collect metrics for monitoring
  parmstro.intel_amt.amt_host_status:
    host: "{{ item.hostname }}"
    username: "{{ amt_username }}"
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
  loop: "{{ nuc_fleet }}"
  register: metrics
  async: 60
  poll: 0

- name: Wait for collection
  ansible.builtin.async_status:
    jid: "{{ item.ansible_job_id }}"
  loop: "{{ metrics.results }}"
  register: collected_metrics
  until: collected_metrics.finished
  retries: 10

- name: Export to monitoring system
  ansible.builtin.uri:
    url: "https://monitoring.example.com/api/metrics"
    method: POST
    body_format: json
    body:
      timestamp: "{{ ansible_date_time.iso8601 }}"
      metrics: "{{ collected_metrics.results }}"
```

## Notes

- This is a read-only operation and never returns `changed: true`
- All information is retrieved via WS-Management protocol
- Network information reflects the AMT management interface, not the OS network configuration
- The module does not verify that the operating system is running, only that AMT firmware is accessible
- Response time is typically under 1 second on local networks

## Protocol Details

This module uses WS-Management (WSMAN) to query Intel AMT firmware:
- Multiple CIM resource URIs for comprehensive status:
  - `CIM_AssociatedPowerManagementService` - Power state
  - `CIM_SoftwareIdentity` - Firmware/BIOS versions
  - `AMT_EthernetPortSettings` - Network configuration
- Authentication: HTTP Digest Authentication

## See Also

- [amt_power](amt_power.md) - For power state management
- [amt_event_log](amt_event_log.md) - For system event history
- [amt_network_settings](amt_network_settings.md) - For network configuration changes
