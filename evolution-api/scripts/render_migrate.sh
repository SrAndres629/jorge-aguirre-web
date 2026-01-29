#!/bin/bash
# -----------------------------------------------------------------------------
# MASTER PROTOCOL: SUPABASE SYNC
# -----------------------------------------------------------------------------
# This script executes the forced schema push to Supabase.
# It uses 'npx prisma migrate deploy' which is safer than 'db push' for production.
# 
# MANUAL EXECUTION INSTRUCTIONS:
# 1. Go to Render Dashboard -> evolution-whatsapp -> Shell
# 2. Copy and paste the command below:

echo "🚀 Starting Master Schema Sync to Supabase..."
npx prisma migrate deploy --schema=./prisma/postgresql-schema.prisma

if [ $? -eq 0 ]; then
  echo "✅ SCHEMA SYNC SUCCESSFUL. Database is now in sync."
  echo "👉 ACTION: Restart the service now."
else
  echo "❌ SYNC FAILED. Check your DATABASE_URL variable."
fi
