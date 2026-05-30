# Intel AMT Collection - Module Documentation

This directory contains comprehensive documentation for all modules in the `parmstro.intel_amt` Ansible collection.

## Documentation Index

- [**Collection Overview**](index.md) - Start here for collection introduction and quick start

### Module Documentation

#### Power Management
- [**amt_power**](amt_power.md) - Manage power state (on, off, reboot, cycle, query)

#### System Monitoring
- [**amt_host_status**](amt_host_status.md) - Retrieve comprehensive system status and configuration

#### Event Log Management
- [**amt_event_log**](amt_event_log.md) - Retrieve and parse AMT event logs
- [**amt_log_clear**](amt_log_clear.md) - Clear AMT event logs (message and security)

#### Network Configuration
- [**amt_network_settings**](amt_network_settings.md) - Configure AMT network settings (IPv4, IPv6, DHCP)

#### Security Configuration  
- [**amt_tls_config**](amt_tls_config.md) - Configure TLS/HTTPS and upload certificates (IPA/certmonger integration) ⚠️ *Requires Enterprise Mode*

#### Compatibility Guide
- [**AMT Mode Compatibility**](amt_mode_compatibility.md) - Small Business vs Enterprise Mode feature matrix

## Using ansible-doc

You can also view module documentation using the `ansible-doc` command:

```bash
# View specific module documentation
ansible-doc parmstro.intel_amt.amt_power
ansible-doc parmstro.intel_amt.amt_host_status
ansible-doc parmstro.intel_amt.amt_event_log
ansible-doc parmstro.intel_amt.amt_log_clear
ansible-doc parmstro.intel_amt.amt_network_settings
ansible-doc parmstro.intel_amt.amt_tls_config

# List all modules in the collection
ansible-doc -l parmstro.intel_amt

# View documentation in JSON format
ansible-doc -j parmstro.intel_amt.amt_power
```

## Additional Resources

### Collection Documentation
- [../README.md](../README.md) - Collection README
- [../CHANGELOG.md](../CHANGELOG.md) - Version history and changes
- [../TESTING.md](../TESTING.md) - Testing guide and procedures
- [../SECURITY.md](../SECURITY.md) - Security considerations and best practices

### Technical Documentation
- [../AMT_10_CAPABILITIES.md](../AMT_10_CAPABILITIES.md) - Intel AMT 10.0 capabilities reference
- [../COLLECTION_STATUS.md](../COLLECTION_STATUS.md) - Development status and roadmap

### Examples
- [../playbooks/](../playbooks/) - Example playbooks
- [../tests/integration/](../tests/integration/) - Integration test playbooks (additional examples)

## Module Categories

### Essential Modules (Production Ready)

**All AMT Modes (Small Business & Enterprise):**
- `amt_power` - Core power management
- `amt_host_status` - System information retrieval
- `amt_event_log` - Event log retrieval
- `amt_log_clear` - Log management
- `amt_network_settings` - Network configuration

**Enterprise Mode Only:**
- `amt_tls_config` - TLS/HTTPS security configuration (with IPA integration)
  - Requires AMT with TLS support
  - Not compatible with Small Business Mode
  - See [Compatibility Guide](amt_mode_compatibility.md)

### Typical Workflow

```yaml
# 1. Check system status
- parmstro.intel_amt.amt_host_status:
    host: "{{ amt_host }}"
    ...
  register: status

# 2. Configure network if needed
- parmstro.intel_amt.amt_network_settings:
    host: "{{ amt_host }}"
    dhcp_enabled: true
    ...
  when: status.dhcp_enabled == false

# 3. Power on the system
- parmstro.intel_amt.amt_power:
    host: "{{ amt_host }}"
    state: on
    ...

# 4. Check event logs
- parmstro.intel_amt.amt_event_log:
    host: "{{ amt_host }}"
    ...
  register: events

# 5. Clear logs after archiving
- parmstro.intel_amt.amt_log_clear:
    host: "{{ amt_host }}"
    log_type: message
    ...
```

## Getting Help

- **Module Issues**: Check module documentation and examples
- **Collection Issues**: See [../README.md](../README.md) for support information
- **Security Issues**: See [../SECURITY.md](../SECURITY.md) for reporting procedures

## Contributing

If you find errors or omissions in the documentation, please report them or submit improvements.

## License

GPL-3.0-or-later

---

**Navigation**: [Back to Collection Root](../) | [Collection README](../README.md) | [Documentation Index](index.md)
