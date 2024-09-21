>Проект вышел на стадию MVP

### ИИ-секретарь

<img src="https://github.com/user-attachments/assets/8e41b23a-91ce-4853-87f2-d4283703b6e8" width="50%" height="50%"/>

Данный сервис призван упростить протоколирование совещаний, используя ИИ-технологии для транскрибирования голоса в текст. На данный момент реализовано 2 функциональные возможности:

- Транскрибирование аудиофайлов (форматы wave, mp3)
- Транскрибирование аудиопотока с микрофона

Реализована идентификация пользователя по SID, одновременная работа нескольких пользователей не пересекается (как разных клиентов, так и нескольких вкладок на одном клиенте). Авторизация не предусмотрена на текущем этапе реализации.

Точность транскрибации зависит от используемой версии модели VOSK. 

> На данной стадии реализации проекта аудиопоток преобразуется в сырой текст. Восстановление пунктуации, а также внедрение VAD технологий для облегчения работы модели транскрибирования будут добавлены позже. 

> В ближайшее время планируется переход с http протокола на https при помощи reverse proxy сервера.

Для запуска необходимо поднять контейнер с моделью VOSK, а затем контейнер с проектом, об этом далее.

#### VOSK

Сервис использует модель транскрибации VOSK с открытым исходным кодом. Достаточно запустить контейнер с моделью.

Запуск с базовой моделью

```bash
docker run -d -p 2700:2700 alphacep/kaldi-ru:latest
```

Запуск со своей моделью (опционально)

```bash
docker run -d -p 2700:2700 -v <путь к модели>:/opt/vosk-model-ru/model alphacep/kaldi-ru:latest
```

#### Образ сервера

Предпочтительный вариант запуска, так как не требует вмешательства в конфигурацию при запуске на хосте, отличном от `127.0.0.1`. 

Собрать образ

```bash
docker build -t vosk-server .
```

Запустить

```bash
docker run -d -p 5000:5000 -e VOSK=ws://host.docker.internal:2700 vosk-server
```

Параметры контейнера:

- `HOST` - адрес хоста сервера, базовое значение `0.0.0.0`
- `PORT` - порт сервера, базовое значение `5000`
- `VOSK` - адрес сервера Vosk с протоколом ws, базовое значение `ws://host.docker.internal:2700`
- `UPLOADS_DIR` - путь к загружаемым файлам (файлы удаляются после обработки), базовое значение `uploads`
- `RECORD_DIR` - путь к файлам, записанным с микрофона, базовое значение `records`

#### Сервер проекта

Для отладки можно не собирать контейнер, а запускать сервер из исходного кода. В таком случае сервер будет запускаться по адресу `127.0.0.1:5000` и ожидать, что модель воска запущена на `127.0.0.1:2700`.

Запустите Flask-сервер

```bash
flask run
```
