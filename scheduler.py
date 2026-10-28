# Модуль планировщика — запускаем проверки по расписанию
# Используется для автоматического мониторинга перед деплоем

import time
from datetime import datetime


class PlanirovshhikProverok:
    def __init__(self, host="localhost", interval_minut=30):
        self.host = host
        self.interval = interval_minut * 60  # переводим в секунды
        self.istoriya = []  # история запусков

    def _zapisat_rezultat(self, uspeshno):
        # сохраняем результат каждого запуска
        self.istoriya.append({
            "vremya": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "host": self.host,
            "uspeshno": uspeshno
        })

    def odna_proverka(self):
        # запускаем одну итерацию проверок
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Запуск проверки {self.host}")
        try:
            from checker import zapustit_proverki, OtchetProverki
            zapustit_proverki(self.host)
            self._zapisat_rezultat(True)
            return True
        except Exception as e:
            print(f"Ошибка при проверке: {e}")
            self._zapisat_rezultat(False)
            return False

    def pokazat_istoriyu(self):
        if not self.istoriya:
            print("История проверок пуста")
            return

        print(f"\n{'=' * 45}")
        print(f"  ИСТОРИЯ ПРОВЕРОК ({len(self.istoriya)} запусков)")
        print(f"{'=' * 45}")
        for zapis in self.istoriya[-10:]:  # последние 10
            status = "✓" if zapis["uspeshno"] else "✗"
            print(f"  [{status}] {zapis['vremya']} — {zapis['host']}")
        print(f"{'=' * 45}\n")

    def zapustit_v_rezhime_monitora(self, max_zapuskov=None):
        # запускаем проверки в цикле с паузами
        zapuskov = 0
        print(f"Мониторинг запущен. Интервал: {self.interval // 60} мин.")
        print("Для остановки нажмите Ctrl+C\n")

        try:
            while True:
                self.odna_proverka()
                zapuskov += 1

                if max_zapuskov and zapuskov >= max_zapuskov:
                    break

                time.sleep(self.interval)

        except KeyboardInterrupt:
            print("\nМониторинг остановлен")

        self.pokazat_istoriyu()