# Intel AMT Mode Compatibility Guide

## Understanding AMT Modes

Intel Active Management Technology (AMT) can be deployed in different operational modes, which significantly affect available features.

## Small Business Mode vs Enterprise Mode

### Small Business Mode

**Characteristics:**
- Simplified setup via Intel MEBx
- Manual configuration only
- **No TLS/HTTPS support** (HTTP only on port 16992)
- No TLS PKI menu in MEBx
- Lower complexity, less secure
- Suitable for isolated networks

**Common Implementations:**
- Consumer and small business Intel NUCs
- Standard Manageability (non-vPro Enterprise) SKUs
- Many AMT 10.x and earlier systems
- Cost-optimized deployments

**Tested Systems with Small Business Mode:**
- Intel NUC5i5MYBE with AMT 10.0.56 build 3002
- BIOS: MYBDWi5v.86A.0059.2022.0706.2207

### Enterprise Mode

**Characteristics:**
- Remote provisioning support
- **Full TLS/HTTPS support** (port 16993)
- TLS PKI menu available in MEBx
- Certificate-based authentication
- Higher complexity, more secure
- Requires PKI infrastructure

**Common Implementations:**
- Corporate vPro systems
- Enterprise workstations and servers
- AMT 11.x and newer (all configurations)
- Systems requiring compliance/security certifications

## How to Check Your AMT Mode

### Method 1: Check for TLS PKI Menu (Definitive)

1. Boot system
2. Press **Ctrl+P** during boot to enter Intel MEBx
3. Navigate: **Intel(R) AMT Configuration**
4. Look for **"TLS PKI"** menu option

**Result:**
- ✅ TLS PKI menu present = **Enterprise Mode**
- ❌ TLS PKI menu absent = **Small Business Mode**

### Method 2: Test Port 16993

```bash
# Test if HTTPS port is listening
nc -zv <amt_ip> 16993

# Or use ansible playbook
ansible-playbook playbooks/probe_amt_capabilities.yml \
  --vault-password-file .vault_password \
  -e test_amt_host=<amt_ip>
```

**Result:**
- ✅ Port 16993 open = **Enterprise Mode (likely)**
- ❌ Port 16993 closed = **Small Business Mode (likely)**

### Method 3: Check MEBx Provisioning Display

In Intel MEBx, check **Current Provisioning Mode**:

**Note:** "PKI" in Small Business Mode refers to provisioning method, NOT HTTPS capability. The presence of "TLS PKI" menu is the definitive indicator.

## Module Compatibility Matrix

| Module | Small Business Mode | Enterprise Mode | Notes |
|--------|---------------------|-----------------|-------|
| **amt_power** | ✅ Fully supported | ✅ Fully supported | Core functionality |
| **amt_host_status** | ✅ Fully supported | ✅ Fully supported | Core functionality |
| **amt_event_log** | ✅ Fully supported | ✅ Fully supported | Core functionality |
| **amt_log_clear** | ✅ Fully supported | ✅ Fully supported | Core functionality |
| **amt_network_settings** | ✅ Fully supported | ✅ Fully supported | Core functionality |
| **amt_tls_config** | ❌ **NOT supported** | ✅ Fully supported | Requires TLS support |

## Connection Parameters by Mode

### Small Business Mode

```yaml
# Always use these settings
parmstro.intel_amt.amt_power:
  host: 192.168.254.100
  username: admin
  password: "{{ amt_password }}"
  port: 16992              # HTTP only
  use_tls: false          # TLS not available
  verify_ssl: false       # N/A
  state: on
```

### Enterprise Mode

**Option 1: HTTP (works in both modes)**
```yaml
parmstro.intel_amt.amt_power:
  host: amt.example.com
  username: admin
  password: "{{ amt_password }}"
  port: 16992
  use_tls: false
  state: on
```

**Option 2: HTTPS (Enterprise Mode only)**
```yaml
parmstro.intel_amt.amt_power:
  host: amt.example.com
  username: admin
  password: "{{ amt_password }}"
  port: 16993              # HTTPS
  use_tls: true           # Use TLS
  verify_ssl: false       # Or true with proper CA
  state: on
```

## Security Recommendations by Mode

### For Small Business Mode (No TLS)

Since HTTPS is not available, implement defense-in-depth at network layer:

**Network Isolation:**
```yaml
# Dedicated management VLAN
- VLAN ID: 254
- Subnet: 192.168.254.0/24
- No routing to internet
- Firewall rules: AMT only from management hosts
```

**Access Control:**
```yaml
# VPN required for remote access
- Use strong AMT passwords (12+ characters)
- Rotate passwords quarterly
- Use Ansible Vault for credential storage
- Implement bastion/jump host
```

