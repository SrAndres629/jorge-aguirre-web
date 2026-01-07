#!/bin/bash
# cleanup.sh - Residue Cleanup Script

echo "🧹 Starting Jorge Aguirre Web Cleanup..."

# 1. Remove Python cache files
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 2. Remove log files
rm -f *.log
rm -f core/*.log

# 3. Remove non-production assets
rm -f qr_code.png
rm -rf design_assets/
rm -rf raw_images/

# 4. Remove temporary files
rm -f *.tmp

# 5. Remove obsolete database directory (if still exists after core migration)
if [ -d "database" ]; then
    echo "⚠️ Warning: root database directory still exists. Already migrated to /core/database."
    rm -rf database
fi

echo "✅ Cleanup completed successfully!"
