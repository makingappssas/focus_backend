import environ

env = environ.Env()
environ.Env.read_env()

POSTGRESQL={
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DATABASES_NAME'),
        'USER': env('DATABASES_USER'),
        'PASSWORD':env('DATABASES_PASSWORD'),
        'HOST':env('DATABASES_HOST'),
        'PORT': '5432'
    },
    
    'db2': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DATABASES_NAME_2'),
        'USER': env('DATABASES_USER'),
        'PASSWORD':env('DATABASES_PASSWORD_2'),
        'HOST':env('DATABASES_HOST_2'),
        'PORT': '5432'
    }
}