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
2. В корне уже есть `amvera.yml`: Python 3.12 + `pip`, запуск `env PORT=8080 python3 -u server.py`, `containerPort: 8080`.
3. Сервер слушает `0.0.0.0`. На Amvera порт задаётся явно (`PORT=8080`), потому что платформа не всегда прокидывает `PORT` сама — иначе остаётся локальный `43127` и получается 503.
4. Зависимостей pip нет (`requirements.txt` пустой по смыслу — только stdlib).
5. После пуша нажмите **Собрать** (не только перезапуск). При 502/503 сверьте `containerPort` и реальный bind в логе приложения.
