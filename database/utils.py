''' Libraries '''
import os
import json
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad



''' Parameters '''
DB_AES_KEY = bytes(os.environ.get("DB_AES_KEY"), encoding="utf8")
DB_AES_IV  = bytes(os.environ.get("DB_AES_IV") , encoding="utf8")
weekday_array = ['一', '二', '三', '四', '五', '六']
session_dict  = dict(zip(['A', 'B', 'C', 'D'], list(range(11, 15))))
place_array   = ["本部", "公館"]



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


def process_time_info(time_info):
    total_time, total_place = [ 0 ] * 91, [ 0 ] * 3
    if time_info == "" or time_info == "◎密集課程":
        total_time[90] = 1
        total_place[2] = 1
    else:
        for ti in time_info.split(','):
            ti = ti.strip().split(' ')
            weekday = weekday_array.index(ti[0])
            session = ti[1]
            if '-' not in session:
                if session in session_dict: session = session_dict[session]
                total_time[weekday*15+int(session)] = 1
            else:
                s_start, s_end = session.split('-')
                if s_start in session_dict: s_start = session_dict[s_start]
                if s_end   in session_dict: s_end   = session_dict[s_end]
                for s in range(int(s_start), int(s_end)+1):
                    total_time[weekday*15+s] = 1
            place = ti[2]
            if place in place_array: place = place_array.index(place)
            else                   : place = 2
            total_place[place] = 1
    total_time_1 = int(''.join(str(t) for t in total_time[:64]), base=2)
    total_time_2 = int(''.join(str(t) for t in total_time[64:]), base=2)
    total_place  = int(''.join(str(p) for p in total_place)    , base=2)
    return total_time_1, total_time_2, total_place