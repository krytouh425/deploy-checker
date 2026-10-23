# Модель результата проверки — фиксируем статус каждого шага
# Используется всеми модулями перед деплоем на сервер

from datetime import datetime


# статусы проверки
STATUS_OK = "OK"
STATUS_WARN = "WARN"
STATUS_FAIL = "FAIL"


class ResultatProverki:
    def __init__(self, nazvanie, status, soobshenie, znachenie=None):
        self.nazvanie = nazvanie    # название проверки
        self.status = status        # OK / WARN / FAIL
        self.soobshenie = soobshenie
        self.znachenie = znachenie  # фактическое значение (например % диска)
        self.vremya = datetime.now().strftime("%H:%M:%S")

    def est_problema(self):
        return self.status == STATUS_FAIL

    def est_preduprezhdenie(self):
        return self.status == STATUS_WARN

    def __repr__(self):
        ikony = {STATUS_OK: "✓", STATUS_WARN: "!", STATUS_FAIL: "✗"}
        ikon = ikony.get(self.status, "?")
        return f"[{ikon}] {self.nazvanie}: {self.soobshenie}"


class OtchetProverki:
    def __init__(self, server):
        self.server = server  # имя или IP сервера
        self.rezultaty = []
        self.nachalo = datetime.now()

    def dobavit(self, rezultat):
        self.rezultaty.append(rezultat)

    def est_oshibki(self):
        return any(r.est_problema() for r in self.rezultaty)

    def mozhno_deployt(self):
        # деплой разрешён только если нет FAIL
        return not self.est_oshibki()

# Модуль проверки портов — убеждаемся что нужные сервисы доступны
# Проверяем перед деплоем чтобы не было сюрпризов на проде

import socket

# стандартные порты которые должны быть открыты
STANDARTNYE_PORTY = {
    80: "HTTP",
    443: "HTTPS",
    5432: "PostgreSQL",
    6379: "Redis",
    8080: "App server"
}


class ProverkaPortov:
    def __init__(self, host="localhost", timeout=3):
        self.host = host
        self.timeout = timeout  # секунд ждём ответа

    def proverit_port(self, port):
        # пробуем подключиться к порту
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            rezultat = sock.connect_ex((self.host, port))
            sock.close()

            if rezultat == 0:
                return ResultatProverki(
                    nazvanie=f"Порт {port}",
                    status=STATUS_OK,
                    soobshenie=f"{STANDARTNYE_PORTY.get(port, 'сервис')} доступен",
                    znachenie=port
                )
            else:
                return ResultatProverki(
                    nazvanie=f"Порт {port}",
                    status=STATUS_FAIL,
                    soobshenie=f"{STANDARTNYE_PORTY.get(port, 'сервис')} недоступен",
                    znachenie=port
                )
        except socket.error as e:
            return ResultatProverki(
                nazvanie=f"Порт {port}",
                status=STATUS_FAIL,
                soobshenie=f"Ошибка подключения: {e}",
                znachenie=port
            )

    def proverit_vse(self, porty):
        # проверяем список портов и возвращаем результаты
        return [self.proverit_port(p) for p in porty]

# Модуль проверки диска — контролируем свободное место перед деплоем
# Деплой с заполненным диском может уронить сервер

import shutil

# пороговые значения свободного места в процентах
POROG_WARN = 20   # предупреждение если меньше 20%
POROG_FAIL = 10   # ошибка если меньше 10%


class ProverkaDiska:
    def __init__(self, put="/"):
        self.put = put  # раздел который проверяем

    def poluchit_info(self):
        # получаем статистику диска
        stat = shutil.disk_usage(self.put)
        svobodno_procent = (stat.free / stat.total) * 100
        svobodno_gb = stat.free / (1024 ** 3)
        vsego_gb = stat.total / (1024 ** 3)
        return svobodno_procent, svobodno_gb, vsego_gb

    def proverit(self):
        try:
            procent, svobodno, vsego = self.poluchit_info()

            soobshenie = (
                f"Свободно {svobodno:.1f} ГБ из {vsego:.1f} ГБ "
                f"({procent:.1f}%)"
            )

            if procent < POROG_FAIL:
                status = STATUS_FAIL
                soobshenie += " — критически мало места!"
            elif procent < POROG_WARN:
                status = STATUS_WARN
                soobshenie += " — рекомендуем очистить диск"
            else:
                status = STATUS_OK

            return ResultatProverki(
                nazvanie="Диск",
                status=status,
                soobshenie=soobshenie,
                znachenie=round(procent, 1)
            )

        except Exception as e:
            return ResultatProverki(
                nazvanie="Диск",
                status=STATUS_FAIL,
                soobshenie=f"Не удалось проверить диск: {e}"
            )
