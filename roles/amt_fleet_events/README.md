# amt_fleet_events

Retrieve event logs from multiple AMT systems in parallel.

## Requirements

- parmstro.intel_amt collection installed
- Network connectivity to AMT systems
- Valid AMT credentials

## Role Variables

```yaml
amt_fleet: []  # List of AMT systems (from inventory)
amt_fleet_parallel_limit: 10  # Concurrent queries
amt_fleet_continue_on_error: true  # Continue if one system fails
```

## Dependencies

None

## Example Playbook

```yaml
- hosts: management_node
  roles:
    - parmstro.intel_amt.amt_fleet_events
```

## License

GPL-3.0-or-later

## Author

parmstro
