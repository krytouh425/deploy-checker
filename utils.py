# Вспомогательные функции — общие утилиты для всех модулей
# Не зависят от бизнес-логики, используются везде

import socket
import os
from datetime import datetime


def proverit_host(host, port=80, timeout=3):
    # быстрая проверка доступности хоста
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        rezultat = sock.connect_ex((host, port))
        sock.close()
        return rezultat == 0
    except socket.error:
        return False


def razmer_fayla_mb(filepath):
    # возвращаем размер файла в МБ
    if not os.path.exists(filepath):
        return 0
    return os.path.getsize(filepath) / (1024 * 1024)


def formatirovat_razmer(bayt):
    # форматируем размер в читаемый вид
    if bayt < 1024:
        return f"{bayt} Б"
    elif bayt < 1024 * 1024:
        return f"{bayt / 1024:.1f} КБ"
    elif bayt < 1024 * 1024 * 1024:
        return f"{bayt / (1024 * 1024):.1f} МБ"
    else:
        return f"{bayt / (1024 * 1024 * 1024):.1f} ГБ"


def tekushee_vremya():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def razdelitel(simvol="=", dlina=50):
    return simvol * dlina


def ip_adres_servera(host):
    # получаем IP адрес по имени хоста
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        return None