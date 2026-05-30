# Release Checklist for v1.0.0

## Pre-Release Testing

### ✅ Completed
- [x] ansible-lint passes with production profile
- [x] Module tested on real hardware (c1s2n2.amt.parmstrong.ca)
- [x] Successfully rebooted NUC via AMT
- [x] Verified PXE boot and Satellite discovery integration
- [x] Passwords secured with Ansible Vault
- [x] .gitignore configured
- [x] Collection builds successfully

### Still To Do
- [ ] Run unit tests: `make unit`
- [ ] Run sanity tests: `make sanity`
- [ ] Run full integration tests: `make integration`
- [ ] Test with all 42 NUCs in fleet
- [ ] Verify check mode works correctly
- [ ] Test error handling (wrong password, unreachable host)
- [ ] Test with AMT 11.0.x (if available)
- [ ] Performance test with parallel operations

## Documentation Review
- [x] README.md complete
- [x] CHANGELOG.md created
- [x] SECURITY.md added
- [x] TESTING.md comprehensive
- [x] Module DOCUMENTATION accurate
- [x] Module EXAMPLES work
- [x] Module RETURN documented
- [ ] Review all docs for typos/clarity

## Code Quality
- [x] ansible-lint passes
- [ ] Python code follows PEP 8
- [ ] No TODO/FIXME in production code
- [ ] All functions have docstrings
- [ ] Error messages are helpful

## Security Review
- [x] Passwords marked `no_log: true`
- [x] Vault used for test credentials
- [x] .vault_password in .gitignore
- [ ] No secrets in git history
- [ ] SSL verification configurable
- [ ] Authentication failures handled gracefully

## Git & GitHub
- [ ] All changes committed
- [ ] Git history clean (no secrets)
- [ ] Create GitHub repository: https://github.com/parmstro/intel_amt
- [ ] Push code to GitHub
- [ ] Create v1.0.0 tag
- [ ] Create GitHub release with notes
- [ ] Upload collection tarball to release

## Ansible Galaxy
- [ ] galaxy.yml validated
- [ ] Collection namespace reserved on Galaxy (parmstro)
- [ ] Collection name available (intel_amt)
- [ ] API key configured
- [ ] Test installation from tarball
- [ ] Publish to Galaxy: `ansible-galaxy collection publish parmstro-intel_amt-1.0.0.tar.gz`
- [ ] Verify Galaxy listing
- [ ] Test installation from Galaxy

## Post-Release
- [ ] Announce on Red Hat forums
- [ ] Blog post about NUCLabv3 + AMT automation
- [ ] Update rhis-builder-nuc-bmc project README to reference collection
- [ ] Create example playbooks for common use cases
- [ ] Consider submitting to Ansible community topics

## Next Version Planning
Future modules to add:
- [ ] amt_boot_device - Control boot device order
- [ ] amt_sol - Serial-over-LAN management
- [ ] amt_kvm - KVM redirection control
- [ ] amt_event_log - Event log retrieval
- [ ] amt_config - General AMT configuration
- [ ] amt_user - User management

## Success Criteria
Before publishing to Galaxy:
1. All tests pass
2. Tested on production hardware (42 NUCs)
3. Documentation complete and accurate
4. No known critical bugs
5. Community feedback incorporated (if applicable)

## Notes
- Test host: c1s2n2.amt.parmstrong.ca
- Successfully integrated with Red Hat Satellite
- Designed for NUCLabv3 (42-node Intel NUC cluster)
- Primary use case: OpenShift bare metal provisioning
