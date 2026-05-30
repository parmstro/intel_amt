# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-30

### Added
- Initial release of parmstro.intel_amt collection
- `amt_power` module for power management via Intel AMT
  - Power operations: on, off, reboot, cycle, query
  - HTTP and HTTPS support
  - Check mode support
  - Tested with Intel NUC5i5MYBE (AMT 10.0.56)
- `amt_host_status` module for retrieving comprehensive system information
  - Returns power state, IPv4/IPv6 addresses, system ID, AMT time
  - Returns BIOS version, MAC address, enabled state
  - JSON output for inventory and monitoring
  - Tested and working on c1s2n2.amt.parmstrong.ca
- `amt_event_log` module for retrieving AMT event logs
  - Enumerates and retrieves event log entries
  - Framework for boot event parsing and uptime calculation
  - Tested with c1s2n2.amt.parmstrong.ca
- `amt_log_clear` module for clearing AMT event logs
  - Clear message log, provisioning log, or all logs
  - Check mode support for safe preview
  - Returns record count before clearing
  - Successfully tested on c1s2n2.amt.parmstrong.ca
- Comprehensive test suite
  - Unit tests with pytest
  - Integration tests with real hardware
  - ansible-lint passing with production profile
- Documentation
  - Module DOCUMENTATION, EXAMPLES, and RETURN
  - Collection README with usage examples
  - SECURITY.md for credential management
  - TESTING.md for test procedures
- Ansible Vault support for secure credential storage
- GPL-3.0-or-later license

### Tested
- Successfully tested on c1s2n2.amt.parmstrong.ca
- Verified PXE boot integration with Red Hat Satellite/Foreman Discovery
- Confirmed WS-Management protocol compatibility with AMT 10.0.x

### Security
- Passwords marked with `no_log: true`
- Vault-encrypted test credentials
- .gitignore configured to prevent password leaks

[1.0.0]: https://github.com/parmstro/intel_amt/releases/tag/v1.0.0
