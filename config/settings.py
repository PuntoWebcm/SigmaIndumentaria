import os
from pathlib import Path
import dj_database_url

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración de seguridad (¡No compartir en producción!)
SECRET_KEY = 'django-insecure-k7a54io&2)*!*vmm@$0^u-v*w!+(#%-isb*-blk=@(1c@65p!p'

DEBUG = True

ALLOWED_HOSTS = []

# Definición de aplicaciones
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'products',
    'cart',
    'orders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Conecta el carrito con todos los templates
                'cart.context_processors.cart', 
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Configuración de Base de Datos
DATABASES = {
    'default': dj_database_url.config(
        # Si existe la variable DATABASE_URL (en Render), la usa.
        # Si no existe (en tu PC), usa SQLite por defecto.
        default=os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600
    )
}

# Validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Configuración de idioma y hora (Argentina)
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

# Archivos estáticos (CSS, JavaScript, Imágenes de diseño)
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')] # Asegúrate de tener una carpeta 'static' en la raíz

# Archivos multimedia (Fotos de productos cargadas desde el Admin)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- CONFIGURACIÓN CRÍTICA DEL CARRITO ---
CART_SESSION_ID = 'cart'
SESSION_SAVE_EVERY_REQUEST = True  # Obliga a Django a guardar la sesión en cada cambio
SESSION_COOKIE_AGE = 86400         # El carrito dura 24 horas
SESSION_EXPIRE_AT_BROWSER_CLOSE = False # No se borra al cerrar el navegador

# Tipo de campo por defecto para IDs
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
