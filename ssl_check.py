# Модуль проверки SSL сертификатов — контролируем срок действия
# По запросу команды — issue #2 "Добавить проверку SSL сертификатов"

import ssl
import socket
from datetime import datetime


PREDUPREZHDENIE_DNEY = 30  # предупреждение если до истечения меньше 30 дней
KRITICHESKIY_DNEY = 7      # критично если меньше 7 дней
TIMEOUT_PODKLYUCHENIYA = 5  # секунд ждём подключения


class ProverkaSSL:
    def __init__(self, host, port=443, timeout=5):
        self.host = host
        self.port = port
        self.timeout = timeout

    def poluchit_sertifikat(self):
        # получаем информацию о SSL сертификате
        context = ssl.create_default_context()
        with socket.create_connection((self.host, self.port), self.timeout) as sock:
            with context.wrap_socket(sock, server_hostname=self.host) as ssock:
                return ssock.getpeercert()

    def proverit(self):
        try:
            sert = self.poluchit_sertifikat()
            istechet_str = sert["notAfter"]
            istechet = datetime.strptime(istechet_str, "%b %d %H:%M:%S %Y %Z")
            dney_ostatok = (istechet - datetime.now()).days

            soobshenie = f"SSL сертификат истекает {istechet.strftime('%d.%m.%Y')} (осталось {dney_ostatok} дней)"

            if dney_ostatok <= KRITICHESKIY_DNEY:
                status = STATUS_FAIL
                soobshenie += " — КРИТИЧНО!"
            elif dney_ostatok <= PREDUPREZHDENIE_DNEY:
                status = STATUS_WARN
                soobshenie += " — скоро истекает"
            else:
                status = STATUS_OK

            return ResultatProverki(
                nazvanie=f"SSL {self.host}",
                status=status,
                soobshenie=soobshenie,
                znachenie=dney_ostatok
            )

        except Exception as e:
            return ResultatProverki(
                nazvanie=f"SSL {self.host}",
                status=STATUS_FAIL,
                soobshenie=f"Не удалось проверить SSL: {e}"
            )