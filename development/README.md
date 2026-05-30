# Development Documentation

This directory contains internal development documentation, research notes, and testing records. **These files are NOT published with the collection.**

## Directory Structure

```
development/
├── README.md                          # This file
├── research/                          # AMT research and discovery
│   ├── AMT_10_CAPABILITIES.md        # AMT 10.0.56 capability testing
│   ├── AMT_10_TLS_LIMITATION.md      # TLS limitations in Small Business Mode
│   ├── AMT_RESOURCE_DISCOVERY.md     # WSMAN resource discovery results
│   ├── CERTIFICATE_MANAGEMENT.md     # Certificate management research
│   └── TLS_TEST_GUIDE.md             # TLS testing guide
├── testing/                           # Testing and validation
│   ├── TESTING.md                    # Testing guide
│   ├── SECURITY.md                   # Security guidelines
│   ├── TEST_PLAN.md                  # Pre-push test plan
│   ├── TEST_RESULTS.md               # Test results
│   └── RELEASE_CHECKLIST.md          # Pre-release checklist
├── COLLECTION_STATUS.md               # Collection development status
├── DOCUMENTATION.md                   # Documentation status
├── DOCUMENTATION_UPDATE_SUMMARY.md    # Doc update history
├── FINAL_SUMMARY.md                   # Final development summary
└── SECURITY_CLEANUP_SUMMARY.md        # Security cleanup record

```

## What Goes Where

### Published with Collection
- `/README.md` - Collection overview and quick start
- `/CHANGELOG.md` - Version history
- `/CLAUDE.md` - Instructions for Claude Code
- `/docs/` - User-facing module documentation and guides

### Development Only (This Directory)
- Research notes and AMT discovery documentation
- Testing procedures and results
- Development status and summaries
- Internal guidelines and checklists

## Using This Documentation

**Contributors:** Reference these docs for:
- Understanding AMT capabilities and limitations
- Following testing procedures before commits
- Learning from research and discovery process
- Checking collection development status

**Users:** See `/docs/` directory and main `/README.md` for user-facing documentation.

## Note on CLAUDE.md

The `/CLAUDE.md` file in the repository root contains persistent instructions for Claude Code. While it's published with the collection, it's clearly marked as tooling-specific and doesn't interfere with user documentation.
