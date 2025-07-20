#!/bin/bash

# Social Media Management Bot - Database Backup Script
# This script creates automated backups of the PostgreSQL database

set -e  # Exit on any error

# Configuration from environment variables
DB_HOST="${POSTGRES_HOST:-postgres}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-socialmedia_db}"
DB_USER="${POSTGRES_USER:-postgres}"
BACKUP_DIR="${BACKUP_STORAGE_PATH:-/backups}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Generate timestamp for backup filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/socialmedia_bot_backup_$TIMESTAMP.sql"
BACKUP_FILE_COMPRESSED="$BACKUP_FILE.gz"

echo "Starting database backup at $(date)"
echo "Backup file: $BACKUP_FILE_COMPRESSED"

# Create database backup
PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --verbose \
    --no-password \
    --format=custom \
    --no-owner \
    --no-privileges > "$BACKUP_FILE"

# Compress the backup
gzip "$BACKUP_FILE"

# Verify backup was created successfully
if [ -f "$BACKUP_FILE_COMPRESSED" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE_COMPRESSED" | cut -f1)
    echo "Backup completed successfully: $BACKUP_FILE_COMPRESSED ($BACKUP_SIZE)"
else
    echo "ERROR: Backup file was not created"
    exit 1
fi

# Clean up old backups (keep only last N days)
echo "Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "socialmedia_bot_backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete

# List remaining backups
echo "Available backups:"
ls -lh "$BACKUP_DIR"/socialmedia_bot_backup_*.sql.gz 2>/dev/null || echo "No backups found"

echo "Backup process completed at $(date)"

# Optional: Upload to cloud storage (uncomment and configure as needed)
# aws s3 cp "$BACKUP_FILE_COMPRESSED" s3://your-backup-bucket/database-backups/
# gsutil cp "$BACKUP_FILE_COMPRESSED" gs://your-backup-bucket/database-backups/