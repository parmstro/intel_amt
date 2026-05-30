# amt_event_log - Retrieve Intel AMT Event Logs

## Synopsis

- Retrieve and parse event log entries from Intel AMT firmware
- Returns structured event data with timestamps and severity levels
- Useful for troubleshooting, auditing, and monitoring system events
- Supports filtering by log type (message or security logs)
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
| **log_type**<br/>string | Choices:<br/>- message<br/>- security<br/>Default: message | Type of log to retrieve:<br/>- `message`: General system events<br/>- `security`: Security and authentication events |
| **max_records**<br/>integer | Default: 100 | Maximum number of log entries to retrieve |

## Return Values

| Key | Type | Description | Sample |
|-----|------|-------------|--------|
| **events** | list of dicts | List of parsed event log entries | See examples below |
| **event_count** | integer | Number of events returned | 15 |
| **log_type** | string | Type of log retrieved | "message" |
| **changed** | boolean | Always false (read-only operation) | false |

### Event Entry Structure

Each event in the `events` list contains:

| Key | Type | Description | Sample |
|-----|------|-------------|--------|
| **timestamp** | string | ISO 8601 formatted timestamp | "2026-05-30T14:23:45Z" |
| **severity** | string | Event severity level | "Information" / "Warning" / "Critical" |
| **event_id** | integer | AMT event identifier | 2048 |
| **description** | string | Human-readable event description | "System boot completed" |
| **source** | string | Event source component | "BIOS" / "AMT" / "ME" |

## Examples

### Retrieve Recent Events

```yaml
- name: Get AMT event log
  parmstro.intel_amt.amt_event_log:
    host: nuc01.amt.example.com
    username: admin
    password: "{{ amt_password }}"
  register: events

- name: Display events
  ansible.builtin.debug:
    var: events.events
```

### Retrieve Security Events

```yaml
- name: Get security audit log
  parmstro.intel_amt.amt_event_log:
    host: nuc01.amt.example.com
    username: admin
    password: "{{ amt_password }}"
    log_type: security
    max_records: 50
  register: security_events

- name: Check for failed authentication attempts
  ansible.builtin.debug:
    msg: "WARNING: Failed login attempts detected"
  when: security_events.events | selectattr('description', 'search', 'failed') | list | length > 0
```

### Filter Events by Severity

```yaml
- name: Get event log
  parmstro.intel_amt.amt_event_log:
    host: "{{ amt_host }}"
    username: "{{ amt_username }}"
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
  register: all_events

- name: Display only critical events
  ansible.builtin.debug:
    msg: "Critical: {{ item.description }} at {{ item.timestamp }}"
  loop: "{{ all_events.events }}"
  when: item.severity == "Critical"
```

### Check for Recent Reboots

```yaml
- name: Check recent boot events
  parmstro.intel_amt.amt_event_log:
    host: "{{ amt_host }}"
    username: "{{ amt_username }}"
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    max_records: 20
  register: recent_events

- name: Find boot events
  ansible.builtin.set_fact:
    boot_events: "{{ recent_events.events | selectattr('description', 'search', 'boot|reboot') | list }}"

- name: Display last boot time
  ansible.builtin.debug:
    msg: "Last boot: {{ boot_events[0].timestamp }}"
  when: boot_events | length > 0
```

## Use Cases

### Post-Provisioning Verification

```yaml
- name: Verify successful provisioning
  block:
    - name: Power on system for PXE boot
      parmstro.intel_amt.amt_power:
        host: "{{ amt_host }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
        state: reboot

    - name: Wait for boot
      ansible.builtin.pause:
        minutes: 5

    - name: Check boot events
      parmstro.intel_amt.amt_event_log:
        host: "{{ amt_host }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
        max_records: 10
      register: boot_log

    - name: Verify PXE boot occurred
      ansible.builtin.assert:
        that:
          - boot_log.events | selectattr('description', 'search', 'PXE') | list | length > 0
        fail_msg: "PXE boot not detected in event log"
        success_msg: "PXE boot confirmed"
```

### Security Audit Collection

```yaml
- name: Collect security audit across fleet
  parmstro.intel_amt.amt_event_log:
    host: "{{ item }}"
    username: "{{ amt_username }}"
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    log_type: security
  loop: "{{ amt_hosts }}"
  register: security_audit

- name: Generate audit report
  ansible.builtin.copy:
    content: |
      # AMT Security Audit Report
      # Generated: {{ ansible_date_time.iso8601 }}
      
      {% for result in security_audit.results %}
      ## {{ result.item }}
      {% for event in result.events %}
      - {{ event.timestamp }} [{{ event.severity }}] {{ event.description }}
      {% endfor %}
      {% endfor %}
    dest: "/tmp/amt_security_audit_{{ ansible_date_time.date }}.md"
```

### Event-Based Alerting

```yaml
- name: Check for hardware errors
  parmstro.intel_amt.amt_event_log:
    host: "{{ amt_host }}"
    username: "{{ amt_username }}"
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    max_records: 100
  register: system_events

- name: Identify hardware issues
  ansible.builtin.set_fact:
    hw_errors: "{{ system_events.events | selectattr('severity', 'equalto', 'Critical') | list }}"

- name: Send alert if hardware errors found
  ansible.builtin.uri:
    url: "https://alerts.example.com/api/incident"
    method: POST
    body_format: json
    body:
      severity: critical
      host: "{{ amt_host }}"
      message: "Hardware errors detected"
      events: "{{ hw_errors }}"
  when: hw_errors | length > 0
```

### Continuous Monitoring

```yaml
- name: Monitor AMT events
  block:
    - name: Retrieve latest events
      parmstro.intel_amt.amt_event_log:
        host: "{{ amt_host }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
        max_records: 50
      register: current_events

    - name: Filter new events since last check
      ansible.builtin.set_fact:
        new_events: "{{ current_events.events | selectattr('timestamp', '>', last_check_time) | list }}"
      vars:
        last_check_time: "{{ lookup('file', '/tmp/last_amt_check.txt', errors='ignore') | default('1970-01-01T00:00:00Z') }}"

    - name: Process new events
      ansible.builtin.debug:
        msg: "New event: {{ item.severity }} - {{ item.description }}"
      loop: "{{ new_events }}"

    - name: Update last check timestamp
      ansible.builtin.copy:
        content: "{{ ansible_date_time.iso8601 }}"
        dest: /tmp/last_amt_check.txt
```

## Notes

- This is a read-only operation and never returns `changed: true`
- Events are returned in reverse chronological order (newest first)
- The `max_records` parameter limits results to prevent overwhelming output
- Event log capacity varies by AMT firmware version (typically 100-400 entries)
- Older events are automatically purged when the log fills
- Use [amt_log_clear](amt_log_clear.md) to clear logs after collection
- Timestamps are in UTC
- Event IDs and descriptions follow Intel AMT firmware specifications

## Common Event Types

### Message Log Events
- System boot/shutdown events
- PXE boot attempts
- BIOS initialization
- Hardware configuration changes
- Firmware updates

### Security Log Events
- Authentication successes and failures
- Certificate changes
- Permission modifications
- Remote access attempts
- Configuration changes

## Protocol Details

This module uses WS-Management (WSMAN) to retrieve event logs:
- CIM resource URI: `http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_RecordLog`
- Method: `EnumerateInstances` with filtering
- Authentication: HTTP Digest Authentication
- Response format: XML with base64-encoded event data

## See Also

- [amt_log_clear](amt_log_clear.md) - Clear event logs
- [amt_host_status](amt_host_status.md) - Retrieve current system status
- [amt_power](amt_power.md) - Power operations that generate events
