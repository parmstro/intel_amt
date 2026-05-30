# parmstro.intel_amt Collection Status

Version: 1.0.0  
License: GPL-3.0-or-later  
Tested on: Intel NUC5i5MYBE with AMT 10.0.56 build 3002

## Working Modules (5)

All modules tested and verified on real hardware (c1s2n2, c1s2n3, c1s2n4.amt.parmstrong.ca).

### 1. amt_power
**Power Management** - Control system power state
- States: on, off, reboot, cycle, query
- Check mode support
- Verified: Successfully triggers PXE boot → Satellite discovery

### 2. amt_host_status  
**System Status Information** - Read-only system information
- Power state
- IPv4/IPv6 addresses
- MAC address
- BIOS version
- AMT time
- System ID

### 3. amt_event_log
**Event Log Retrieval** - Read AMT event logs
- Enumerate all events or limit with max_records
- Parse event timestamps and descriptions
- Useful for boot verification

### 4. amt_log_clear
**Log Management** - Clear AMT logs
- Clear message log, provisioning log, or all logs
- Check mode support
- Returns record count before clearing

### 5. amt_network_settings
**Network Configuration** - Configure AMT network settings
- DHCP or static IP configuration
- Set IP address, subnet mask, gateway
- Configure DNS servers (primary/secondary)
- Check mode support
- Returns previous and new configuration

## Fleet Capabilities

✅ **Multi-Host Operations** - Tested across 3 NUCs simultaneously  
✅ **Parallel Execution** - Ansible loop-based fleet management  
✅ **Status Aggregation** - Collect and summarize fleet state  

## Security

✅ **Credential Management**
- Ansible Vault directory pattern
- Environment variable support for CI/CD
- All passwords marked with `no_log: true`
- Special character password support tested (credentials in vault)

✅ **Code Quality**
- ansible-lint production profile: PASS
- Fully Qualified Collection Names (FQCN) throughout
- Comprehensive documentation
- Python syntax validated

## Use Cases

### 1. Bare Metal Provisioning
```yaml
- name: Reboot for PXE boot to Satellite
  parmstro.intel_amt.amt_power:
    host: "{{ amt_host }}"
    username: admin
    password: "{{ vault_amt_password }}"
    port: 16992
    use_tls: false
    state: reboot
```

### 2. Fleet Status Check
```yaml
- name: Check fleet power states
  parmstro.intel_amt.amt_power:
    host: "{{ item }}"
    username: admin
    password: "{{ vault_amt_password }}"
    port: 16992
    use_tls: false
    state: query
  loop: "{{ amt_hosts }}"
```

### 3. Network Configuration
```yaml
- name: Configure static IP
  parmstro.intel_amt.amt_network_settings:
    host: "{{ current_amt_ip }}"
    username: admin
    password: "{{ vault_amt_password }}"
    use_tls: false
    dhcp_enabled: false
    ip_address: 192.168.254.100
    subnet_mask: 255.255.255.0
    gateway: 192.168.254.1
    primary_dns: 8.8.8.8
```

### 4. Boot Verification
```yaml
- name: Check event log after reboot
  parmstro.intel_amt.amt_event_log:
    host: "{{ amt_host }}"
    username: admin
    password: "{{ vault_amt_password }}"
    port: 16992
    use_tls: false
    max_records: 20
  register: boot_events
```

## Integration with Red Hat Satellite/Foreman

This collection enables:
1. **Remote power control** for bare metal systems
2. **PXE boot triggering** for Foreman Discovery
3. **Boot verification** via event logs
4. **Network IP management** for AMT interfaces
5. **Fleet-wide operations** across 42 NUC systems

## AMT 10.0.56 Limitations

Based on testing with actual hardware:

❌ **No Hardware Inventory** - AMT 10.x does not expose CPU/RAM/disk details via WSMAN  
❌ **Limited Enumeration** - Most resources require GET with specific selectors, not Enumerate  
❌ **Management Only** - Focus is out-of-band management, not hardware discovery  

**Recommendation:** Use OS-level tools (Ansible facts, dmidecode) or Satellite inventory for hardware details.

## What Works vs What Doesn't

### Works (AMT 10.0.56)
✅ Power management  
✅ Network settings (read and write)  
✅ Event logs  
✅ Basic system status  
✅ Time synchronization info  

### Doesn't Work
❌ CIM hardware enumeration (processor, memory, disk)  
❌ Advanced boot configuration  
❌ Certificate management  
❌ VLAN configuration (may work with different approach)  

## Installation

```bash
ansible-galaxy collection install parmstro.intel_amt
```

## Documentation

- README.md - Collection overview
- SECURITY.md - Security best practices
- AMT_10_CAPABILITIES.md - Detailed AMT 10.x capabilities
- tests/TEST_CREDENTIALS.md - Credential management guide
- vault/README.md - Vault directory usage

## Testing

```bash
# Lint
make lint

# Build
make build

# Install locally
make install

# Fleet test
ansible-playbook test_fleet.yml --vault-password-file=.vault_password
```

## Next Steps for Galaxy Publication

1. ✅ Core functionality tested
2. ✅ ansible-lint passing
3. ✅ Real hardware validation
4. ✅ Documentation complete
5. ⏳ Integration test suite (in progress)
6. ⏳ GitHub repository creation
7. ⏳ Galaxy publication

## Credits

Developed for managing 42 Intel NUC5i5MYBE systems in NUCLabv3 infrastructure.
