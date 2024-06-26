#!/bin/bash

# Project configuration
PROJECT_ROOT=$(pwd)  # Assumes the script is run from the project root
PACKAGE_NAME="transaction-decorator"
PACKAGE_VERSION="1.0.1"
BUILD_DIR="$PROJECT_ROOT/build/$PACKAGE_NAME"
FINAL_DEB="$PROJECT_ROOT/build/${PACKAGE_NAME}_${PACKAGE_VERSION}.deb"
RESOURCE_DIR="$BUILD_DIR/usr/share/$PACKAGE_NAME"

# Create the directory structure
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/lib"
mkdir -p "$BUILD_DIR/usr/lib/$PACKAGE_NAME"
mkdir -p "$BUILD_DIR/usr/share/applications"

mkdir -p "$RESOURCE_DIR/backup"
mkdir -p "$RESOURCE_DIR/csv"
mkdir -p "$RESOURCE_DIR/dictionary"

# Copy application scripts and resources
cp -r "$PROJECT_ROOT/src/." "$BUILD_DIR/usr/lib/$PACKAGE_NAME/src/"
cp -r "$PROJECT_ROOT/icons/." "$BUILD_DIR/usr/lib/$PACKAGE_NAME/icons/"
cp "$PROJECT_ROOT/csv/allTransactions.csv" "$RESOURCE_DIR/csv/"
cp -r "$PROJECT_ROOT/dictionary/." "$RESOURCE_DIR/dictionary/"

# Create the launcher script in /usr/bin
cat > "$BUILD_DIR/usr/bin/$PACKAGE_NAME" << EOF
#!/bin/bash

# Execute your main Python script
python3 /usr/lib/$PACKAGE_NAME/src/gui.py
EOF
chmod +x "$BUILD_DIR/usr/bin/$PACKAGE_NAME"

# Create the DEBIAN/control file
cat > "$BUILD_DIR/DEBIAN/control" << EOF
Package: $PACKAGE_NAME
Version: $PACKAGE_VERSION
Architecture: all
Maintainer: Lukk <luksarna@gmail.com>
Depends: python3, python3-pandas, python3-numpy, python3-matplotlib, python3-chardet, libxcb-xinerama0, libxcb1, libx11-xcb1, libglu1-mesa, libxrender1, libxi6
Description: A tool to decorate financial transactions and analyze them.
EOF

# Create the .desktop file
cat > "$BUILD_DIR/usr/share/applications/$PACKAGE_NAME.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Transaction Decorator
Exec=/usr/bin/$PACKAGE_NAME
Icon=/usr/lib/$PACKAGE_NAME/icons/logo.png
Categories=Utility;
EOF

# Build the .deb package
dpkg-deb --build "$BUILD_DIR" "$FINAL_DEB"

echo "Package built at $FINAL_DEB"
