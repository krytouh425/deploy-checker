# Модуль проверки здоровья сервисов — быстрая диагностика
# Используется дежурным администратором для оценки состояния системы

from datetime import datetime


class HealthChecker:
    def __init__(self, host="localhost"):
        self.host = host
        self.rezultaty = []

    def dobavit_rezultat(self, nazvanie, status, soobshenie):
        self.rezultaty.append({
            "nazvanie": nazvanie,
            "status": status,
            "soobshenie": soobshenie,
            "vremya": datetime.now().strftime("%H:%M:%S")
        })

    def proverit_set(self, proverki):
        # запускаем набор проверок и собираем результаты
        for nazvanie, funktsiya in proverki.items():
            try:
                rezultat = funktsiya()
                self.dobavit_rezultat(nazvanie, "OK", rezultat)
            except Exception as e:
                self.dobavit_rezultat(nazvanie, "FAIL", str(e))

    def obshiy_status(self):
        # общий статус — OK только если все проверки прошли
        if not self.rezultaty:
            return "UNKNOWN"
        est_fail = any(r["status"] == "FAIL" for r in self.rezultaty)
        est_warn = any(r["status"] == "WARN" for r in self.rezultaty)
        if est_fail:
            return "FAIL"
        if est_warn:
            return "WARN"
        return "OK"

    def vyvesti(self):
        print(f"\n{'=' * 50}")
        print(f"  HEALTH CHECK — {self.host}")
        print(f"  Статус: {self.obshiy_status()}")
        print(f"{'=' * 50}")
        for r in self.rezultaty:
            ikona = "✓" if r["status"] == "OK" else "✗"
            print(f"  [{ikona}] {r['nazvanie']}: {r['soobshenie']}")
        print(f"{'=' * 50}\n")