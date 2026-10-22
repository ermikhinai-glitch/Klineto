# Klineto

Статический сайт клининга в Москве и Московской области (HTML/CSS/JS, без фреймворка).

## Как открыть локально

```bash
python3 server.py
```

Сайт: [http://127.0.0.1:43127](http://127.0.0.1:43127)

Другой порт:

```bash
PORT=43210 python3 server.py
```

Основные разделы: `/`, `/uborka-kvartir`, `/uborka-domov`, `/uborka-ofisov` и вложенные услуги. Дополнительно из макета hub v2: `/korporativnym`, `/o-kompanii`, `/kontakty`, `/kalkulyator`, `/tarify`, `/zayavka-prinyata`.

## Деплой на Amvera

Репозиторий: [github.com/ermikhinai-glitch/Klineto](https://github.com/ermikhinai-glitch/Klineto) (ветка `main`).

1. В [Amvera](https://amvera.ru) создайте приложение из GitHub-репозитория (или подключите remote Amvera и сделайте `git push`).
2. В корне уже есть `amvera.yml`: Python 3.12 + `pip`, запуск `python3 server.py`, `containerPort: 80`.
3. Сервер слушает `0.0.0.0` и берёт порт из переменной `PORT` (на Amvera по умолчанию `80`).
4. Зависимостей pip нет (`requirements.txt` пустой по смыслу — только stdlib).
5. После сборки откройте выданный Amvera-домен; при 502 проверьте, что приложение биндится на `0.0.0.0` и порт совпадает с `containerPort` / `PORT`.
