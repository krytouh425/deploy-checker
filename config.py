# Конфигурация проверок — все настройки в одном месте
# Меняй здесь не трогая основной код checker.py

# настройки подключения
DEFAULT_HOST = "localhost"
CONNECTION_TIMEOUT = 3  # секунд ждём ответа от порта

# порты которые проверяем перед деплоем
PORTY_DLYA_PROVERKI = {
    80: "HTTP",
    443: "HTTPS",
    5432: "PostgreSQL",
    6379: "Redis",
    8080: "App server"
}

# пороговые значения диска
DISK_WARN_PROCENT = 25   # предупреждение если свободно меньше 25%
DISK_FAIL_PROCENT = 10   # блокировка если свободно меньше 10%

# процессы которые должны быть запущены
PROTSESSY_DLYA_PROVERKI = [
    ("PostgreSQL", "postgres"),
    ("Redis", "redis"),
    ("Nginx", "nginx"),
    ("App server", "gunicorn")
]

# настройки отчёта
POKAZYVAT_WARN_V_OTCHETE = True   # показывать предупреждения
POKAZYVAT_OK_V_OTCHETE = True     # показывать успешные проверки
BLOKIROVAT_PRI_WARN = False       # блокировать деплой при WARN