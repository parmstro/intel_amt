# Intel AMT Certificate Management Guide

This guide explains how to secure Intel AMT management interfaces with TLS certificates using the `amt_tls_config` module.

## ⚠️ Prerequisites - Check AMT Mode First

**IMPORTANT: This guide applies to Intel AMT in Enterprise Mode only.**

### Verify Your AMT Mode

Before proceeding, check if your AMT supports TLS/HTTPS:

1. **Boot system and press Ctrl+P** to enter Intel MEBx
2. Navigate to **Intel AMT Configuration**
3. **Look for "TLS PKI" menu**

**If TLS PKI menu is present:**
- ✅ Enterprise Mode - Continue with this guide
- ✅ TLS/HTTPS supported
- ✅ Certificate management available

**If TLS PKI menu is NOT present:**
- ❌ Small Business Mode - TLS not supported
- ❌ This guide does not apply
- ❌ Use network-level security instead (see Security Recommendations below)

### AMT Mode Quick Reference

| AMT Mode | TLS/HTTPS | This Guide Applies? | Alternative |
|----------|-----------|---------------------|-------------|
| Enterprise Mode | ✅ Supported | ✅ YES | Use certificate workflow |
| Small Business Mode | ❌ Not supported | ❌ NO | Network isolation (see below) |

### Known Configurations

**Small Business Mode (TLS Not Available):**
- Intel NUC5i5MYBE with AMT 10.0.56
- Many consumer/small business Intel NUC models
- Standard Manageability (non-vPro Enterprise) SKUs

**Enterprise Mode (TLS Available):**
- Intel AMT 11.x and newer (all modes)
- Corporate vPro systems
- Enterprise workstations with full AMT feature set

---

## For Small Business Mode: Network Security Instead

If your AMT is in Small Business Mode (no TLS support), implement these security measures:

### Network Isolation
```
✅ Dedicated management VLAN (e.g., 192.168.254.0/24)
✅ No routing to untrusted networks
✅ Firewall rules: AMT access only from management hosts
✅ No internet exposure
✅ VPN required for remote access
```

### Access Control
```
✅ Strong AMT admin passwords (Ansible Vault)
✅ Regular password rotation
✅ Audit logging of AMT access
✅ Bastion/jump host architecture
```

### Monitoring
```
✅ Alert on unexpected AMT connections
✅ Log all power state changes
✅ Track failed authentication attempts
```

---

## For Enterprise Mode: Certificate Management

If you have Enterprise Mode AMT with TLS support, continue below:

## Why Use HTTPS for AMT?

**Security Requirements:**
- HTTP transmits AMT admin credentials in cleartext (even with Digest Auth)
- Management traffic including power commands is unencrypted
- Vulnerable to man-in-the-middle attacks
- Does not meet security compliance requirements (PCI-DSS, HIPAA, etc.)

**Benefits of HTTPS:**
- ✅ Encrypted management traffic
- ✅ Authenticated server identity
- ✅ Protection against MITM attacks
- ✅ Compliance with security standards
- ✅ Integration with enterprise PKI

## Certificate Options

### Option 1: Red Hat Identity Management (IPA) - **Recommended**

**Best for:**
- Production environments
- Enterprise deployments
- Automated certificate lifecycle management
- Integration with existing Red Hat infrastructure

**Advantages:**
- Automatic certificate issuance
- Integrated renewal tracking via certmonger
- Centralized CA management
- Kerberos principal binding
- No manual CSR generation

**Requirements:**
- Red Hat IPA server deployed
- Management host enrolled as IPA client
- `ipa-getcert` command available

**Workflow:**
```yaml
- name: Secure AMT with IPA certificate
  parmstro.intel_amt.amt_tls_config:
    host: nuc01.amt.example.com
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    tls_enabled: true
    certmonger_request: true
    certmonger_nickname: "amt-nuc01"
    certmonger_subject: "CN=nuc01.amt.example.com"
    certmonger_principal: "host/nuc01.amt.example.com@EXAMPLE.COM"
    certificate_path: /var/lib/certmonger/amt/nuc01.crt
    private_key_path: /var/lib/certmonger/amt/nuc01.key
```

### Option 2: Manual Certificate with Existing CA

**Best for:**
- Organizations with existing PKI
- Integration with third-party CAs
- Custom certificate requirements

**Workflow:**
1. Generate CSR
2. Submit to CA
3. Receive signed certificate
4. Upload to AMT

```yaml
- name: Upload CA-signed certificate
  parmstro.intel_amt.amt_tls_config:
    host: nuc01.amt.example.com
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    tls_enabled: true
    certificate_path: /etc/pki/amt/nuc01.crt
    private_key_path: /etc/pki/amt/nuc01.key
    ca_certificate_path: /etc/pki/ca-trust/source/anchors/corporate-ca.crt
```

