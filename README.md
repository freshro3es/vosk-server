
#### Vosk

Запуск с базовой моделью

```bash
docker run -d -p 2700:2700 alphacep/kaldi-ru:latest
```

Запуск со своей моделью (опционально)

```bash
docker run -d -p 2700:2700 -v /home/freshro3es/vosk/vosk-model-small-ru-0.22:/opt/vosk-model-ru/model alphacep/kaldi-ru:latest
```

#### Сервер

Запустите Flask-сервер

```bash
flask run
```

#### Image

Собрать образ

```bash
docker build -t vosk-server .
```

Запустить

```bash
docker run -d -p 5000:5000 -e VOSK=ws://host.docker.internal:2700 vosk-server
```

