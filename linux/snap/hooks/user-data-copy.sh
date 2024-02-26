#!/bin/bash

# Define the source directories and target directories
SRC_CSV="$SNAP/usr/share/transaction-decorator/csv/allTransactions.csv"
DEST_CSV="$SNAP_DATA/csv/"
SRC_DICT="$SNAP/usr/share/transaction-decorator/dictionary/"
DEST_DICT="$SNAP_DATA/dictionary/"
BACKUP_DIR="$SNAP_DATA/backup/"

# Ensure target directories exist
mkdir -p "$DEST_CSV"
mkdir -p "$DEST_DICT"
mkdir -p "$BACKUP_DIR"

# Copy files
cp "$SRC_CSV" "$DEST_CSV"
cp -r "$SRC_DICT"* "$DEST_DICT"

# Set permissions for the copied files and backup directory
chmod -R +w "$DEST_CSV"
chmod -R +w "$DEST_DICT"
chmod -R +w "$BACKUP_DIR"