### Option 3: Self-Signed Certificates

**Best for:**
- Lab/testing environments
- Isolated networks
- Quick setup without CA infrastructure

**Limitations:**
- ⚠️ Not suitable for production
- ⚠️ No chain of trust
- ⚠️ Browser/client warnings
- ⚠️ Manual trust configuration required

**Workflow:**
```yaml
# Generate self-signed certificate
- name: Create self-signed certificate
  community.crypto.x509_certificate:
    path: /etc/pki/amt/nuc01.crt
    privatekey_path: /etc/pki/amt/nuc01.key
    provider: selfsigned
    selfsigned_not_after: "+365d"

# Upload to AMT
- name: Configure AMT with self-signed cert
  parmstro.intel_amt.amt_tls_config:
    host: nuc01.amt.example.com
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
    tls_enabled: true
    certificate_path: /etc/pki/amt/nuc01.crt
    private_key_path: /etc/pki/amt/nuc01.key
```

## AMT 10.0.56 WSMAN Limitations

### Important Note

Intel AMT 10.0.56 has **limited WSMAN support** for certificate management. The `amt_tls_config` module attempts automated certificate upload, but you may need to **manually configure certificates via Intel MEBx**.

### What the Module Does

1. ✅ Manages certmonger certificate requests (if using IPA)
2. ✅ Prepares certificate files in correct format
3. ✅ Attempts WSMAN certificate upload
4. ✅ Provides clear instructions if manual configuration needed

### Manual Configuration via Intel MEBx

If WSMAN upload fails (common on AMT 10.0.56):

**Steps:**
1. Reboot the AMT-enabled system
2. Press **Ctrl+P** during boot to enter Intel MEBx
3. Enter AMT admin password
4. Navigate to: **Remote Setup and Configuration → TLS PKI**
5. Select **Import Certificate**
6. Paste certificate contents from generated `.crt` file
7. Paste private key contents from generated `.key` file
8. Save and exit MEBx
9. System will reboot
10. Verify HTTPS connectivity on port 16993

**Certificate File Locations:**
- Certificate: `/var/lib/certmonger/amt/<hostname>.crt`
- Private Key: `/var/lib/certmonger/amt/<hostname>.key`

**View certificate contents:**
```bash
cat /var/lib/certmonger/amt/nuc01.crt
```

**View private key contents:**
```bash
sudo cat /var/lib/certmonger/amt/nuc01.key
```

## Complete Workflow Examples

### Example 1: Secure Entire Fleet with IPA

See: `playbooks/secure_amt_with_ipa.yml`

This comprehensive playbook:
- ✅ Verifies IPA client setup
- ✅ Requests certificates for all systems
- ✅ Configures HTTPS
- ✅ Validates connectivity
- ✅ Generates detailed report
- ✅ Provides manual configuration instructions for failed systems

### Example 2: Manual Certificate Workflow

See: `playbooks/manual_certificate_upload.yml`

This playbook demonstrates:
- ✅ Self-signed certificate generation
- ✅ Certificate upload to single system
- ✅ HTTPS validation
- ✅ Troubleshooting guidance

## Certificate Lifecycle Management

### Monitoring Certificate Expiration

**List all AMT certificates:**
```bash
ipa-getcert list | grep "amt-"
```

**Check specific certificate:**
```bash
ipa-getcert list -n amt-nuc01
```

**Check expiration dates:**
```bash
ipa-getcert list | grep -E "amt-|expires"
```

### Automated Renewal

**Certmonger automatic renewal:**
- Certmonger automatically renews certificates before expiration
- Default: 28 days before expiration
- Check renewal status: `systemctl status certmonger`

**Monitor renewal:**
```bash
# Set up daily monitoring
crontab -e

# Add line:
0 2 * * * ipa-getcert list | grep -E "amt-|expires|status" | mail -s "AMT Certificate Status" admin@example.com
```

### Manual Certificate Renewal

**Force renewal via certmonger:**
```bash
ipa-getcert resubmit -n amt-nuc01
```

**Wait for renewal:**
```bash
ipa-getcert list -n amt-nuc01 | grep status
# Should show: status: MONITORING
```

**Upload renewed certificate to AMT:**
```yaml
- name: Update AMT with renewed certificate
  parmstro.intel_amt.amt_tls_config:
    host: nuc01.amt.example.com
    username: admin
    password: "{{ amt_password }}"
    port: 16993
    use_tls: true
    certificate_path: /var/lib/certmonger/amt/nuc01.crt
    private_key_path: /var/lib/certmonger/amt/nuc01.key
```

## Troubleshooting

