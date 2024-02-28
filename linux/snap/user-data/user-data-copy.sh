#!/bin/bash

# Define the source directories and target directories
SRC_CSV="$SNAP/usr/share/transaction-decorator/csv/allTransactions.csv"
DEST_CSV="$SNAP_USER_DATA/csv/"

SRC_DICT="$SNAP/usr/share/transaction-decorator/dictionary/"
DEST_DICT="$SNAP_USER_DATA/dictionary/"

BACKUP_DIR="$SNAP_USER_DATA/backup/"

echo "Ensure target directories exist"
mkdir -p "$DEST_CSV"
mkdir -p "$DEST_DICT"

echo "Creating backup directory $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

echo "Set permissions for the copied files and backup directory"
chmod -R +w "$DEST_CSV"
chmod -R +w "$DEST_DICT"
chmod -R +w "$BACKUP_DIR"

echo "Copying from $SRC_CSV to $DEST_CSV"
cp "$SRC_CSV" "$DEST_CSV"

echo "Copying from $SRC_DICT to $DEST_DICT"
cp -r "$SRC_DICT"* "$DEST_DICT"
