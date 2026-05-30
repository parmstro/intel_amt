# amt_network_settings - Configure Intel AMT Network Settings

## Synopsis

- Configure network settings for Intel AMT management interface
- Supports both DHCP and static IP configuration
- Can configure IPv4 and IPv6 settings
- Allows enabling ping response for monitoring
- Network changes take effect immediately but may require reconnection

## Parameters

| Parameter | Choices/Defaults | Comments |
|-----------|------------------|----------|
| **host**<br/>string / required | | Hostname or IP address of the AMT management interface |
| **username**<br/>string / required | | AMT admin username |
| **password**<br/>string / required | | AMT admin password<br/>(no_log: true) |
| **port**<br/>integer | Default: 16992 | AMT management port |
| **use_tls**<br/>boolean | Default: true | Whether to use TLS for the connection |
| **verify_ssl**<br/>boolean | Default: false | Whether to verify SSL certificates |
| **dhcp_enabled**<br/>boolean | | Enable DHCP for automatic IPv4 configuration<br/>When true, static IPv4 settings are ignored |
| **ip_address**<br/>string | | Static IPv4 address for AMT interface<br/>Required when dhcp_enabled is false |
| **subnet_mask**<br/>string | | Subnet mask for static IPv4 configuration<br/>Required when dhcp_enabled is false |
| **gateway**<br/>string | | Default gateway for static IPv4 configuration<br/>Required when dhcp_enabled is false |
| **primary_dns**<br/>string | | Primary DNS server (IPv4) |
| **secondary_dns**<br/>string | | Secondary DNS server (IPv4) |
| **ping_response_enabled**<br/>boolean | | Enable AMT to respond to ICMP ping requests |
| **ipv6_enabled**<br/>boolean | | Enable IPv6 on the AMT interface |
| **ipv6_address**<br/>string | | Static IPv6 address<br/>Required when ipv6_enabled is true and ipv6_dhcp_enabled is false |
| **ipv6_prefix_length**<br/>integer | | IPv6 prefix length (e.g., 64 for /64)<br/>Required for static IPv6 |
| **ipv6_gateway**<br/>string | | IPv6 default gateway<br/>Required for static IPv6 |
| **ipv6_dhcp_enabled**<br/>boolean | | Enable DHCPv6 for automatic IPv6 configuration |
| **ipv6_dns_primary**<br/>string | | Primary IPv6 DNS server |
| **ipv6_dns_secondary**<br/>string | | Secondary IPv6 DNS server |

## Return Values

| Key | Type | Description | Sample |
|-----|------|-------------|--------|
| **changed** | boolean | Whether configuration was changed | true |
| **msg** | string | Human-readable status message | "Network settings updated successfully" |
| **previous_settings** | dict | Network settings before change | See examples |
| **new_settings** | dict | Network settings after change | See examples |

## Examples

### Enable DHCP

```yaml
- name: Configure AMT to use DHCP
  parmstro.intel_amt.amt_network_settings:
    host: 192.168.1.100
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    dhcp_enabled: true
```

### Configure Static IP

```yaml
- name: Set static IP address
  parmstro.intel_amt.amt_network_settings:
    host: 192.168.1.100
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    dhcp_enabled: false
    ip_address: 192.168.254.100
    subnet_mask: 255.255.255.0
    gateway: 192.168.254.1
    primary_dns: 192.168.254.1
    secondary_dns: 8.8.8.8
```

### Enable Ping Response

```yaml
- name: Enable ping for monitoring
  parmstro.intel_amt.amt_network_settings:
    host: nuc01.amt.example.com
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    ping_response_enabled: true
```

### Configure IPv6

```yaml
- name: Enable IPv6 with static address
  parmstro.intel_amt.amt_network_settings:
    host: 192.168.1.100
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    ipv6_enabled: true
    ipv6_dhcp_enabled: false
    ipv6_address: "2001:db8::100"
    ipv6_prefix_length: 64
    ipv6_gateway: "2001:db8::1"
    ipv6_dns_primary: "2001:db8::1"
```

## Use Cases

### Network Migration

```yaml
- name: Migrate AMT to new subnet
  block:
    - name: Get current network configuration
      parmstro.intel_amt.amt_host_status:
        host: "{{ old_amt_ip }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
      register: old_config

    - name: Configure new static IP
      parmstro.intel_amt.amt_network_settings:
        host: "{{ old_amt_ip }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
        dhcp_enabled: false
        ip_address: "{{ new_amt_ip }}"
        subnet_mask: "{{ new_subnet_mask }}"
        gateway: "{{ new_gateway }}"
        primary_dns: "{{ new_dns }}"

    - name: Wait for network reconfiguration
      ansible.builtin.pause:
        seconds: 10

    - name: Verify new configuration
      parmstro.intel_amt.amt_host_status:
        host: "{{ new_amt_ip }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
      register: new_config

    - name: Confirm migration successful
      ansible.builtin.assert:
        that:
          - new_config.ipv4_address == new_amt_ip
```

