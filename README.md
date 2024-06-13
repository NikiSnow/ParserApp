# Apache Log Aggregator

## Описание
Приложение для агрегации данных из логов веб-сервера Apache и предоставления API для получения данных. Приложение позволяет просматривать и фильтровать логи по IP-адресам и датам.

## Функционал
- Парсинг логов Apache и сохранение данных в базу данных.
- API для получения логов в формате JSON.
- Фильтрация логов по IP-адресам и промежутку дат.
- Конфигурация через файл настроек.
- Запуск парсинга как вручную, так и по расписанию (cron).

## Установка и настройка
```bash
- git clone https://github.com/NikiSnow/ParserApp
- cd ParseApp
- загрузите ваши access.log
- при необходимости отредактируйте parser.ini
- через консоль запустите parser.py
- введите python parser.py -h изучите доступные команды
```

## Доступные команды
```bash
usage: parser.py [-h] [-c CONFIG] [-d DB] [--ip IP] [--start-time START_TIME] [--end-time END_TIME] {parse,get}

positional arguments:
  {parse,get}

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        path to configuration file
  -d DB, --db DB        path to db file
  --ip IP               host ip filter (only for get command)
  --start-time START_TIME
                        start time (only for get command)
  --end-time END_TIME   stop time (only for get command)
  ```
  
  ### Пример использования
  ```bash
  python parse.py parse # Для того чтобы распарсить данные и сохранить в базу данных из log файлов
   python parse.py get --ip 2.177.12.140 # Фильтрация данных по IP
   python parse.py get --start-time "2019-01-22 03:56:35" # Фильтрация данных по времени начала
   python parse.py get --end-time "2019-01-22 03:56:35" # Фильтрация данных по времени конца
   python parse.py get --start-time "2019-01-22 03:56:35" --end-time "2035-01-22 03:56:35" # Фильтраци по определенному промежутку   
  ```
  
  ### Конфигурационный файл
  ```
  files_glob отвечает за то какие файлы будут парситься
  logformat задает формат access.log
  ```
  
