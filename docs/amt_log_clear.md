# amt_log_clear - Clear Intel AMT Event Logs

## Synopsis

- Clear message or security event logs on Intel AMT systems
- Useful for log rotation and cleanup after event collection
- Destructive operation that permanently removes log entries
- Typically used after retrieving and archiving events

## Parameters

| Parameter | Choices/Defaults | Comments |
|-----------|------------------|----------|
| **host**<br/>string / required | | Hostname or IP address of the AMT management interface |
| **username**<br/>string / required | | AMT admin username |
| **password**<br/>string / required | | AMT admin password<br/>(no_log: true) |
| **port**<br/>integer | Default: 16992 | AMT management port |
| **use_tls**<br/>boolean | Default: true | Whether to use TLS for the connection |
| **verify_ssl**<br/>boolean | Default: false | Whether to verify SSL certificates |
| **log_type**<br/>string | Choices:<br/>- message<br/>- security<br/>Default: message | Type of log to clear:<br/>- `message`: General system events<br/>- `security`: Security and authentication events |

## Return Values

| Key | Type | Description | Sample |
|-----|------|-------------|--------|
| **log_type** | string | Type of log that was cleared | "message" |
| **changed** | boolean | Whether the log was cleared | true |
| **msg** | string | Human-readable status message | "Message log cleared successfully" |

## Examples

### Clear Message Log

```yaml
- name: Clear AMT message log
  parmstro.intel_amt.amt_log_clear:
    host: nuc01.amt.example.com
    username: admin
    password: "{{ amt_password }}"
    log_type: message
```

### Clear Security Log

```yaml
- name: Clear AMT security log
  parmstro.intel_amt.amt_log_clear:
    host: nuc01.amt.example.com
    username: admin
    password: "{{ amt_password }}"
    log_type: security
```

### Clear Log via HTTP

```yaml
- name: Clear message log over HTTP
  parmstro.intel_amt.amt_log_clear:
    host: 192.168.1.100
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    log_type: message
```

## Use Cases

### Log Rotation After Collection

```yaml
- name: Collect and rotate AMT logs
  block:
    - name: Retrieve current event log
      parmstro.intel_amt.amt_event_log:
        host: "{{ amt_host }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
      register: events

    - name: Archive events to file
      ansible.builtin.copy:
        content: "{{ events.events | to_nice_json }}"
        dest: "/var/log/amt/{{ amt_host }}_{{ ansible_date_time.date }}.json"

    - name: Clear the log after archiving
      parmstro.intel_amt.amt_log_clear:
        host: "{{ amt_host }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
        log_type: message
```

### Security Audit Workflow

```yaml
- name: Security audit and cleanup
  block:
    - name: Collect security events
      parmstro.intel_amt.amt_event_log:
        host: "{{ amt_host }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
        log_type: security
      register: security_log

    - name: Send to SIEM system
      ansible.builtin.uri:
        url: "https://siem.example.com/api/events"
        method: POST
        body_format: json
        body:
          source: "amt"
          host: "{{ amt_host }}"
          events: "{{ security_log.events }}"

    - name: Clear security log after export
      parmstro.intel_amt.amt_log_clear:
        host: "{{ amt_host }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
        log_type: security
```

### Fleet Log Cleanup

```yaml
- name: Clear logs across entire fleet
  parmstro.intel_amt.amt_log_clear:
    host: "{{ item }}"
    username: "{{ amt_username }}"
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    log_type: message
  loop: "{{ amt_hosts }}"
  async: 60
  poll: 0
  register: clear_jobs

- name: Wait for all clears to complete
  ansible.builtin.async_status:
    jid: "{{ item.ansible_job_id }}"
  loop: "{{ clear_jobs.results }}"
  register: job_result
  until: job_result.finished
  retries: 10
```

### Pre-Test Log Reset

```yaml
- name: Prepare system for testing
  block:
    - name: Clear existing logs for clean test
      parmstro.intel_amt.amt_log_clear:
        host: "{{ amt_host }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
        log_type: message

    - name: Perform test operation
      parmstro.intel_amt.amt_power:
        host: "{{ amt_host }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
        state: reboot

    - name: Wait for reboot
      ansible.builtin.pause:
        seconds: 60

    - name: Collect test-specific events
      parmstro.intel_amt.amt_event_log:
        host: "{{ amt_host }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
      register: test_events

    - name: Verify expected events occurred
      ansible.builtin.assert:
        that:
          - test_events.events | selectattr('description', 'search', 'boot') | list | length > 0
```

### Scheduled Maintenance

```yaml
- name: Weekly log maintenance
  block:
    - name: Archive all logs
      include_tasks: archive_amt_logs.yml

    - name: Clear message logs
      parmstro.intel_amt.amt_log_clear:
        host: "{{ item }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
        log_type: message
      loop: "{{ amt_hosts }}"

    - name: Clear security logs
      parmstro.intel_amt.amt_log_clear:
        host: "{{ item }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
        log_type: security
      loop: "{{ amt_hosts }}"
```

### Conditional Log Clear

```yaml
- name: Clear logs only if nearly full
  block:
    - name: Check current log count
      parmstro.intel_amt.amt_event_log:
        host: "{{ amt_host }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
        max_records: 400
      register: current_log

    - name: Clear if approaching capacity
      parmstro.intel_amt.amt_log_clear:
        host: "{{ amt_host }}"
        username: "{{ amt_username }}"
        password: "{{ amt_password }}"
        port: 16992
        use_tls: false
        log_type: message
      when: current_log.event_count > 300
```

## Notes

- **WARNING**: This is a destructive operation that permanently deletes log entries
- Always retrieve and archive logs before clearing them
- The operation is idempotent - clearing an already-empty log succeeds
- Message and security logs are independent; clearing one does not affect the other
- Only users with AMT admin privileges can clear logs
- Consider regulatory and compliance requirements before implementing automatic log clearing
- There is no "undo" operation - cleared logs cannot be recovered

## Best Practices

1. **Always Archive First**: Retrieve logs with `amt_event_log` before clearing
2. **Verify Archive**: Confirm log data is properly stored before clearing
3. **Use Check Mode**: Test playbooks with `--check` flag before production runs
4. **Audit Clearing**: Log when and why AMT logs are cleared
5. **Separate Security Logs**: Handle security logs with stricter retention policies
6. **Scheduled Rotation**: Implement regular log rotation schedules

## Protocol Details

This module uses WS-Management (WSMAN) to clear event logs:
- CIM resource URI: `http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_RecordLog`
- Method: `ClearLog`
- Authentication: HTTP Digest Authentication

## See Also

- [amt_event_log](amt_event_log.md) - Retrieve event logs before clearing
- [amt_host_status](amt_host_status.md) - Retrieve system status
