bind = '127.0.0.1:8000'

workers = 4

debug = False


# Logging 
loglevel = 'info'
errorlog = './logs/gunicorn.error.log'
accesslog = './logs/gunicorn.access.log'

enable_stdio_inheritance = True