### DHCP to Static Conversion

```yaml
- name: Convert fleet from DHCP to static IPs
  block:
    - name: Get current DHCP addresses
      parmstro.intel_amt.amt_host_status:
        host: "{{ item.hostname }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
      loop: "{{ nuc_fleet }}"
      register: dhcp_addresses

    - name: Configure static IP for each system
      parmstro.intel_amt.amt_network_settings:
        host: "{{ item.ipv4_address }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
        dhcp_enabled: false
        ip_address: "{{ item.ipv4_address }}"
        subnet_mask: 255.255.255.0
        gateway: "{{ amt_gateway }}"
        primary_dns: "{{ amt_dns_primary }}"
        secondary_dns: "{{ amt_dns_secondary }}"
      loop: "{{ dhcp_addresses.results }}"
```

### Standardize Fleet Configuration

```yaml
- name: Standardize AMT network settings across fleet
  parmstro.intel_amt.amt_network_settings:
    host: "{{ item }}"
    username: "{{ amt_username }}"
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    dhcp_enabled: true
    ping_response_enabled: true
  loop: "{{ amt_hosts }}"
  async: 60
  poll: 0
  register: config_jobs

- name: Wait for configuration completion
  ansible.builtin.async_status:
    jid: "{{ item.ansible_job_id }}"
  loop: "{{ config_jobs.results }}"
  register: job_result
  until: job_result.finished
  retries: 10
```

### Enable Monitoring Across Fleet

```yaml
- name: Enable ping response for monitoring
  parmstro.intel_amt.amt_network_settings:
    host: "{{ item }}"
    username: "{{ amt_username }}"
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    ping_response_enabled: true
  loop: "{{ amt_hosts }}"

- name: Verify all systems respond to ping
  ansible.builtin.command:
    cmd: "ping -c 1 {{ item }}"
  loop: "{{ amt_hosts }}"
  register: ping_results
  failed_when: ping_results.rc != 0
```

### Disaster Recovery Network Reconfiguration

```yaml
- name: Emergency network reconfiguration
  block:
    - name: Configure temporary DHCP
      parmstro.intel_amt.amt_network_settings:
        host: "{{ item }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
        dhcp_enabled: true
      loop: "{{ affected_systems }}"

    - name: Wait for DHCP assignment
      ansible.builtin.pause:
        seconds: 30

    - name: Collect new IP addresses
      parmstro.intel_amt.amt_host_status:
        host: "{{ item }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
      loop: "{{ affected_systems }}"
      register: recovery_status

    - name: Update inventory with new addresses
      ansible.builtin.lineinfile:
        path: /etc/hosts
        regexp: "^.*{{ item.hostname }}$"
        line: "{{ item.ipv4_address }} {{ item.hostname }}"
      loop: "{{ recovery_status.results }}"
```

## Notes

- **IMPORTANT**: After changing the IP address, you must reconnect using the new address
- Network configuration changes take effect immediately
- When enabling DHCP, allow time for DHCP lease acquisition
- Static IP configuration requires ip_address, subnet_mask, and gateway
- IPv4 and IPv6 can be configured independently
- Ping response is disabled by default on AMT for security
- DNS settings are optional but recommended for proper operation
- The module is idempotent - applying the same configuration twice does not cause changes

## Network Change Workflow

1. **Plan**: Document current and target network configurations
2. **Backup**: Record current settings using `amt_host_status`
3. **Configure**: Apply new settings with this module
4. **Wait**: Allow time for network reconfiguration (5-10 seconds)
5. **Verify**: Check new configuration with `amt_host_status`
6. **Update**: Update inventory/DNS with new addresses if changed

## Protocol Details

This module uses WS-Management (WSMAN) to configure network settings:
- CIM resource URI: `http://intel.com/wbem/wscim/1/amt-schema/1/AMT_EthernetPortSettings`
- Method: `Put` with modified settings
- Authentication: HTTP Digest Authentication

## See Also

- [amt_host_status](amt_host_status.md) - Retrieve current network configuration
- [amt_event_log](amt_event_log.md) - Check for network-related events
