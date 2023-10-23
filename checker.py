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
