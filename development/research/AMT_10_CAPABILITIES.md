# Intel AMT 10.0.56 Capabilities

Based on testing with actual NUC5i5MYBE hardware running AMT 10.0.56 build 3002.

## What Works

### Management Functions
✅ **Power Control** - Full power management (on, off, reboot, cycle)
- Module: `amt_power`
- Resource: `CIM_PowerManagementService`

✅ **Event Logs** - Read and clear AMT event logs  
- Modules: `amt_event_log`, `amt_log_clear`
- Resource: `AMT_MessageLog`

✅ **Basic System Status** - Power state, network info
- Module: `amt_host_status`
- Resources: `CIM_ComputerSystem`, `AMT_EthernetPortSettings`, `CIM_BIOSElement`

### Available Information

**From CIM_ComputerSystem (with Selector: Name=ManagedSystem):**
- System name
- Enabled state
- Operational status  
- Power state (via CIM_AssociatedPowerManagementService)

**From AMT_EthernetPortSettings (with Selector: InstanceID=Intel(r) AMT Ethernet Port Settings 0):**
- IPv4 address
- IPv6 address (or "Disabled")
- MAC address
- Link status

**From CIM_BIOSElement:**
- BIOS version
- Manufacturer

**From IPS_GeneralSettings (Intel Platform Services):**
- Firmware version components

**From AMT_TimeSynchronizationService:**
- AMT system time (UTC)

## What Does NOT Work

### Hardware Inventory via CIM Enumeration  
❌ **Processor Info** - CIM_Processor enumeration returns 0 items
❌ **Memory Info** - CIM_PhysicalMemory enumeration returns 0 items  
❌ **Disk Info** - CIM_DiskDrive not supported (400 error)
❌ **Chassis Info** - CIM_Chassis enumeration returns 0 items
❌ **Battery Info** - CIM_Battery enumeration returns 0 items (expected on desktops)

###AMT-Specific Advanced Features
❌ **Network Configuration** - AMT_EthernetPortSettings enumeration fails (400 error)
  - Can GET specific instance with selector, but can't enumerate all
❌ **Boot Configuration** - AMT_BootCapabilities/AMT_BootSettingData enumeration fails
❌ **Security/Certificates** - AMT_TLSSettingData, AMT_PublicKeyCertificate enumeration fails
❌ **General Settings** - AMT_GeneralSettings enumeration fails

## Why This Happens

**AMT 10.0.56 Limitations:**
1. **No CIM Hardware Enumeration**: AMT 10.x does not expose hardware inventory details via WSMAN/CIM
2. **Selective Instance Access Only**: Most resources require knowing the exact InstanceID/Name selector
3. **Management-Focused**: AMT is for out-of-band management, not hardware discovery
4. **GET vs Enumerate**: Must use GET with selectors, not Enumerate operations

## Recommendations

### For This Collection

**Keep These Modules (Working):**
- `amt_power` - Core functionality ✓
- `amt_host_status` - Working with known selectors ✓
- `amt_event_log` - Works ✓
- `amt_log_clear` - Works ✓

**Remove/Mark Experimental:**
- `amt_system_info` - Returns empty (no CIM hardware data)
- `amt_processor_info` - Returns empty
- `amt_memory_info` - Returns empty
- `amt_disk_info` - Not supported
- `amt_battery_info` - Returns empty
- `amt_network_config` - Enumeration fails
- `amt_boot_config` - Enumeration fails
- `amt_security_config` - Enumeration fails
- `amt_firmware_info` - Partial data only

### Alternative Approaches

**For Hardware Inventory:**
- Use OS-level discovery (Ansible facts, dmidecode, lshw)
- Use Red Hat Satellite/Foreman hardware inventory
- Use IPMI/Redfish if available on other hardware

**For AMT Network/Boot/Security Config:**
- These could be rewritten as configuration modules (SET operations with known selectors)
- Or document that AMT 10.x has limited read-only management info

## Verified Working Configuration

```yaml
# What you CAN reliably do with AMT 10.0.56:

- name: Power cycle for PXE boot
  parmstro.intel_amt.amt_power:
    host: c1s2n2.amt.parmstrong.ca
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    state: reboot

- name: Check system status
  parmstro.intel_amt.amt_host_status:
    host: c1s2n2.amt.parmstrong.ca
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
  register: status

- name: Get event log
  parmstro.intel_amt.amt_event_log:
    host: c1s2n2.amt.parmstrong.ca
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    max_records: 50
```

## Conclusion

For your 42 NUC fleet management use case, the working modules (power, status, event log) provide the essential out-of-band management capabilities you need for:
- Remote power control
- PXE boot triggering
- Boot verification via event logs
- Basic connectivity/IP verification

Hardware inventory should be collected via other means (Satellite, OS facts) once systems are booted.
