#!/bin/bash

# Run: sudo bash build_wifite_gui_full.sh

# Root check
if [ "$EUID" -ne 0 ]; then
  echo "Please run the script with sudo"
  exit
fi

echo "=== Wifite2 GUI Builder (fork d3ad0x1) ==="

# Determine the user to ensure correct paths
USERNAME=$(logname)

# Project directory
PROJECT_DIR="/home/$USERNAME/wifite_gui"
mkdir -p "$PROJECT_DIR"

# Install system dependencies
echo "Installing system dependencies..."
apt update
apt install -y python3 python3-tk python3-pip git iw net-tools wifite

# Clone or update the d3ad0x1 fork
echo "Downloading the d3ad0x1 Wifite2 fork..."
cd "$PROJECT_DIR"
if [ -d "wifite2" ]; then
    echo "Wifite2 already exists, updating..."
    cd wifite2
    git pull
else
    git clone https://github.com/d3ad0x1/wifite2.git
fi

# Copy the local GUI script from the repository
REPO_DIR="$(pwd)/../"  # It is assumed that the script is located in the repository root
if [ -f "$REPO_DIR/wifite_gui.py" ]; then
    cp "$REPO_DIR/wifite_gui.py" "$PROJECT_DIR/wifite_gui.py"
    echo "GUI script copied to $PROJECT_DIR/wifite_gui.py"
else
    echo "Error: wifite_gui.py not found in the repository root"
    exit 1
fi

# Create a .desktop file for the applications menu
DESKTOP_FILE="/home/$USERNAME/.local/share/applications/wifite_gui.desktop"
mkdir -p "$(dirname $DESKTOP_FILE)"
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=Wifite2 GUI
Comment=Graphical interface for Wifite2 (d3ad0x1 fork)
Exec=sudo python3 $PROJECT_DIR/wifite_gui.py
Icon=network-wireless
Terminal=true
Type=Application
Categories=Network;Security;
StartupNotify=true
EOF

update-desktop-database "/home/$USERNAME/.local/share/applications"

echo "=== Installation completed ==="
echo "Project location: $PROJECT_DIR"
echo "GUI script: $PROJECT_DIR/wifite_gui.py"
echo "Run the GUI:"
echo "sudo python3 $PROJECT_DIR/wifite_gui.py"
echo "Or via the Applications menu (Wifite2 GUI)"
echo "Done! Enjoy the GUI for Wifite2 (d3ad0x1 fork)."
