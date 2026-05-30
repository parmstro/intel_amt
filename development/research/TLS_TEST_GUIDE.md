# Quick TLS Test Guide - Standalone System

Since you have physical access to a test system, this is the perfect opportunity to test the TLS configuration module end-to-end, including manual MEBx configuration if needed.

## Pre-Test Checklist

✅ Standalone test system powered on
✅ AMT accessible via HTTP (port 16992)
✅ Physical access available (keyboard/monitor or KVM)
✅ AMT admin credentials in vault
✅ 15-20 minutes available for testing

## Test Option 1: Self-Signed Certificate (Quickest)

**Best for:** Initial testing, no IPA required

```bash
# Run the test playbook
ansible-playbook playbooks/test_tls_single_system.yml \
  --vault-password-file .vault_password \
  -e test_amt_host=c1s2n2.amt.parmstrong.ca \
  -e cert_method=selfsigned

# What happens:
# 1. Generates self-signed certificate
# 2. Attempts WSMAN upload to AMT
# 3. Tests HTTPS connectivity
# 4. Provides MEBx instructions if needed
```

**Expected Result:**
- ✅ Certificate generated successfully
- ⚠️ WSMAN upload likely fails (AMT 10.0.56 limitation)
- 📋 Clear instructions for manual MEBx configuration

## Test Option 2: IPA Certificate (Production-Like)

**Best for:** Testing real-world workflow with certmonger

```bash
# Run with IPA method
ansible-playbook playbooks/test_tls_single_system.yml \
  --vault-password-file .vault_password \
  -e test_amt_host=c1s2n2.amt.parmstrong.ca \
  -e cert_method=ipa

# What happens:
# 1. Requests certificate from IPA via ipa-getcert
# 2. Waits for certificate issuance
# 3. Attempts WSMAN upload to AMT
# 4. Tests HTTPS connectivity
# 5. Provides MEBx instructions if needed
```

## Manual MEBx Configuration (Likely Required)

After the playbook runs, you'll get instructions like this:

### Step 1: Get Certificate Contents

```bash
# The playbook saves easy-to-access files:
cat /tmp/amt_test_certs/certificate_for_mebx.txt
cat /tmp/amt_test_certs/privatekey_for_mebx.txt

# Or view the full instructions:
cat /tmp/amt_test_certs/MANUAL_CONFIG_INSTRUCTIONS.md
```

### Step 2: Physical Access to System

1. **Reboot** the test system
2. Watch for boot screen
3. Press **Ctrl+P** when you see the prompt
4. Enter AMT admin password (from vault)

### Step 3: Navigate MEBx Interface

```
Intel(R) Management Engine BIOS Extension (MEBx)

Main Menu
├── Intel(R) AMT Configuration
│   ├── Remote Setup and Configuration
│   │   ├── TLS PKI
│   │   │   ├── PKI DNS Suffix           # Optional
│   │   │   ├── Manage Certificates
│   │   │   │   └── Import Certificate   # <-- SELECT THIS
```

### Step 4: Import Certificate

**In the "Import Certificate" screen:**

1. **Certificate** field:
   - Copy entire contents of `certificate_for_mebx.txt`
   - Including `-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----`
   - Paste into MEBx

2. **Private Key** field:
   - Copy entire contents of `privatekey_for_mebx.txt`  
   - Including `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----`
   - Paste into MEBx

3. **Save Configuration**
   - MEBx will validate the certificate
   - Save and exit MEBx
   - System will reboot

### Step 5: Verify HTTPS Works

After reboot, run verification:

```bash
ansible-playbook playbooks/verify_tls.yml \
  --vault-password-file .vault_password \
  -e test_amt_host=c1s2n2.amt.parmstrong.ca
```

**Success looks like:**
```
HTTPS (port 16993): ✅ Accessible
AMT Version: 10.0.56
Power State: on
✅ Power control working over HTTPS
```

## What You'll Learn

### If WSMAN Upload Works (Unlikely but Possible)
- ✅ Module successfully configured HTTPS automatically
- ✅ No manual intervention needed
- ✅ HTTPS working immediately
- 🎉 Best case scenario!

