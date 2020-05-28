"WebServer" Автор Плюхин Игорь КН-102

Описание:
Веб-сервер раздающий статическое содержимое


- Асинхронна реализация
- Ручной разбор HTTP запросов
- keep alive connection
- кэш дескрипторов открытых файлов (https://nginx.org/ru/docs/http/ngx_http_core_module.html#open_file_cache)
- Автоматическая индексация файлов в каталоге
- Логирование запросов в файл в формате apache
- поддержка GET, POST запросов


Требования для запуска:
- Unix система
- sudo apt install tree
- python3.8
- pip install lru-dict


Примеры запуска:
python3.8 run_server.py
