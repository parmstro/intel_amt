#!/bin/bash
# Run integration tests with vault

set -e

COLLECTION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VAULT_PASS_FILE="${COLLECTION_DIR}/.vault_password"

if [ ! -f "$VAULT_PASS_FILE" ]; then
    echo "Error: Vault password file not found: $VAULT_PASS_FILE"
    echo "Create it with: echo 'your_password' > .vault_password && chmod 600 .vault_password"
    exit 1
fi

echo "Running integration tests for parmstro.intel_amt collection"
echo "============================================================"

cd "$COLLECTION_DIR"

# Run the integration test playbook
ansible-playbook tests/integration/targets/amt_power/tasks/main.yml \
    --vault-password-file="$VAULT_PASS_FILE" \
    -e @tests/integration/integration_config.yml \
    -v

echo ""
echo "Integration tests completed successfully!"
