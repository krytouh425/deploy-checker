# Модуль истории деплоев — храним все запуски проверок
# Используется для анализа стабильности сервера за период

import json
import os
from datetime import datetime

HISTORY_FILE = "deploy_history.json"  # файл истории


class HistoryDeployev:
    def __init__(self, filepath=HISTORY_FILE):
        self.filepath = filepath

    def _zagruzit(self):
        if not os.path.exists(self.filepath):
            return []
        with open(self.filepath, encoding="utf-8") as f:
            return json.load(f)

    def _sohranit(self, istoriya):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(istoriya, f, ensure_ascii=False, indent=2)

    def zapisat(self, server, uspeshno, kolichestvo_proverok, oshibki=None):
        # записываем результат одного запуска
        istoriya = self._zagruzit()
        istoriya.append({
            "vremya": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "server": server,
            "uspeshno": uspeshno,
            "kolichestvo_proverok": kolichestvo_proverok,
            "oshibki": oshibki or []
        })
        self._sohranit(istoriya)

    def poslednie(self, kolichestvo=10):
        istoriya = self._zagruzit()
        return istoriya[-kolichestvo:]

    def statistika(self):
        istoriya = self._zagruzit()
        if not istoriya:
            return None

        uspeshno = len([z for z in istoriya if z["uspeshno"]])
        return {
            "vsego": len(istoriya),
            "uspeshno": uspeshno,
            "neuspeshno": len(istoriya) - uspeshno,
            "protsent_uspekha": round(uspeshno / len(istoriya) * 100, 1)
        }

    def vyvesti(self):
        stat = self.statistika()
        if not stat:
            print("История деплоев пуста")
            return

        print(f"\n{'=' * 45}")
        print(f"  ИСТОРИЯ ДЕПЛОЕВ")
        print(f"  Всего: {stat['vsego']} | Успешно: {stat['uspeshno']} | "
              f"Ошибок: {stat['neuspeshno']}")
        print(f"  Успешность: {stat['protsent_uspekha']}%")
        print(f"{'=' * 45}")

        for z in self.poslednie():
            status = "✓" if z["uspeshno"] else "✗"
            print(f"  [{status}] {z['vremya']} — {z['server']}")
        print(f"{'=' * 45}\n")