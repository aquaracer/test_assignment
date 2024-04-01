### Сборка контейнера docker

```bash
docker-compose --build
```

### Запуск приложения через docker-compose

```bash
docker-compose up
```

### Запуск тестов в docker-compose

```bash
 docker-compose run --rm api ./manage.py test
```