#!/bin/bash
set -e

# Install the .deb package
echo "Installing the .deb package..."
sudo apt-get update
sudo apt-get install -y --no-install-recommends /tmp/package/*.deb || {
    echo "Failed to install the package. Checking dependencies..."
    sudo apt-get install -f -y
    sudo apt-get install -y --no-install-recommends /tmp/package/*.deb
}

echo "Package installed successfully"

# List installed files
echo "Files installed by the package:"
dpkg -L millisecond

echo "Starting millisecond application with Wayland..."
echo "The application window should appear on your desktop."
echo "Press Ctrl+C to exit when done testing."

# Run the application
millisecond

# If the app exits normally, we'll reach here
echo "Application exited."
