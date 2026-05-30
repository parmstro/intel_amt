# amt_fleet_configure

Configure multiple AMT systems in parallel with standardized settings.

## Requirements

- parmstro.intel_amt collection installed
- Network connectivity to AMT systems
- Valid AMT credentials with administrative privileges

## Role Variables

```yaml
amt_fleet: []  # List of AMT systems with configuration
amt_fleet_parallel_limit: 10  # Concurrent operations
amt_fleet_continue_on_error: true  # Continue if one system fails
```

## Dependencies

None

## Example Playbook

```yaml
- hosts: management_node
  roles:
    - parmstro.intel_amt.amt_fleet_configure
```

## License

GPL-3.0-or-later

## Author

parmstro
