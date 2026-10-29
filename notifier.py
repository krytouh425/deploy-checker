# Модуль уведомлений — оповещаем команду о результатах проверки
# Используется после каждого запуска checker.py перед деплоем

from datetime import datetime


class MenedzherUvedomleniy:
    def __init__(self, otchet):
        self.otchet = otchet
        self.istoriya = []  # история отправленных уведомлений

    def _sozdat_soobshenie(self):
        # формируем текст уведомления
        vremya = datetime.now().strftime("%d.%m.%Y %H:%M")
        status = "✓ РАЗРЕШЁН" if self.otchet.mozhno_deployt() else "✗ ЗАБЛОКИРОВАН"

        oshibki = [r for r in self.otchet.rezultaty if r.est_problema()]
        preduprezhdeniya = [r for r in self.otchet.rezultaty if r.est_preduprezhdenie()]

        stroki = [
            f"[{vremya}] Проверка сервера {self.otchet.server}",
            f"Деплой: {status}",
            f"Проверок: {len(self.otchet.rezultaty)}",
            f"Ошибок: {len(oshibki)} | Предупреждений: {len(preduprezhdeniya)}"
        ]

        if oshibki:
            stroki.append("\nКритические проблемы:")
            for o in oshibki:
                stroki.append(f"  - {o.nazvanie}: {o.soobshenie}")

        return "\n".join(stroki)

    def v_konsol(self):
        # выводим уведомление в консоль
        soobshenie = self._sozdat_soobshenie()
        print("\n" + "=" * 50)
        print(soobshenie)
        print("=" * 50 + "\n")
        self._zapisat_istoriyu(soobshenie)

    def v_fayl(self, filepath="notifications.log"):
        # записываем уведомление в файл
        soobshenie = self._sozdat_soobshenie()
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(soobshenie + "\n" + "-" * 50 + "\n")
        print(f"✓ Уведомление записано в {filepath}")
        self._zapisat_istoriyu(soobshenie)

    def _zapisat_istoriyu(self, soobshenie):
        self.istoriya.append({
            "vremya": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "soobshenie": soobshenie
        })

    def pokazat_istoriyu(self):
        if not self.istoriya:
            print("История уведомлений пуста")
            return
        print(f"\nИстория уведомлений ({len(self.istoriya)}):")
        for zapis in self.istoriya[-5:]:
            print(f"  [{zapis['vremya']}]")