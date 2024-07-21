import jwt
import datetime


dt = datetime.datetime.now() + datetime.timedelta(days=1)
secret_code = 'django-insecure-snvk*#y805$!7_u$l$(jmz&wdcf=s=20sjqbo%(d7r3h5f%e%8'

token = jwt.encode(
    {
        'username': 'admin',
        'exp': int(dt.strftime('%s'))
    },
    secret_code,
    algorithm='HS256'
)

print(token)

dec_token = jwt.decode(token, secret_code, algorithms='HS256')

print(dec_token)