**Monitoring:**
```yaml
# Alert on anomalies
- Monitor for unexpected AMT connections
- Log all power state changes
- Track failed authentication attempts
- Audit AMT operations
```

**Playbook Security:**
```yaml
# Always use vault
- ansible.builtin.include_vars:
    dir: vault
    no_log: true

# Never log passwords
- parmstro.intel_amt.amt_power:
    password: "{{ amt_password }}"  # no_log: true on parameter
    ...
```

### For Enterprise Mode (TLS Available)

Implement certificate-based security:

**TLS Configuration:**
```yaml
# Enable HTTPS with proper certificates
- parmstro.intel_amt.amt_tls_config:
    host: amt.example.com
    port: 16992
    use_tls: false
    tls_enabled: true
    certmonger_request: true
    certmonger_nickname: "amt-{{ inventory_hostname }}"
    ...
```

**After TLS Enabled:**
```yaml
# Use HTTPS for all operations
- parmstro.intel_amt.amt_power:
    port: 16993
    use_tls: true
    verify_ssl: true  # With proper CA trust
    ...
```

## Upgrading from Small Business to Enterprise Mode

### Is It Possible?

**Theoretically:** Yes, but complex and risky

**Requirements:**
1. Hardware must support Enterprise Mode (check with Intel)
2. May need firmware/ME update
3. Requires unconfiguring current AMT setup
4. Need enterprise provisioning infrastructure
5. Risk of bricking AMT configuration

### Recommended Approach

**For existing Small Business Mode systems:**
- ❌ Do NOT attempt mode conversion
- ✅ Implement network-level security
- ✅ Use the 5 working modules
- ✅ Consider network isolation adequate for security

**For new hardware purchases:**
- ✅ Specify Enterprise vPro if TLS required
- ✅ Verify TLS support before purchase
- ✅ Request systems with "Intel AMT with TLS" 
- ✅ Test port 16993 on arrival

## Testing Your Configuration

### Automated Probe

```bash
# Comprehensive capability test
ansible-playbook playbooks/probe_amt_capabilities.yml \
  --vault-password-file .vault_password \
  -e test_amt_host=192.168.254.100 \
  -e amt_username="{{ amt_test_user }}" \
  -e amt_password="{{ amt_test_password }}"
```

**Output will show:**
- Port 16992 status (HTTP)
- Port 16993 status (HTTPS)
- AMT version and configuration
- Mode recommendation

### Manual Verification

**Check HTTP (always works):**
```bash
curl -k http://192.168.254.100:16992
```

**Check HTTPS (Enterprise Mode only):**
```bash
curl -k https://192.168.254.100:16993
```

## FAQ

**Q: My MEBx shows "PKI" mode but no HTTPS. Why?**

A: "PKI" in the provisioning mode refers to the provisioning method (using certificates to authenticate provisioning), not HTTPS capability. Small Business Mode can show "PKI" but still not support TLS/HTTPS.

**Q: Can I enable HTTPS via firmware update?**

A: Unlikely. TLS support is tied to AMT mode (Small Business vs Enterprise), which is usually determined by hardware SKU and initial provisioning. Check Intel support for your specific model.

**Q: Is Small Business Mode secure enough?**

A: For isolated management networks with proper firewall rules and access controls, yes. Many enterprise deployments successfully use HTTP-only AMT on isolated VLANs. The key is network-level security.

**Q: Do I need to buy new hardware for HTTPS?**

A: Not necessarily. For a 42-system fleet on an isolated management network, Small Business Mode with network security is acceptable. Newer Intel AMT 11+ systems will have full TLS support regardless of mode.

**Q: Will the amt_tls_config module work if I upgrade AMT firmware?**

A: Only if the firmware upgrade enables Enterprise Mode with TLS support. Check with Intel whether your hardware SKU supports Enterprise Mode before attempting firmware updates.

## References

- [AMT Small Business Mode Documentation](https://software.intel.com/sites/manageability/AMT_Implementation_and_Reference_Guide/WordDocuments/intelamtconfigurationsecuritymodels.htm)
- [AMT TLS Configuration Guide](https://trstn.com/posts/intel-amt-with-tls/)
- [Intel AMT Features Overview](https://www.intel.com/content/www/us/en/docs/active-management-technology/developer-guide/2021/overview.html)
- [Getting Started with Intel AMT](https://www.intel.com/content/www/us/en/developer/articles/guide/getting-started-with-active-management-technology.html)

---

**Last Updated:** 2026-05-30  
**Tested Configurations:** Intel NUC5i5MYBE (Small Business Mode), Various Enterprise vPro systems
