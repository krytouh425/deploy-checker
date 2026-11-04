# Модуль проверки внешних API — убеждаемся что зависимости доступны
# По запросу команды — issue #3 "Добавить проверку доступности внешних API"

import socket
import urllib.request
import urllib.error


# внешние сервисы от которых зависит приложение
VNESHNIE_API = {
    "Платёжный шлюз": "https://api.payment-gateway.ru",
    "SMS провайдер": "https://api.sms-service.ru",
    "Геокодер": "https://api.geocoder.ru"
}

TIMEOUT = 5  # секунд ждём ответа


class ProverkaVneshnihAPI:
    def __init__(self, api_spisok=None):
        self.api_spisok = api_spisok or VNESHNIE_API

    def proverit_url(self, nazvanie, url):
        # проверяем доступность URL
        try:
            zapros = urllib.request.Request(url, method="HEAD")
            urllib.request.urlopen(zapros, timeout=TIMEOUT)
            return ResultatProverki(
                nazvanie=f"API {nazvanie}",
                status=STATUS_OK,
                soobshenie=f"{url} доступен"
            )
        except urllib.error.HTTPError as e:
            # HTTP ошибка — сервер отвечает значит доступен
            if e.code < 500:
                return ResultatProverki(
                    nazvanie=f"API {nazvanie}",
                    status=STATUS_OK,
                    soobshenie=f"{url} отвечает (код {e.code})"
                )
            return ResultatProverki(
                nazvanie=f"API {nazvanie}",
                status=STATUS_FAIL,
                soobshenie=f"{url} вернул ошибку {e.code}"
            )
        except (urllib.error.URLError, socket.timeout) as e:
            return ResultatProverki(
                nazvanie=f"API {nazvanie}",
                status=STATUS_FAIL,
                soobshenie=f"{url} недоступен: {e}"
            )

    def proverit_vse(self):
        return [
            self.proverit_url(nazvanie, url)
            for nazvanie, url in self.api_spisok.items()
        ]