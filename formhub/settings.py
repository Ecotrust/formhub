# vim: set fileencoding=utf-8

import os
import subprocess
import sys

from pymongo import MongoClient

import djcelery
djcelery.setup_loader()

CURRENT_FILE = os.path.abspath(__file__)
PROJECT_ROOT = os.path.realpath(
    os.path.join(os.path.dirname(CURRENT_FILE), '..'))
PRINT_EXCEPTION = False

DEBUG = True
TEMPLATE_DEBUG = DEBUG
TEMPLATED_EMAIL_TEMPLATE_DIR = 'templated_email/'

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

ugettext = lambda s: s

LANGUAGES = (
    ('fr', u'Français'),
    ('en', u'English'),
    ('es', u'Español'),
    ('it', u'Italiano'),
    ('km', u'ភាសាខ្មែរ'),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = 'http://localhost:8000/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

#ENKETO URL
ENKETO_URL = 'https://enketo.formhub.org/'
ENKETO_API_SURVEY_PATH = '/api_v1/survey'
ENKETO_API_INSTANCE_PATH = '/api_v1/instance'
ENKETO_PREVIEW_URL = ENKETO_URL + 'webform/preview'
ENKETO_API_TOKEN = ''

# Login URLs
LOGIN_URL = '/accounts/login/'
#LOGIN_REDIRECT_URL = '/login_redirect/'
LOGIN_REDIRECT_URL = '/app/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
# Make this unique, and don't share it with anybody.
SECRET_KEY = 'mlfs33^s1l4xf6a36$0#j%dd*sisfoi&)&4s-v=91#^l01v)*j'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',
    'utils.middleware.LocaleMiddlewareWithTweaks',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'utils.middleware.HTTPResponseNotAllowedMiddleware',
)

LOCALE_PATHS = (os.path.join(PROJECT_ROOT, 'formhub', 'locale'), )

ROOT_URLCONF = 'formhub.urls'
USE_TZ = True


TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
    # Put strings here, like "/home/html/django_templates"
    # or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# needed by guardian
ANONYMOUS_USER_ID = -1

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'registration',
    'south',
    'django_nose',
    'django_digest',
    'corsheaders',
    'rest_framework',
    'rest_framework_swagger',
    'rest_framework.authtoken',
    'odk_logger',
    'odk_viewer',
    'main',
    'restservice',
    'staff',
    'api',
    'guardian',
    'djcelery',
    'stats',
    'sms_support',
)

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
    'rest_framework.serializers.HyperlinkedModelSerializer',

    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        #'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

SWAGGER_SETTINGS = {
    "exclude_namespaces": [],    # List URL namespaces to ignore
    "api_version": '1.0',  # Specify your API's version (optional)
    "enabled_methods": [         # Methods to enable in UI
        'get',
        'post',
        'put',
        'patch',
        'delete'
    ],
}

CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = (
    'dev.formhub.org',
)

USE_THOUSAND_SEPARATOR = True

COMPRESS = True

# extra data stored with users
AUTH_PROFILE_MODULE = 'main.UserProfile'

# case insensitive usernames
AUTHENTICATION_BACKENDS = (
    'main.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

# Settings for Django Registration
ACCOUNT_ACTIVATION_DAYS = 1

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s' +
                      ' %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'audit': {
            'level': 'DEBUG',
            'class': 'utils.log.AuditLogHandler',
            'formatter': 'verbose',
            'model': 'main.models.audit.AuditLog'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'console_logger': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        },
        'audit_logger': {
            'handlers': ['audit'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}

MONGO_DATABASE = {
    'HOST': 'localhost',
    'PORT': 27017,
    'NAME': 'formhub',
    'USER': '',
    'PASSWORD': ''
}

GOOGLE_STEP2_URI = 'http://formhub.org/gwelcome'
GOOGLE_CLIENT_ID = '617113120802.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '9reM29qpGFPyI8TBuB54Z4fk'

THUMB_CONF = {
    'large': {'size': 1280, 'suffix': '-large'},
    'medium': {'size': 640, 'suffix': '-medium'},
    'small': {'size': 240, 'suffix': '-small'},
}
# order of thumbnails from largest to smallest
THUMB_ORDER = ['large', 'medium', 'small']
IMG_FILE_TYPE = 'jpg'

# celery
BROKER_BACKEND = "rabbitmq"
BROKER_URL = 'amqp://guest:guest@localhost:5672/'
CELERY_RESULT_BACKEND = "amqp"  # telling Celery to report results to RabbitMQ
CELERY_ALWAYS_EAGER = False

# auto add crowdform to new registration
AUTO_ADD_CROWDFORM = False
DEFAULT_CROWDFORM = {'xform_username': 'bob', 'xform_id_string': 'transport'}

# duration to keep zip exports before deletio (in seconds)
ZIP_EXPORT_COUNTDOWN = 3600  # 1 hour

# default content length for submission requests
DEFAULT_CONTENT_LENGTH = 10000000

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--with-fixture-bundling']
#NOSE_PLUGINS = [
#    'utils.nose_plugins.SilenceSouth'
#]

TESTING_MODE = False
if len(sys.argv) >= 2 and (sys.argv[1] == "test" or sys.argv[1] == "test_all"):
    # This trick works only when we run tests from the command line.
    TESTING_MODE = True
else:
    TESTING_MODE = False

if TESTING_MODE:
    MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'test_media/')
    subprocess.call(["rm", "-r", MEDIA_ROOT])
    MONGO_DATABASE['NAME'] = "formhub_test"
    # need to have CELERY_ALWAYS_EAGER True and BROKER_BACKEND as memory
    # to run tasks immediately while testing
    CELERY_ALWAYS_EAGER = True
    BROKER_BACKEND = 'memory'
    ENKETO_API_TOKEN = 'abc'
    #TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'