# Модуль проверки процессов — убеждаемся что нужные сервисы запущены
# Если база или кэш не работают — деплой бессмысленен

import subprocess
import sys


class ProverkaProtsessov:
    def __init__(self):
        self.os_windows = sys.platform == "win32"

    def poluchit_protsessy(self):
        # получаем список запущенных процессов
        try:
            if self.os_windows:
                rezultat = subprocess.run(
                    ["tasklist"],
                    capture_output=True,
                    text=True
                )
            else:
                rezultat = subprocess.run(
                    ["ps", "aux"],
                    capture_output=True,
                    text=True
                )
            return rezultat.stdout.lower()
        except Exception as e:
            return ""

    def proverit_protsess(self, nazvanie, klyuchevoe_slovo):
        # ищем процесс по ключевому слову
        protsessy = self.poluchit_protsessy()

        if klyuchevoe_slovo.lower() in protsessy:
            return ResultatProverki(
                nazvanie=nazvanie,
                status=STATUS_OK,
                soobshenie=f"{nazvanie} запущен"
            )
        else:
            return ResultatProverki(
                nazvanie=nazvanie,
                status=STATUS_WARN,
                soobshenie=f"{nazvanie} не обнаружен в списке процессов"
            )

    def proverit_vse(self, protsessy):
        # protsessy — список кортежей (название, ключевое_слово)
        return [self.proverit_protsess(n, k) for n, k in protsessy]

# Точка входа — запускаем все проверки и выводим итоговый отчёт
# Если есть FAIL — деплой блокируется

import sys


def zapustit_proverki(host="localhost"):
    otchet = OtchetProverki(host)

    print(f"\n{'=' * 50}")
    print(f"  ПРОВЕРКА СЕРВЕРА ПЕРЕД ДЕПЛОЕМ: {host}")
    print(f"{'=' * 50}\n")

    # проверка портов
    checker_portov = ProverkaPortov(host)
    porty = [80, 443, 5432, 6379]
    for rezultat in checker_portov.proverit_vse(porty):
        otchet.dobavit(rezultat)
        print(rezultat)

    # проверка диска
    checker_diska = ProverkaDiska()
    rezultat_diska = checker_diska.proverit()
    otchet.dobavit(rezultat_diska)
    print(rezultat_diska)

    # проверка процессов
    checker_protsessov = ProverkaProtsessov()
    protsessy = [
        ("PostgreSQL", "postgres"),
        ("Redis", "redis"),
        ("Nginx", "nginx")
    ]
    for rezultat in checker_protsessov.proverit_vse(protsessy):
        otchet.dobavit(rezultat)
        print(rezultat)

    # итоговый отчёт
    oshibki = [r for r in otchet.rezultaty if r.est_problema()]
    preduprezhdeniya = [r for r in otchet.rezultaty if r.est_preduprezhdenie()]

    print(f"\n{'=' * 50}")
    print(f"  ИТОГ")
    print(f"{'=' * 50}")
    print(f"  Проверок выполнено:   {len(otchet.rezultaty)}")
    print(f"  Ошибок (FAIL):        {len(oshibki)}")
    print(f"  Предупреждений (WARN): {len(preduprezhdeniya)}")

    if otchet.mozhno_deployt():
        print("\n  ✓ ДЕПЛОЙ РАЗРЕШЁН")
    else:
        print("\n  ✗ ДЕПЛОЙ ЗАБЛОКИРОВАН — устраните ошибки")
        for o in oshibki:
            print(f"    → {o.nazvanie}: {o.soobshenie}")

    print(f"{'=' * 50}\n")


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    zapustit_proverki(host)

