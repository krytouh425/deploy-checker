# Модуль проверки памяти — контролируем RAM перед деплоем
# По запросу команды — issue #1 "Добавить проверку доступности RAM"

import os
import sys


# пороговые значения свободной памяти в МБ
RAM_WARN_MB = 512    # предупреждение если меньше 512 МБ
RAM_FAIL_MB = 256    # блокировка если меньше 256 МБ


class ProverkaRAM:
    def proverit(self):
        try:
            svobodno_mb = self._poluchit_svobodnuyu_ram()

            soobshenie = f"Свободно {svobodno_mb:.0f} МБ RAM"

            if svobodno_mb < RAM_FAIL_MB:
                status = STATUS_FAIL
                soobshenie += f" — критически мало (порог {RAM_FAIL_MB} МБ)"
            elif svobodno_mb < RAM_WARN_MB:
                status = STATUS_WARN
                soobshenie += f" — рекомендуем освободить память"
            else:
                status = STATUS_OK

            return ResultatProverki(
                nazvanie="RAM",
                status=status,
                soobshenie=soobshenie,
                znachenie=round(svobodno_mb)
            )

        except Exception as e:
            return ResultatProverki(
                nazvanie="RAM",
                status=STATUS_FAIL,
                soobshenie=f"Не удалось проверить RAM: {e}"
            )

    def _poluchit_svobodnuyu_ram(self):
        # читаем данные о памяти из системы
        if sys.platform == "win32":
            import ctypes
            kernel32 = ctypes.windll.kernel32
            c_ulong = ctypes.c_ulong
            class MEMORYSTATUS(ctypes.Structure):
                _fields_ = [
                    ("dwLength", c_ulong),
                    ("dwMemoryLoad", c_ulong),
                    ("dwTotalPhys", c_ulong),
                    ("dwAvailPhys", c_ulong),
                ]
            status = MEMORYSTATUS()
            status.dwLength = ctypes.sizeof(MEMORYSTATUS)
            kernel32.GlobalMemoryStatus(ctypes.byref(status))
            return status.dwAvailPhys / (1024 * 1024)
        else:
            with open("/proc/meminfo") as f:
                for stroka in f:
                    if stroka.startswith("MemAvailable"):
                        kb = int(stroka.split()[1])
                        return kb / 1024
        return 0