else:
    MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media/')

if PRINT_EXCEPTION and DEBUG:
    MIDDLEWARE_CLASSES += ('utils.middleware.ExceptionLoggingMiddleware',)

# re-captcha in registrations
REGISTRATION_REQUIRE_CAPTCHA = False
RECAPTCHA_USE_SSL = False
RECAPTCHA_PRIVATE_KEY = ''
RECAPTCHA_PUBLIC_KEY = '6Ld52OMSAAAAAJJ4W-0TFDTgbznnWWFf0XuOSaB6'

ENKETO_API_INSTANCE_IFRAME_URL = "https://enketo-dev.formhub.org/api_v1/instance/iframe"
ENKETO_API_TOKEN = "---"

################################################################################
# AK Logbook specific settings
AK_LOGBOOK_SURVEY = "frp_awc_survey"
FIELD_MAP = {
    'obs_name': "general/obs_nm",
    'date': "general/obs_date",
    'permit_num': "general/perm_num",
    'species': "general/sps_name",
    'species_group': "general/sps_grp",
    'awc_num': "awc/awc_num",
    'waterway': "general/wtr_nm",
    'name_type': "general/name_type",
    'observation_type': "awc/observ",
    "fishcollectionmethod": "frp/gear_type",
    "lifestage": "frp/Lf_stg",
    "length": "frp/lngth",
    "lengthmethod": "frp/lngth_md",
    "weight": "frp/wt",
    "sex": "frp/sex",
    "age": "frp/age",
    "agemethod": "frp/age_md",
    "gcl": "frp/gcl",
    "add_cnt1": "frp/add_cnt1",
    "disp1": "frp/disp1",
    "add_cnt2": "frp/add_cnt2",
    "disp2": "frp/disp2",
    "comments": "frp/frp_comm",
}

IGNORED_OUTPUT_FIELDS = [
    "formhub/uuid",
    "meta/instanceID",
    "_xform_id_string",
    "meta/deprecatedID",
    "awc/show_awc",
    "frp/show_frp",
    "general2/req_edit"
]

SHOW_FRP_KEY = 'frp/show_frp'

SHOW_AWC_KEY = 'awc/show_awc'

FRP_LOCATION_KEY = 'frp/obs_loc'

AWC_START_POINT_KEY = 'awc/wtr_st'

AWC_END_POINT_KEY = 'awc/wtr_end'

PHOTO_KEY = 'general/pics'

COMMENT_KEY = 'awc/awc_comm'

################################################################################
# Yukon Logbook specific settings

