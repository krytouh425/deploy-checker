# Модуль логирования — записываем все проверки в лог
# Используется для анализа истории деплоев и поиска проблем

import os
from datetime import datetime

LOG_FILE = "checker.log"


class LoggerProverok:
    def __init__(self, filepath=LOG_FILE):
        self.filepath = filepath

    def _zapisat(self, uroven, soobshenie):
        vremya = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        stroka = f"{vremya} [{uroven}] {soobshenie}\n"
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(stroka)

    def info(self, soobshenie):
        self._zapisat("INFO", soobshenie)

    def warn(self, soobshenie):
        self._zapisat("WARN", soobshenie)

    def error(self, soobshenie):
        self._zapisat("ERROR", soobshenie)

    def zapisat_rezultat(self, rezultat):
        # логируем результат каждой проверки
        if rezultat.status == "OK":
            self.info(f"{rezultat.nazvanie}: {rezultat.soobshenie}")
        elif rezultat.status == "WARN":
            self.warn(f"{rezultat.nazvanie}: {rezultat.soobshenie}")
        else:
            self.error(f"{rezultat.nazvanie}: {rezultat.soobshenie}")

    def zapisat_otchet(self, otchet):
        # логируем итог всей проверки
        status = "DEPLOY_OK" if otchet.mozhno_deployt() else "DEPLOY_BLOCKED"
        self.info(f"{'=' * 30}")
        self.info(f"Сервер: {otchet.server} | Статус: {status}")
        self.info(f"Проверок: {len(otchet.rezultaty)}")
        self.info(f"{'=' * 30}")

    def prochitat_poslednie(self, kolichestvo=20):
        if not os.path.exists(self.filepath):
            print("Лог файл ещё не создан")
            return []

        with open(self.filepath, encoding="utf-8") as f:
            stroki = f.readlines()

        if not stroki:
            print("Лог файл пустой")
            return []

        rezultat = [s.strip() for s in stroki[-kolichestvo:]]

        # считаем статистику
        oshibki = len([s for s in rezultat if "[ERROR]" in s])
        preduprezhdeniya = len([s for s in rezultat if "[WARN]" in s])

        print(f"\nПоследние {len(rezultat)} записей:")
        print(f"Ошибок: {oshibki} | Предупреждений: {preduprezhdeniya}\n")

        return rezultat