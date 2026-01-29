const { Client } = require('pg');

// Single Socket: Force Cleanup Script
// This script runs before the start script to kill zombie sessions in Postgres.
// PREVENTS: "Conflict: Replaced" error in Render/Kubernetes.

const DB_URI = process.env.DATABASE_URL;
if (!DB_URI) {
    console.warn("⚠️ NO DATABASE_URL detected. Skipping cleanup.");
    process.exit(0);
}

const client = new Client({
    connectionString: DB_URI,
    ssl: { rejectUnauthorized: false } // Required for Render/Neon
});

async function cleanOrphanSessions() {
    try {
        await client.connect();

        console.log("🧹 [MAINTENANCE] Searching for orphan sessions...");

        // 1. Delete instances marked as 'connecting' or 'open' from previous unpredictable restarts
        // We only want to start FRESH. "qrcode" does not exist in Instance table, avoiding error.
        const query = `
            UPDATE "Instance"
            SET "connectionStatus" = 'close'
            WHERE "connectionStatus" IN ('open', 'connecting');
        `;

        const res = await client.query(query);

        if (res.rowCount > 0) {
            console.log(`✅ [CLEANUP] Reset ${res.rowCount} stuck instances to 'close'.`);
        } else {
            console.log("✨ [CLEANUP] No orphan sessions found. System is clean.");
        }

    } catch (err) {
        console.error("❌ [ERROR] Cleanup failed:", err.message);
        // Do not crash the build, just warn
    } finally {
        await client.end();
        console.log("🔒 [MAINTENANCE] Cleanup sequence finished.");
    }
}

cleanOrphanSessions();
