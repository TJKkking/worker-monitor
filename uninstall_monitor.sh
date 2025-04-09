#!/bin/bash

set -e

echo "[INFO] Stopping and disabling worker-monitor.service..."
sudo systemctl stop worker-monitor || true
sudo systemctl disable worker-monitor || true

echo "[INFO] Removing systemd service file..."
sudo rm -f /etc/systemd/system/worker-monitor.service

echo "[INFO] Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "[INFO] Deleting monitor files..."
sudo rm -rf /opt/worker-monitor

echo "[INFO] ✅ Monitor uninstalled successfully!"
