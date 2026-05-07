#!/bin/bash
#
# Build a .deb that bundles a self-contained PyInstaller binary.
# The packaged app does NOT depend on the host system's Python or
# any python3-* apt packages — Python and every runtime dep are
# embedded inside the binary by PyInstaller. This matches the
# Windows installer and macOS .dmg builds, so the user gets the
# exact same pinned dep versions on every platform.
#
# Run from the project root:
#   bash linux/createDebFile.sh
#
# Prerequisites on the build host:
#   - python3, pip, venv
#   - dpkg-deb
set -euo pipefail

PROJECT_ROOT="$(pwd)"
PACKAGE_NAME="transaction-decorator"
PACKAGE_VERSION="1.0.1"
BUILD_DIR="$PROJECT_ROOT/build/$PACKAGE_NAME"
FINAL_DEB="$PROJECT_ROOT/build/${PACKAGE_NAME}_${PACKAGE_VERSION}.deb"
DIST_DIR="$PROJECT_ROOT/dist-linux"

# 1. Build the PyInstaller binary in an isolated venv (clean rebuild).
echo "==> Building PyInstaller binary in isolated venv..."
rm -rf /tmp/td-build-venv "$DIST_DIR"
python3 -m venv /tmp/td-build-venv
/tmp/td-build-venv/bin/pip install --upgrade pip
/tmp/td-build-venv/bin/pip install . pyinstaller
/tmp/td-build-venv/bin/pyinstaller --clean --distpath "$DIST_DIR" "$PROJECT_ROOT/TransactionDecorator.spec"

PYI_BINARY="$DIST_DIR/TransactionDecorator"
if [ ! -f "$PYI_BINARY" ]; then
    echo "ERROR: PyInstaller did not produce $PYI_BINARY" >&2
    exit 1
fi

# 2. Lay out the .deb directory tree.
echo "==> Staging deb tree at $BUILD_DIR..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/lib/$PACKAGE_NAME"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/$PACKAGE_NAME/dictionary"
mkdir -p "$BUILD_DIR/usr/share/$PACKAGE_NAME/csv"
mkdir -p "$BUILD_DIR/usr/share/$PACKAGE_NAME/backup"

# 3. Copy the self-contained binary + assets.
install -m 0755 "$PYI_BINARY" "$BUILD_DIR/usr/lib/$PACKAGE_NAME/TransactionDecorator"
cp -r "$PROJECT_ROOT/icons" "$BUILD_DIR/usr/lib/$PACKAGE_NAME/"
cp -r "$PROJECT_ROOT/dictionary/." "$BUILD_DIR/usr/share/$PACKAGE_NAME/dictionary/"
if [ -f "$PROJECT_ROOT/csv/allTransactions.csv" ]; then
    cp "$PROJECT_ROOT/csv/allTransactions.csv" "$BUILD_DIR/usr/share/$PACKAGE_NAME/csv/"
fi

# 4. Launcher script in /usr/bin.
cat > "$BUILD_DIR/usr/bin/$PACKAGE_NAME" << EOF
#!/bin/bash
exec /usr/lib/$PACKAGE_NAME/TransactionDecorator "\$@"
EOF
chmod +x "$BUILD_DIR/usr/bin/$PACKAGE_NAME"

# 5. DEBIAN/control — only system-level libs needed (Qt runtime libs).
#    NO python3-* deps: Python and pip-installed packages are bundled
#    inside the PyInstaller binary.
cat > "$BUILD_DIR/DEBIAN/control" << EOF
Package: $PACKAGE_NAME
Version: $PACKAGE_VERSION
Architecture: amd64
Maintainer: Lukk <luksarna@gmail.com>
Depends: libxcb-xinerama0, libxcb1, libx11-xcb1, libglu1-mesa, libxrender1, libxi6, libxkbcommon0, libxkbcommon-x11-0, libfontconfig1, libdbus-1-3
Description: A tool to decorate financial transactions and analyze them.
 Transaction Decorator imports bank-export CSVs, normalizes them, and
 applies user-defined keyword dictionaries to assign categories and
 labels. Self-contained — bundles its own Python interpreter and all
 dependencies.
EOF

# 6. .desktop entry.
cat > "$BUILD_DIR/usr/share/applications/$PACKAGE_NAME.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Transaction Decorator
Exec=/usr/bin/$PACKAGE_NAME
Icon=/usr/lib/$PACKAGE_NAME/icons/logo.png
Categories=Office;Finance;
EOF

# 7. Build the .deb.
mkdir -p "$(dirname "$FINAL_DEB")"
dpkg-deb --build "$BUILD_DIR" "$FINAL_DEB"
echo "==> Package built: $FINAL_DEB"
