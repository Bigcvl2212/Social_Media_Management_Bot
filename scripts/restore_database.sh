#!/bin/bash

# Social Media Management Bot - Database Restore Script
# This script restores the PostgreSQL database from a backup

set -e  # Exit on any error

# Configuration from environment variables
DB_HOST="${POSTGRES_HOST:-postgres}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-socialmedia_db}"
DB_USER="${POSTGRES_USER:-postgres}"
BACKUP_DIR="${BACKUP_STORAGE_PATH:-/backups}"

# Function to display usage
usage() {
    echo "Usage: $0 [BACKUP_FILE]"
    echo ""
    echo "BACKUP_FILE: Path to the backup file to restore (optional)"
    echo "            If not provided, will list available backups for selection"
    echo ""
    echo "Examples:"
    echo "  $0 /backups/socialmedia_bot_backup_20231220_143000.sql.gz"
    echo "  $0  # Interactive mode to select from available backups"
    exit 1
}

# Function to list available backups
list_backups() {
    echo "Available backup files:"
    echo "======================"
    local backups=($(ls -t "$BACKUP_DIR"/socialmedia_bot_backup_*.sql.gz 2>/dev/null || true))
    
    if [ ${#backups[@]} -eq 0 ]; then
        echo "No backup files found in $BACKUP_DIR"
        exit 1
    fi
    
    for i in "${!backups[@]}"; do
        local backup="${backups[$i]}"
        local size=$(du -h "$backup" | cut -f1)
        local date=$(date -r "$backup" '+%Y-%m-%d %H:%M:%S')
        printf "%2d) %s (%s) - %s\n" $((i+1)) "$(basename "$backup")" "$size" "$date"
    done
    
    echo ""
    echo -n "Select backup number (1-${#backups[@]}): "
    read -r selection
    
    if [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -le ${#backups[@]} ]; then
        BACKUP_FILE="${backups[$((selection-1))]}"
    else
        echo "Invalid selection"
        exit 1
    fi
}

# Parse command line arguments
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
fi

BACKUP_FILE="$1"

# If no backup file provided, show interactive selection
if [ -z "$BACKUP_FILE" ]; then
    list_backups
fi

# Verify backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file '$BACKUP_FILE' not found"
    exit 1
fi

echo "Starting database restore at $(date)"
echo "Backup file: $BACKUP_FILE"
echo "Target database: $DB_NAME on $DB_HOST:$DB_PORT"

# Warning prompt
echo ""
echo "WARNING: This will completely replace the current database!"
echo "Make sure you have a current backup before proceeding."
echo ""
echo -n "Do you want to continue? (yes/no): "
read -r confirmation

if [ "$confirmation" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

# Create a backup of current database before restore
CURRENT_BACKUP="$BACKUP_DIR/pre_restore_backup_$(date +"%Y%m%d_%H%M%S").sql.gz"
echo "Creating backup of current database: $CURRENT_BACKUP"

PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --no-password \
    --format=custom \
    --no-owner \
    --no-privileges | gzip > "$CURRENT_BACKUP"

echo "Current database backed up successfully"

# Drop and recreate database
echo "Dropping and recreating database..."
PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME;"

# Restore from backup
echo "Restoring database from backup..."
if [[ "$BACKUP_FILE" == *.gz ]]; then
    # Compressed backup
    gunzip -c "$BACKUP_FILE" | PGPASSWORD="$POSTGRES_PASSWORD" pg_restore \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --verbose \
        --no-password \
        --no-owner \
        --no-privileges
else
    # Uncompressed backup
    PGPASSWORD="$POSTGRES_PASSWORD" pg_restore \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --verbose \
        --no-password \
        --no-owner \
        --no-privileges \
        "$BACKUP_FILE"
fi

echo "Database restore completed successfully at $(date)"
echo "Pre-restore backup saved as: $CURRENT_BACKUP"

# Verify restore
echo "Verifying database connection..."
PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT current_database(), version();" > /dev/null

echo "Database verification successful"
echo "Restore process completed successfully!"