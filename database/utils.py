''' Libraries '''
import os
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad



''' Parameters '''
DB_AES_KEY  = bytes(os.environ.get("DB_AES_KEY"), encoding="utf8")
DB_AES_IV   = bytes(os.environ.get("DB_AES_IV") , encoding="utf8")



''' Functions '''
def AES_encode(data):
    cipher = AES.new(DB_AES_KEY, AES.MODE_CBC, DB_AES_IV)
    data = bytes(data, encoding="utf-8")
    return cipher.encrypt(pad(data, 16, style='pkcs7'))


def AES_decode(data):
    decrypter = AES.new(DB_AES_KEY, AES.MODE_CBC, DB_AES_IV)
    return decrypter.decrypt(data).decode(encoding="utf-8")