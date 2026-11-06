# Модуль проверки сети — контролируем сетевые параметры перед деплоем
# Проверяем DNS, пинг и пропускную способность канала

import socket
import time


TIMEOUT = 5  # секунд ждём ответа
DNS_SERVERY = ["8.8.8.8", "8.8.4.4"]  # DNS серверы для проверки


class ProverkaSeti:
    def __init__(self, host="localhost"):
        self.host = host

    def proverit_dns(self, domen):
        # проверяем что DNS резолвит домен
        try:
            ip = socket.gethostbyname(domen)
            return ResultatProverki(
                nazvanie=f"DNS {domen}",
                status=STATUS_OK,
                soobshenie=f"Резолвится в {ip}"
            )
        except socket.gaierror as e:
            return ResultatProverki(
                nazvanie=f"DNS {domen}",
                status=STATUS_FAIL,
                soobshenie=f"Не удалось резолвить: {e}"
            )

    def proverit_ping(self, host, port=80):
        # проверяем время отклика хоста
        try:
            nachalo = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(TIMEOUT)
            sock.connect((host, port))
            sock.close()
            ms = round((time.time() - nachalo) * 1000)

            if ms > 1000:
                status = STATUS_WARN
                soobshenie = f"Высокая задержка: {ms} мс"
            else:
                status = STATUS_OK
                soobshenie = f"Отклик: {ms} мс"

            return ResultatProverki(
                nazvanie=f"Пинг {host}",
                status=status,
                soobshenie=soobshenie,
                znachenie=ms
            )
        except Exception as e:
            return ResultatProverki(
                nazvanie=f"Пинг {host}",
                status=STATUS_FAIL,
                soobshenie=f"Недоступен: {e}"
            )

    def proverit_vse(self, domeny=None, porty=None):
        rezultaty = []

        if domeny:
            for domen in domeny:
                rezultaty.append(self.proverit_dns(domen))

        if porty:
            for host, port in porty.items():
                rezultaty.append(self.proverit_ping(host, port))

        return rezultaty