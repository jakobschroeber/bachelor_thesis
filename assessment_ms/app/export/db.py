from app.settings import env, DATABASES


def update_connections():
    DATABASES.update({
        'cassandra': {
            'ENGINE': env('DJANGO_EXPORT_DB_ENGINE'),
            'NAME': env('DJANGO_EXPORT_DB_NAME'),
            'HOST': env('DJANGO_EXPORT_DB_HOST'),
            'OPTIONS': {
                'replication': {
                    'strategy_class': env('DJANGO_EXPORT_DB_REPLICATION_STRATEGY_CLASS'),
                    'replication_factor': int(env('DJANGO_EXPORT_DB_REPLICATION_FACTOR')),
                },
                'connection': {
                    'retry_connect': bool(env('DJANGO_EXPORT_DB_CONNECTION_RETRY_CONNECT')),
                    # + All connection options for cassandra.cluster.Cluster()
                },
                'session': {
                    'default_timeout': int(env('DJANGO_EXPORT_DB_SESSION_DEFAULT_TIMEOUT')),
                    'default_fetch_size': int(env('DJANGO_EXPORT_DB_SESSION_DEFAULT_FETCH_SIZE')),
                    # + All options for cassandra.cluster.Session()
                }
            }
        }
    })