# Модуль отчётов — сохраняем результаты проверок в файл
# Используется для истории деплоев и разбора инцидентов

import os
import json
from datetime import datetime

REPORTS_DIR = "reports"  # папка для отчётов о проверках


class ReporterProverok:
    def __init__(self, otchet, reports_dir=REPORTS_DIR):
        self.otchet = otchet
        self.reports_dir = reports_dir
        self._sozdat_papku()

    def _sozdat_papku(self):
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def _imya_fayla(self, format):
        vremya = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.reports_dir, f"deploy_{vremya}.{format}")

    def v_json(self):
        # сохраняем полный отчёт в JSON для автоматической обработки
        danye = {
            "server": self.otchet.server,
            "vremya": self.otchet.nachalo.strftime("%Y-%m-%d %H:%M:%S"),
            "mozhno_deployt": self.otchet.mozhno_deployt(),
            "rezultaty": [r.to_dict() for r in self.otchet.rezultaty]
        }
        fayl = self._imya_fayla("json")
        with open(fayl, "w", encoding="utf-8") as f:
            json.dump(danye, f, ensure_ascii=False, indent=2)
        print(f"✓ Отчёт сохранён: {fayl}")
        return fayl

    def v_txt(self):
        # читаемый отчёт для дежурного администратора
        fayl = self._imya_fayla("txt")
        with open(fayl, "w", encoding="utf-8") as f:
            f.write("=" * 50 + "\n")
            f.write(f"  ОТЧЁТ О ПРОВЕРКЕ СЕРВЕРА\n")
            f.write(f"  Сервер: {self.otchet.server}\n")
            f.write(f"  Время:  {self.otchet.nachalo.strftime('%d.%m.%Y %H:%M')}\n")
            f.write("=" * 50 + "\n\n")

            for r in self.otchet.rezultaty:
                f.write(f"{r}\n")

            f.write("\n" + "=" * 50 + "\n")
            if self.otchet.mozhno_deployt():
                f.write("  ИТОГ: ДЕПЛОЙ РАЗРЕШЁН\n")
            else:
                f.write("  ИТОГ: ДЕПЛОЙ ЗАБЛОКИРОВАН\n")
            f.write("=" * 50 + "\n")

        print(f"✓ Отчёт сохранён: {fayl}")
        return fayl