### HTTPS Not Accessible After Configuration

**Check 1: Verify certificate was uploaded**
```bash
# Check module output for warnings
# Look for: "Certificate upload not supported via WSMAN"
```

**Check 2: Firewall rules**
```bash
# Ensure port 16993 is accessible
firewall-cmd --list-ports
firewall-cmd --add-port=16993/tcp --permanent
firewall-cmd --reload
```

**Check 3: Test basic connectivity**
```bash
# HTTP (should still work)
curl -k http://nuc01.amt.example.com:16992

# HTTPS
curl -k https://nuc01.amt.example.com:16993
```

**Check 4: AMT event logs**
```yaml
- name: Check for TLS-related errors
  parmstro.intel_amt.amt_event_log:
    host: nuc01.amt.example.com
    username: admin
    password: "{{ amt_password }}"
    port: 16992
    use_tls: false
```

### Certificate Mismatch Errors

**Symptom:** SSL certificate verification fails

**Cause:** Certificate CN doesn't match hostname

**Solution:**
```yaml
# Generate certificate with correct subject
certmonger_subject: "CN=exact.hostname.match.com"

# Or disable SSL verification (testing only)
verify_ssl: false
```

### Certmonger Request Fails

**Check IPA enrollment:**
```bash
ipa-client-install --unattended --check
```

**Check certmonger service:**
```bash
systemctl status certmonger
systemctl restart certmonger
```

**Check IPA server connectivity:**
```bash
kinit admin
ipa ping
```

**View certmonger logs:**
```bash
journalctl -u certmonger -f
```

## Security Best Practices

### 1. Certificate Key Protection

```bash
# Ensure private keys have restricted permissions
chmod 600 /var/lib/certmonger/amt/*.key
chown root:root /var/lib/certmonger/amt/*.key
```

### 2. Transition Strategy

**Recommended approach:**
1. ✅ Enable HTTPS alongside HTTP
2. ✅ Verify HTTPS works on all systems
3. ✅ Update automation/monitoring to use HTTPS
4. ✅ Run parallel for validation period (1-2 weeks)
5. ⚠️ Consider disabling HTTP after validation

**DO NOT:**
- ❌ Disable HTTP before verifying HTTPS works
- ❌ Skip connectivity validation
- ❌ Forget to update monitoring systems

### 3. Recovery Procedures

**Document recovery steps:**
1. How to access MEBx on each system
2. Location of certificate files
3. Procedure for manual certificate import
4. Emergency HTTP re-enable process

**Keep HTTP access available until:**
- All systems verified on HTTPS
- Recovery procedures tested
- Team trained on MEBx access
- Monitoring updated

### 4. Certificate Rotation

**Regular rotation schedule:**
- Default: Certmonger auto-renews before expiration
- Recommended: Force renewal every 6 months
- Emergency: Procedure for immediate revocation/reissue

### 5. Audit Trail

**Log certificate operations:**
```yaml
- name: Record certificate deployment
  ansible.builtin.lineinfile:
    path: /var/log/amt_security_audit.log
    line: "{{ ansible_date_time.iso8601 }} - {{ ansible_hostname }} - Certificate deployed to {{ amt_host }}"
    create: true
```

## Integration with Monitoring

### Nagios/Icinga Check

```bash
#!/bin/bash
# Check AMT HTTPS certificate expiration

HOST=$1
WARN_DAYS=30
CRIT_DAYS=7

EXPIRY=$(echo | openssl s_client -connect ${HOST}:16993 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s)
NOW_EPOCH=$(date +%s)
DAYS_REMAINING=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))

if [ $DAYS_REMAINING -lt $CRIT_DAYS ]; then
    echo "CRITICAL: Certificate expires in $DAYS_REMAINING days"
    exit 2
elif [ $DAYS_REMAINING -lt $WARN_DAYS ]; then
    echo "WARNING: Certificate expires in $DAYS_REMAINING days"
    exit 1
else
    echo "OK: Certificate valid for $DAYS_REMAINING days"
    exit 0
fi
```

### Prometheus Exporter

Monitor certificate expiration for entire fleet via Prometheus.

## Additional Resources

- **Module Documentation**: [docs/amt_tls_config.md](docs/amt_tls_config.md)
- **IPA Playbook**: [playbooks/secure_amt_with_ipa.yml](playbooks/secure_amt_with_ipa.yml)
- **Manual Playbook**: [playbooks/manual_certificate_upload.yml](playbooks/manual_certificate_upload.yml)
- **Red Hat IPA Docs**: https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/planning_identity_management/
- **Intel AMT Docs**: https://software.intel.com/content/www/us/en/develop/topics/iot/hardware/vpro-platform-retail.html

---

**Last Updated**: 2026-05-30
