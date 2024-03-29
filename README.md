# Парсер книг с сайта tululu.org и сайт на основе собранных данных

Данный репозиторий, представляет собой скрипт для сбора информации о книгах с сайта [tululu.org](tululu.org) и создание
оффлайн библиотеки с книгами жанра "фантастика".
Под информацией подразумевается название книги, автор, картинка с обложкой (если таковая имеется), комментарии к книге
и непосредственно сам текст.

Т.к. каждая страница книги имеет свой уникальный id, скрипт предусматривает возможность задать критерии сбора информации, а конкретно,
возможность указать границы интервала страниц для сбора информации и скачивания книг.

## Хочу скачать библиотеку
Данный репозиторий имеет полностью все необходимые файлы, чтобы запустить подготовленную библиотеку оффлайн.
Для этого достаточно скачать данные папки:
```shell
/media
/pages
/static
```
После чего запустить файл `pages/index1.html` в любом браузере.

## Что за проект?
Данная оффлайн библиотека написана в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
Пример конечного результата можно увидеть на [Github Pages проекта](https://fulllmental.github.io/parse-tululu.org/)

<img src="https://iili.io/HEv188X.png" width="50%" height="50%" />

## Хочу такой же
### Как установить

Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```

### Аргументы main.py

Для запуска достаточно ввести:
```
python main.py
```
В данном случае соберется информация о первых 10 книгах на сайте, для изменения интервала, достаточно его указать после команды запуска
```
python main.py start_page end_page --dest_folder dwnlds
```
где `start_page` это начало интервала и является целым числом, а `end_page` это, соответственно, конец интервала и так же целое число. 
`--dest_folder` отвечает за папку, в которую будут сохранены книги/обложки книг/информации о книгах


Пример запуска:
```commandline
python main.py 20 30 --dest_folder dwnlds
Заголовок: 20. Черный PR. Защита и нападение в бизнесе и не только
                    Жанры: ['Деловая литература']
Заголовок: 21. Чичваркин Егений. Если из 100 раз тебя посылают 99
                    Жанры: ['Биографии и мемуары', 'Деловая литература']
Заголовок: 24. Дорога в будущее
                    Жанры: ['Маркетинг - PR - Реклама', 'О бизнесе популярно']
```

### Аргументы parse_tululu_category.py

Для запуска достаточно ввести:
```
python parse_tululu_category.py
```
В данном случае соберется информация со всех 701 страницы из категории "фантастика", для изменения интервала, достаточно указать его значения после команды запуска
```
python parse_tululu_category.py --start_page 650 --end_page 683
```
Всего дополнительных настроек, на данный момент шесть, все они опциональны:

`--start_page` - стартовый номер интервала страниц, для сбора информации и скачивания книг/обложек книг.

`--end_page` - финальный номер интервала страниц, для сбора информации и скачивания книг/обложек книг.

`-skip_txt` - При указании данного параметра, загружаться тексты книг не будут (по умолчанию будет сохранено в папке `books`).

`-skip_imgs` - При указании данного параметра, загружаться обложки книг не будут (по умолчанию будет сохранено в папке `images`).

`--dest_folder` - Можно указать путь для сохранения книг/обложек книг/информации о книгах в формате `*.json`.
По умолчанию всё будет сохранено в директорию, рядом с исполняемым файлом.

`--json_path` - Данный параметр принимает на вход путь до *.json файла с описанием книг/обложек книг/информации о книгах.


Пример запуска:
```commandline
python main.py  --start_page 700 --end_page 701 -skip_txt -skip_imgs --dest_folder Dwnlds --json_path Dwnlds
INFO:root:Сбор ссылок на книги со страниц, по жанрам
100%|█████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  3.19it/s]
INFO:root:Сбор информации с указанных страниц / скачивание книг / обложек
100%|███████████████████████████████████████████████████████████████| 25/25 [00:10<00:00,  2.32it/s]
INFO:root:Сохраняю, данные в JSON файл...
INFO:root:Готово...
```
### render_website.py
Для запуска достаточно ввести:
```
python render_website.py --json_folder my_folder --json_file my_json_file.json
```
`--json_folder` - Данный необязательный параметр принимает на вход название директории расположения *.json файла с собранными данными 
о книгах

`--json_file` - Данный необязательный параметр принимает на входе название файла с данными по книгам

Данный скрипт создаёт в директории `pages` нужное количество страниц со всеми скачанными книгами находящимися в директории `media`

После запуска сервера, открыть библиотеку можно будет по адресу [http://127.0.0.1:5500/](http://127.0.0.1:5500/
)
