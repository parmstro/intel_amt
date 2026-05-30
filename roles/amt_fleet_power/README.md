# amt_fleet_power

Fleet power management role for Intel AMT systems using the aggregator pattern.

## Description

This role manages power states across multiple Intel AMT systems simultaneously. It provides:

- Parallel execution across fleet with configurable throttling
- Aggregated results and summary statistics
- Error handling with continue-on-error option
- Power sequencing with configurable delays
- Detailed logging and reporting

## Requirements

- `parmstro.intel_amt` collection installed
- Network access to AMT management interfaces
- Valid AMT credentials

## Role Variables

### Required Variables

```yaml
amt_fleet_targets:
  system1:
    host: 192.168.254.209
    username: admin
    password: "{{ vault_password }}"
  system2:
    host: 192.168.254.210
    username: admin
    password: "{{ vault_password }}"
```

### Optional Variables

```yaml
# Power state: on, off, reboot, cycle, query
amt_fleet_power_state: query

# Continue processing if individual systems fail
amt_fleet_continue_on_error: true

# Maximum parallel operations
amt_fleet_parallel_limit: 10

# Delay between operations (seconds)
amt_fleet_operation_delay: 0

# Display summary
amt_fleet_show_summary: true
amt_fleet_show_failures: true

# Save detailed results to file
amt_fleet_results_file: /tmp/amt_fleet_power_results.md
```

## Dependencies

None

## Example Playbook

### Query power state across fleet

```yaml
- name: Query AMT fleet power state
  hosts: localhost
  gather_facts: false
  vars:
    amt_fleet_targets:
      c1s2n2:
        host: 192.168.254.209
        username: admin
        password: "{{ vault_amt_password }}"
        port: 16992
        use_tls: false
      c1s2n3:
        host: 192.168.254.210
        username: admin
        password: "{{ vault_amt_password }}"
        port: 16992
        use_tls: false
    amt_fleet_power_state: query
  roles:
    - parmstro.intel_amt.amt_fleet_power
```

### Power on entire fleet

```yaml
- name: Power on all NUCs
  hosts: localhost
  gather_facts: false
  vars:
    amt_fleet_targets: "{{ lookup('file', 'fleet_inventory.yml') | from_yaml }}"
    amt_fleet_power_state: on
    amt_fleet_parallel_limit: 5
    amt_fleet_operation_delay: 2
  roles:
    - parmstro.intel_amt.amt_fleet_power
```

### Graceful shutdown with sequencing

```yaml
- name: Graceful shutdown of rack
  hosts: localhost
  gather_facts: false
  vars:
    amt_fleet_targets:
      # Shutdown in reverse order (stack 2 -> stack 1)
      c1s2n7: { host: "192.168.254.217", username: admin, password: "{{ vault_pwd }}", port: 16992, use_tls: false }
      c1s2n6: { host: "192.168.254.216", username: admin, password: "{{ vault_pwd }}", port: 16992, use_tls: false }
      c1s1n7: { host: "192.168.254.207", username: admin, password: "{{ vault_pwd }}", port: 16992, use_tls: false }
      c1s1n6: { host: "192.168.254.206", username: admin, password: "{{ vault_pwd }}", port: 16992, use_tls: false }
    amt_fleet_power_state: off
    amt_fleet_parallel_limit: 2
    amt_fleet_operation_delay: 5
  roles:
    - parmstro.intel_amt.amt_fleet_power
```

### Dynamic fleet from inventory

```yaml
- name: Reboot all chassis 1 systems
  hosts: localhost
  gather_facts: false
  vars:
    amt_fleet_targets: >-
      {{
        groups['chassis_1'] | default([]) |
        map('extract', hostvars) |
        items2dict(key_name='inventory_hostname', value_name='amt_config')
      }}
    amt_fleet_power_state: reboot
  roles:
    - parmstro.intel_amt.amt_fleet_power
```

## Fleet Target Format

Each target in `amt_fleet_targets` must include:

- `host`: AMT management interface address
- `username`: AMT admin username  
- `password`: AMT admin password

Optional per-target settings:

- `port`: AMT port (default: 16992)
- `use_tls`: Use HTTPS (default: false)
- `verify_ssl`: Verify SSL certificates (default: false)

## Return Values

The role sets the following facts:

- `amt_fleet_summary`: Dictionary with total, successful, failed, changed counts and success_rate
- `amt_fleet_power_results`: Full results from all operations

## License

GPL-3.0-or-later

## Author

parmstro
