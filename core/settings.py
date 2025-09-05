import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------
# SECURITY SETTINGS
# ------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-secret-key")  # fallback for local dev
DEBUG = os.getenv("DEBUG", "False") == "True"

# Render gives you a free subdomain like myapp.onrender.com
ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".onrender.com"]

# ------------------------------
# DATABASE
# ------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default="postgresql://postgres:postgres@localhost:5432/postgres",  # local fallback
        conn_max_age=600,
    )
}

# ------------------------------
# STATIC FILES
# ------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# WhiteNoise for serving static files
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # 👈 add this line just after SecurityMiddleware
    # ... keep existing middleware below
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# WhiteNoise settings (compressed static files)
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
