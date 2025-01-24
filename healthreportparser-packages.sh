#!/bin/bash

# Update the package list
echo "Updating package list..."
sudo apt-get update

# Install wkhtmltopdf
echo "Installing wkhtmltopdf..."
sudo apt-get install -y wkhtmltopdf

# Install Python packages using pip
echo "Installing Python packages..."
pip install openpyxl pandas xlsx2html imgkit

echo "Installation completed!"

