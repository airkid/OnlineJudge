from settings import *

DEBUG = True

TEST_RUNNER = 'legacy.utils.ManagedModelTestRunner'

DATABASE_ROUTERS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(HERE, 'test.db'),
    },
}
