''' Libraries '''
import os
import json
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad



''' Parameters '''
DB_AES_KEY  = bytes(os.environ.get("DB_AES_KEY"), encoding="utf8")
DB_AES_IV   = bytes(os.environ.get("DB_AES_IV") , encoding="utf8")



''' Functions '''
def AES_encode(data):
    cipher = AES.new(DB_AES_KEY, AES.MODE_CBC, DB_AES_IV)
    data = bytes(data, encoding="utf-8")
    data = pad(data, 48, style="pkcs7")
    data = cipher.encrypt(data)
    return data


def AES_decode(data):
    decrypter = AES.new(DB_AES_KEY, AES.MODE_CBC, DB_AES_IV)
    data = decrypter.decrypt(data)
    data = unpad(data, 48, style="pkcs7")
    data = data.decode(encoding="utf-8")
    return data