YUKON_WATER_SURVEY = "yukon_water"
YUKON_FIELD_MAP = {
    'site_id': {
        'name':"general/site_id",
        'label': "Site Name ID"
    },
    'obs_name':{
        'name': "general/tech_name",
        'label': "Technician(s)"
    },
    'date':{
        'name': "general/date",
        'label': "Date"
    },
    'start_time':{
        'name': 'general/st_time',
        'label': "Time (24 hrs)"
    },
    'water_body':{
        'name': 'general/wtr_bdy',
        'label': "Waterbody Name"
    },
    'meter_type':{
        'name': 'general/meter',
        'label': "Meter type"
    },
    'meter_id':{
        'name': 'general/meter_id',
        'label': "Meter ID #"
    },
    'ph7_buffer':{
        'name': 'ph_calibration/ph7_buffer',
        'label': "pH 7 Buffer Reading"
    },
    'ph7_buffer_temp':{
        'name': 'ph_calibration/ph7_buffer_tmp',
        'label': "pH 7 Buffer Temperature"
    },
    'ph10_buffer':{
        'name': 'ph_calibration/ph10_buffer',
        'label': "pH 10 Buffer Reading"
    },
    'ph10_buffer_temp':{
        'name': 'ph_calibration/ph10_buffer_tmp',
        'label': "pH 10 Buffer Temperature"
    },
    'bar_pressure':{
        'name': 'do_calibration/bar_pressure',
        'label': "Barometric Pressure"
    },
    'pressure_hg':{
        'name': 'do_calibration/us_note',
        'label': "air pressure in inHg"
    },
    'pressure_kpa':{
        'name': 'do_calibration/ca_note',
        'label': "air pressure in kPa"
    },
    'pct_do_saturation':{
        'name': 'do_calibration/do_reading_sat',
        'label': "DO Reading (%) Saturation"
    },
    'do_reading':{
        'name': 'do_calibration/do_reading',
        'label': "DO Reading"
    },
    'conductivity_standard':{
        'name': 'con_calibration/con_standard',
        'label': "Conductivity Standard Used"
    },
    'conductivity_reading':{
        'name': 'con_calibration/con_read',
        'label': "Conductivity Reading"
    },
    'conductivity_soln_temp':{
        'name': 'con_calibration/con_temp',
        'label': "Conductivity Solution Temperature"
    },
    'ph':{
        'name': 'field/ph',
        'label': "pH"
    },
    'dissolved_o_pct':{
        'name': 'field/dssvld_o_perc',
        'label': "Dissolved Oxygen (%)"
    },
    'dissolved_oxygen':{
        'name': 'field/dssvld_o',
        'label': "Dissolved Oxygen"
    },
    'conductivity':{
        'name': 'field/conduct',
        'label': "Conductivity"
    },
    'air_temp':{
        'name': 'field/air_temp',
        'label': "Air Temperature"
    },
    'water_temp':{
        'name': 'field/wtr_temp',
        'label': "Water Temperature"
    },
    'ice_thickness':{
        'name': 'field/ice',
        'label': "Ice Thickness"
    },
    'coordinates':{
        'name': 'field/gps_loc',
        'label': "Location"
    },
    'include_oth_obs':{
        'name': 'field_cond/show_field',
        'label': "Would like to include other observations about weather and river conditions?"
    },
    'current_weather':{
        'name': 'field_cond/weather_current',
        'label': "Current weather"
    },
    'weather_last_24hrs':{
        'name': 'field_cond/weather_24',
        'label': "Weather in the last 24 hours"
    },
    'sample_location':{
        'name': 'field_cond/sample_loc',
        'label': "Sample Location"
    },
    'flow_description':{
        'name': 'field_cond/flow_desc',
        'label': "Flow Description"
    },
    'water_clarity':{
        'name': 'field_cond/wtr_clrty',
        'label': "Water Clarity"
    },
    'odor':{
        'name': 'field_cond/odor',
        'label': "Site Odor"
    },
    'odor_oth_description':{
        'name': 'field_cond/odor_other',
        'label': "describe other"
    },
    'river_other':{
        'name': 'field_cond/riv_other_info',
        'label': "Other information"
    },
    'river_change':{
        'name': 'field_cond/riv_change',
        'label': "Changes with the river since last sample"
    },
    'river_height_2weeks':{
        'name': 'field_cond/riv_hght_2w',
        'label': "How does the river height compare to two weeks ago?"
    },
    'river_height_1year':{
        'name': 'field_cond/riv_height_lyear',
        'label': "How does the river height compare to this time last year?"
    },
    'weather_notes':{
        'name': 'field_cond/weather_note',
        'label': "Anything noteworthy happening with the weather?"
    },
    'wildlife_concern':{
        'name': 'field_cond/wildlife_concern',
        'label': "Any specific concerns about wildlife?"
    },
    'wildlife_note':{
        'name': 'field_cond/wildlife_note',
        'label': "Any noteworthy wildlife or fish species traveling through your community or nearby?"
    },
    'contaminate_events':{
        'name': 'field_cond/contaminants1',
        'label': "Has anything occurred since the last sampling that might have affected the water quality at your site?"
    },
    'other_site_req':{
        'name': 'field_cond/contaminants2',
        'label': "Is there any other site that your community wants monitored? Please describe:"
    },
    'interesting_notes':{
        'name': 'field_cond/other_info1',
        'label': "Anything else interesting? Please write your comments or observations"
    },
    'sample_issues':{
        'name': 'field_cond/other_info2',
        'label': "Are there any issues with this sample that we should know about?"
    }
}

YUKON_IGNORED_OUTPUT_FIELDS = []

YUKON_LOCATION_KEY = 'field/gps_loc'

################################################################################

try:
    from local_settings import *
except ImportError:
    print("You can override the default settings by adding a "
          "local_settings.py file.")

# MongoDB
if MONGO_DATABASE.get('USER') and MONGO_DATABASE.get('PASSWORD'):
    MONGO_CONNECTION_URL = (
        "mongodb://%(USER)s:%(PASSWORD)s@%(HOST)s:%(PORT)s") % MONGO_DATABASE
else:
    MONGO_CONNECTION_URL = "mongodb://%(HOST)s:%(PORT)s" % MONGO_DATABASE

MONGO_CONNECTION = MongoClient(
    MONGO_CONNECTION_URL, safe=True, j=True, tz_aware=True)
MONGO_DB = MONGO_CONNECTION[MONGO_DATABASE['NAME']]

# Clear out the test database
if TESTING_MODE:
    MONGO_DB.instances.drop()
