# amt_power - Manage Power State of Intel AMT Systems

## Synopsis

- Power on, power off, reboot, or check power state of systems with Intel AMT
- Uses WS-Management protocol to communicate with Intel AMT firmware
- Suitable for managing Intel NUC and other AMT-enabled systems
- Supports graceful and forced power operations

## Parameters

| Parameter | Choices/Defaults | Comments |
|-----------|------------------|----------|
| **host**<br/>string / required | | Hostname or IP address of the AMT management interface |
| **username**<br/>string / required | | AMT admin username |
| **password**<br/>string / required | | AMT admin password<br/>(no_log: true) |
| **port**<br/>integer | Default: 16992 | AMT management port |
| **use_tls**<br/>boolean | Default: true | Whether to use TLS for the connection |
| **verify_ssl**<br/>boolean | Default: false | Whether to verify SSL certificates |
| **state**<br/>string / required | Choices:<br/>- on<br/>- off<br/>- reboot<br/>- cycle<br/>- query | Desired power state:<br/>- `on`: Powers on the system<br/>- `off`: Gracefully powers off the system<br/>- `reboot`: Reboots the system<br/>- `cycle`: Hard power cycle<br/>- `query`: Check current state without changes |

## Return Values

| Key | Type | Description | Sample |
|-----|------|-------------|--------|
| **power_state** | string | Current power state of the system | "on" |
| **changed** | boolean | Whether the power state was changed | true |
| **msg** | string | Human-readable status message | "System powered on successfully" |

## Examples

### Power On a System

```yaml
- name: Power on NUC
  parmstro.intel_amt.amt_power:
    host: 192.168.1.100
    username: admin
    password: "{{ amt_password }}"
    state: on
```

### Reboot a System

```yaml
- name: Reboot NUC for PXE boot
  parmstro.intel_amt.amt_power:
    host: nuc01.amt.example.com
    username: admin
    password: "{{ amt_password }}"
    state: reboot
```

### Query Power State

```yaml
- name: Check current power state
  parmstro.intel_amt.amt_power:
    host: 192.168.1.100
    username: admin
    password: "{{ amt_password }}"
    state: query
  register: power_status

- name: Display power state
  ansible.builtin.debug:
    msg: "System is {{ power_status.power_state }}"
```

### Power Off with Non-TLS Connection

```yaml
- name: Power off system via HTTP
  parmstro.intel_amt.amt_power:
    host: 192.168.1.100
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    state: off
```

### Hard Power Cycle

```yaml
- name: Force power cycle unresponsive system
  parmstro.intel_amt.amt_power:
    host: 192.168.1.100
    username: admin
    password: "{{ amt_password }}"
    state: cycle
```

## Use Cases

### Bare Metal Provisioning Workflow

```yaml
- name: Prepare system for PXE boot
  block:
    - name: Ensure system is powered on
      parmstro.intel_amt.amt_power:
        host: "{{ amt_host }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
        state: on

    - name: Wait for system to initialize
      ansible.builtin.pause:
        seconds: 30

    - name: Reboot to trigger PXE boot
      parmstro.intel_amt.amt_power:
        host: "{{ amt_host }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
        state: reboot
```

### Fleet Power Management

```yaml
- name: Power on entire NUC cluster
  parmstro.intel_amt.amt_power:
    host: "{{ item }}"
    username: "{{ amt_username }}"
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    state: on
  loop:
    - c1s1n1.amt.example.com
    - c1s1n2.amt.example.com
    - c1s1n3.amt.example.com
  async: 300
  poll: 0
  register: power_jobs

- name: Wait for all systems to power on
  ansible.builtin.async_status:
    jid: "{{ item.ansible_job_id }}"
  loop: "{{ power_jobs.results }}"
  register: job_result
  until: job_result.finished
  retries: 30
  delay: 10
```

## Notes

- The module is idempotent - requesting the current state will not change anything
- Power operations may take several seconds to complete
- The `cycle` operation is a hard power cycle and should be used with caution
- For PXE booting, use `reboot` rather than `cycle` for cleaner BIOS initialization
- AMT firmware must be provisioned and configured before use
- Default AMT credentials should be changed in production environments

## Protocol Details

This module uses WS-Management (WSMAN) to communicate with Intel AMT firmware:
- CIM resource URI: `http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_PowerManagementService`
- Method: `RequestPowerStateChange`
- Authentication: HTTP Digest Authentication

## See Also

- [amt_host_status](amt_host_status.md) - For comprehensive system status including power state
- [amt_event_log](amt_event_log.md) - To check event logs after power operations