### If Manual MEBx Required (Expected)
- ✅ Module prepared certificates correctly
- ✅ Clear instructions provided
- ✅ Certificate import via MEBx works
- ✅ HTTPS functional after manual config
- 📝 Documented limitation of AMT 10.0.56

## Testing Timeline

**Automated Part:** ~3 minutes
- Certificate generation: 30 seconds
- WSMAN attempt: 30 seconds
- Connectivity tests: 30 seconds
- Instruction generation: 30 seconds

**Manual Part (if needed):** ~10 minutes
- Reboot and MEBx access: 2 minutes
- Certificate copy/paste: 5 minutes
- Save and reboot: 2 minutes
- Verification: 1 minute

**Total:** ~15 minutes

## Common Issues & Solutions

### Issue: Can't Access MEBx

**Symptom:** Ctrl+P doesn't work during boot

**Solutions:**
- Make sure you're pressing Ctrl+P at the right time (usually before OS loads)
- Try pressing it multiple times during boot
- Check if AMT is enabled in BIOS
- Verify system has AMT firmware (Intel NUC5i5MYBE does)

### Issue: Certificate Won't Import

**Symptom:** MEBx rejects certificate

**Causes:**
- Missing BEGIN/END markers
- Extra whitespace or line breaks
- Wrong format (must be PEM)
- Private key is encrypted (must be unencrypted)

**Solution:**
```bash
# Verify certificate format
openssl x509 -in /tmp/amt_test_certs/certificate_for_mebx.txt -text -noout

# Verify private key format (and that it's unencrypted)
openssl rsa -in /tmp/amt_test_certs/privatekey_for_mebx.txt -check
```

### Issue: HTTPS Still Not Working After Import

**Checks:**
1. System actually rebooted after MEBx save?
2. Firewall blocking port 16993?
3. Using correct hostname/IP?
4. Certificate matches hostname?

```bash
# Quick connectivity test
curl -k https://c1s2n2.amt.parmstrong.ca:16993

# Should return some XML/HTML, not connection refused
```

## Success Criteria

✅ Certificate generated (IPA or self-signed)
✅ Clear instructions provided for manual config
✅ MEBx accepts certificate import
✅ HTTPS accessible on port 16993
✅ amt_host_status works via HTTPS
✅ amt_power works via HTTPS

## Next Steps After Successful Test

1. **Document the process**
   - Time it took
   - Any MEBx quirks discovered
   - Screenshots if possible

2. **Update module documentation**
   - Add any learnings to docs
   - Update troubleshooting section

3. **Test on additional systems**
   - Verify process is repeatable
   - Test different certificate types

4. **Plan fleet deployment**
   - Certmonger for cert management
   - Bulk MEBx configuration strategy
   - Monitoring setup

## Files Generated During Test

```
/tmp/amt_test_certs/
├── amt-test-<timestamp>.crt          # Certificate
├── amt-test-<timestamp>.key          # Private key
├── amt-test-<timestamp>.csr          # CSR (if self-signed)
├── certificate_for_mebx.txt          # Easy access cert
├── privatekey_for_mebx.txt           # Easy access key
└── MANUAL_CONFIG_INSTRUCTIONS.md     # Full instructions
```

## Quick Reference Commands

```bash
# Run test (self-signed)
ansible-playbook playbooks/test_tls_single_system.yml \
  --vault-password-file .vault_password \
  -e test_amt_host=YOUR_HOST

# Run test (IPA)
ansible-playbook playbooks/test_tls_single_system.yml \
  --vault-password-file .vault_password \
  -e test_amt_host=YOUR_HOST \
  -e cert_method=ipa

# Verify after MEBx config
ansible-playbook playbooks/verify_tls.yml \
  --vault-password-file .vault_password \
  -e test_amt_host=YOUR_HOST

# View cert contents
cat /tmp/amt_test_certs/certificate_for_mebx.txt

# View key contents
cat /tmp/amt_test_certs/privatekey_for_mebx.txt

# Check cert details
openssl x509 -in /tmp/amt_test_certs/*.crt -text -noout

# Test HTTPS manually
curl -k https://YOUR_HOST:16993
```

---

**Ready to Test!** 🚀

Start with the self-signed method for quickest results, then try IPA if you want to test the full production workflow.
