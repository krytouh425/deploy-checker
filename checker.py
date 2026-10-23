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
