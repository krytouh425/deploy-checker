# Модуль очистки диска — удаляем временные файлы перед деплоем
# Используется когда места на диске недостаточно для деплоя

import os
import shutil
from datetime import datetime


TEMP_PAPKI = ["tmp", "temp", "cache", ".cache"]  # папки для очистки
STARYE_POSLE_DNEY = 7  # удаляем файлы старше 7 дней


class OchistitelDiska:
    def __init__(self, koren="."):
        self.koren = koren
        self.udaleno_bayt = 0
        self.udaleno_faylov = 0

    def _vozrast_fayla(self, filepath):
        vremya = os.path.getmtime(filepath)
        data = datetime.fromtimestamp(vremya)
        return (datetime.now() - data).days

    def ochistit_temp(self):
        # удаляем временные файлы из стандартных папок
        for papka in TEMP_PAPKI:
            put = os.path.join(self.koren, papka)
            if not os.path.exists(put):
                continue
            for fayl in os.listdir(put):
                filepath = os.path.join(put, fayl)
                try:
                    razmer = os.path.getsize(filepath)
                    os.remove(filepath)
                    self.udaleno_bayt += razmer
                    self.udaleno_faylov += 1
                except Exception as e:
                    print(f"! Не удалось удалить {filepath}: {e}")

    def ochistit_starye_logi(self, log_papka="logs"):
        # удаляем лог-файлы старше N дней
        put = os.path.join(self.koren, log_papka)
        if not os.path.exists(put):
            return

        for fayl in os.listdir(put):
            if not fayl.endswith(".log"):
                continue
            filepath = os.path.join(put, fayl)
            if self._vozrast_fayla(filepath) >= STARYE_POSLE_DNEY:
                try:
                    razmer = os.path.getsize(filepath)
                    os.remove(filepath)
                    self.udaleno_bayt += razmer
                    self.udaleno_faylov += 1
                    print(f"✓ Удалён старый лог: {fayl}")
                except Exception as e:
                    print(f"! Ошибка при удалении {fayl}: {e}")

    def otchet(self):
        mb = self.udaleno_bayt / (1024 * 1024)
        print(f"\n{'=' * 40}")
        print(f"  ОЧИСТКА ДИСКА")
        print(f"  Удалено файлов: {self.udaleno_faylov}")
        print(f"  Освобождено:    {mb:.1f} МБ")
        print(f"{'=' * 40}\n")