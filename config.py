import os
import secrets


class AppConfig:
    DEBUG = os.getenv("FORGE3D_DEBUG", "false").lower() == "true"
    HOST = os.getenv("FORGE3D_HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", os.getenv("FORGE3D_PORT", "5000")))
    SECRET_KEY = os.getenv("FORGE3D_SECRET_KEY") or secrets.token_hex(32)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
