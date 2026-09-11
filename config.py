import os


class AppConfig:
    DEBUG = os.getenv("FORGE3D_DEBUG", "false").lower() == "true"
    HOST = os.getenv("FORGE3D_HOST", "0.0.0.0")
    PORT = int(os.getenv("FORGE3D_PORT", "5000"))
    SECRET_KEY = os.getenv("FORGE3D_SECRET_KEY", "forge3d-dev-secret")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
