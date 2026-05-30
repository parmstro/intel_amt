# Development Documentation Index

Quick reference to all internal development documentation.

## 📋 Quick Links

- [Collection Status](COLLECTION_STATUS.md) - Current development status
- [Testing Guide](testing/TESTING.md) - How to test before commits
- [Security Guidelines](testing/SECURITY.md) - Security best practices
- [Test Results](testing/TEST_RESULTS.md) - Latest test results

## 📁 Directory Structure

### Research & Discovery
Location: `development/research/`

| Document | Purpose | Last Updated |
|----------|---------|--------------|
| [AMT 10 Capabilities](research/AMT_10_CAPABILITIES.md) | AMT 10.0.56 feature testing | 2026-05-30 |
| [AMT TLS Limitation](research/AMT_10_TLS_LIMITATION.md) | Small Business Mode TLS limitations | 2026-05-30 |
| [Resource Discovery](research/AMT_RESOURCE_DISCOVERY.md) | WSMAN resource discovery results | 2026-05-30 |
| [Certificate Management](research/CERTIFICATE_MANAGEMENT.md) | Certificate management research | 2026-05-30 |
| [TLS Test Guide](research/TLS_TEST_GUIDE.md) | TLS testing procedures | 2026-05-30 |

### Testing & Validation
Location: `development/testing/`

| Document | Purpose | Last Updated |
|----------|---------|--------------|
| [Testing Guide](testing/TESTING.md) | Comprehensive testing procedures | 2026-05-30 |
| [Security Guidelines](testing/SECURITY.md) | Security best practices | 2026-05-30 |
| [Test Plan](testing/TEST_PLAN.md) | Pre-push test plan | 2026-05-30 |
| [Test Results](testing/TEST_RESULTS.md) | Latest test results | 2026-05-30 |
| [Release Checklist](testing/RELEASE_CHECKLIST.md) | Pre-release validation | 2026-05-30 |

### Development Status
Location: `development/`

| Document | Purpose | Last Updated |
|----------|---------|--------------|
| [Collection Status](COLLECTION_STATUS.md) | Overall collection status | 2026-05-30 |
| [Documentation Status](DOCUMENTATION.md) | Documentation coverage | 2026-05-30 |
| [Documentation Updates](DOCUMENTATION_UPDATE_SUMMARY.md) | Doc update history | 2026-05-30 |
| [Final Summary](FINAL_SUMMARY.md) | Development summary | 2026-05-30 |
| [Security Cleanup](SECURITY_CLEANUP_SUMMARY.md) | Security cleanup record | 2026-05-30 |

## 🎯 Common Tasks

### Before Committing
1. Read: [Test Plan](testing/TEST_PLAN.md)
2. Run: Tests against real hardware
3. Check: [Security Guidelines](testing/SECURITY.md)
4. Update: [Test Results](testing/TEST_RESULTS.md)

### Understanding AMT Limitations
1. Read: [AMT TLS Limitation](research/AMT_10_TLS_LIMITATION.md)
2. Check: [AMT Mode Compatibility](../docs/amt_mode_compatibility.md)
3. Reference: [Resource Discovery](research/AMT_RESOURCE_DISCOVERY.md)

### Adding New Modules
1. Review: [Collection Status](COLLECTION_STATUS.md)
2. Follow: [Testing Guide](testing/TESTING.md)
3. Reference: [Resource Discovery](research/AMT_RESOURCE_DISCOVERY.md)
4. Update: Documentation when complete

## 📚 External Documentation

### User-Facing (Published)
- `/README.md` - Collection overview
- `/docs/` - Module documentation
- `/docs/CI_CD_INTEGRATION.md` - CI/CD guide
- `/docs/amt_mode_compatibility.md` - AMT mode guide

### Tooling
- `/CLAUDE.md` - Claude Code instructions
- `/CHANGELOG.md` - Version history

## 🔍 Finding Information

### "How do I test this?"
→ [Testing Guide](testing/TESTING.md)

### "What AMT features are available?"
→ [AMT 10 Capabilities](research/AMT_10_CAPABILITIES.md)  
→ [Resource Discovery](research/AMT_RESOURCE_DISCOVERY.md)

### "Why doesn't TLS work?"
→ [AMT TLS Limitation](research/AMT_10_TLS_LIMITATION.md)

### "What's the collection status?"
→ [Collection Status](COLLECTION_STATUS.md)

### "What are the security rules?"
→ [Security Guidelines](testing/SECURITY.md)  
→ `/CLAUDE.md` (Critical Security Standards section)

### "How do I release?"
→ [Release Checklist](testing/RELEASE_CHECKLIST.md)

## 📝 Maintenance

This index should be updated when:
- New documents are added to `development/`
- Document purposes change
- Directory structure changes

Last updated: 2026-05-30
