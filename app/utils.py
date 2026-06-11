from pwdlib import PasswordHash
pwd_context=PasswordHash.recommended()
def hash(password : str):
    return pwd_context.hash(password)

def verify(plain_password : str,hashed_password: str):
    return pwd_context.verify(plain_password,hashed_password)