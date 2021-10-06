#!/bin/bash --login
# The --login ensures the bash configuration is loaded,
# enabling Conda.

# Enable strict mode.
set -euo pipefail
# ... Run whatever commands ...

# Temporarily disable strict mode and activate conda:
set +euo pipefail
# conda activate /opt/env

# Re-enable strict mode:
set -euo pipefail

# exec the final command:
exec echo "Usage: python3 dn_nifti.py <project ID>"
exec echo "Or: python3 nifti2bids.py <project ID>"
exec echo "Make sure your working.lst is in your scripts directory and up to date."