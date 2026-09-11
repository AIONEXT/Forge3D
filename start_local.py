"""Soft-run startup for local deployment. Starts the Flask app without requiring any hosted AI API."""
from __future__ import annotations

import os

from app import app


if __name__ == "__main__":
    host = os.getenv("FORGE3D_HOST", "0.0.0.0")
    port = int(os.getenv("FORGE3D_PORT", "5000"))
    debug = os.getenv("FORGE3D_DEBUG", "false").lower() == "true"
    print("Starting Forge3D in soft-run mode...")
    print(f"Host: {host} Port: {port} Debug: {debug}")
    print("AI provider mode: local/offline fallback enabled")
    app.run(host=host, port=port, debug=debug, threaded=True)
