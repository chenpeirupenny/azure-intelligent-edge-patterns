"""Django settings for vision_on_edge project.

Generated by 'django-admin startproject' using Django 3.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from pathlib import Path

import config
from configs import logging_config
from configs.customvision_config import ENDPOINT, TRAINING_KEY

# Mimic cookie-cutter django
ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

# Project root
PROJECT_ROOT = ROOT_DIR / "vision_on_edge"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "gjfeo_pt@1$23c$*g8to4bewom59sml0%8fgbdgot=ypr84b$@"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "channels",
    "vision_on_edge.streams",
    "vision_on_edge.azure_settings",
    "vision_on_edge.azure_projects",
    "vision_on_edge.azure_training_status",
    "vision_on_edge.notifications",
    "vision_on_edge.azure_parts",
    "vision_on_edge.images",
    "vision_on_edge.cameras",
    "vision_on_edge.inference_modules",
    "vision_on_edge.azure_part_detections",
    "vision_on_edge.feedback",
    "vision_on_edge.locations",
    "vision_on_edge.camera_tasks",
    "vision_on_edge.prediction_modules",
    #    'vision_on_edge.image_predictions',
    "vision_on_edge.azure_pd_deploy_status",
    "rest_framework",
    "drf_yasg2",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # 'django.middleware.csrf.CsrfViewMiddleware',
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "configs.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

CORS_ORIGIN_ALLOW_ALL = True

ASGI_APPLICATION = "configs.routing.application"

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(ROOT_DIR, "db.sqlite3"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

UI_DIR = PROJECT_ROOT / "ui_production"
STATICFILES_DIRS = [UI_DIR / "static"]

STATIC_URL = "/static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = PROJECT_ROOT / "media"

ICON_URL = "/icons/"
ICON_ROOT = UI_DIR / "icons"

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "vision_on_edge.general.api.exception_handlers.ms_style_exception_handler"
}

IOT_HUB_CONNECTION_STRING = config.IOT_HUB_CONNECTION_STRING
DEVICE_ID = config.DEVICE_ID
MODULE_ID = config.MODULE_ID

print("************************************")
print("CONFIGURATION:")
print("  TRAINING_KEY:", TRAINING_KEY)
print("  ENDPOINT:", ENDPOINT)
print("************************************")

LOGGING = logging_config.LOGGING_CONFIG_PRODUCTION
