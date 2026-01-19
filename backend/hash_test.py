from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
secret = 'testpass123'
print('secret repr:', repr(secret))
print('secret length:', len(secret))
print('hashing...')
print(pwd.hash(secret))
