# Сравниваем вакансии программистов

Скрипт ищет вакансии по самым популярным языкам программирования и выводит среднюю зарплату по языку программирования ,количество найденных вакансий, а также количество вакансий участвующих в подсчете средней зарплаты по языку программирования.

Поиск вакансий осуществляется через API  сайта [HeadHunter](https://dev.hh.ru/) и через API [Superjob](https://api.superjob.ru/)
### Как установить
Скачайте репозиторий и запустите команду 
```python 
pip install -r requirements.txt
```
Он установит нужные библиотеки для работы программы.

Также для  работы скрипта вам нужно зарегистрировать приложение в [API SuperJob](https://api.superjob.ru/) и получить Secret Key .

Кроме того нам нужно еще получить Access Token.
Как это сделать?
1. Перейдите по [ссылке]("https://api.superjob.ru/#authorize) и скопируйте то что в поле ```Пример запроса``` и вставьте в строку поиска браузера и перейдите по ней. Вставлять нужно без параметра ```GET```
2. После того как вы перешли по ней посмотрите в строку поиска там вы увидите вот такие строчки ```http://www.example.ru/?code=76e445583b0d8062e2cfe5b11702cbe5742d9dda1c137b8048d37b1bd1583f3f.b4d7e10cf69bf7dd213747cc8a549a2545db120b&state=custom``` вам нужно скопировать все что находится в поле ```code```.
3. После того как вы скопировали поле ```code``` вам нужно сделать запрос уже на Accses Token перейдите по [этой](https://api.superjob.ru/#access_token) ссылке и найдите поле ```Пример запроса``` 
Вам нужно в этом запросе заменить значение ```code``` на то который вы получили во втором шаге 
Пример:
```https://api.superjob.ru/2.0/oauth2/access_token/?code=76e445583b0d8062e2cfe5b11702cbe5742d9dda1c137b8048d37b1bd1583f3f.b4d7e10cf69bf7dd213747cc8a549a2545db120b&redirect_uri=http%3A%2F%2Fwww.example.ru&client_id=1895&client_secret=v3.r.136571141.be8710c005865505bc2e759ce6f00b68ef46ad33.b50c7acd628ad3f0b250e9f454c905ccc63e3553```
Далее вставьте это в строку поиска и перейдите по ней.Там вы увидите несколько полей со значениями вам нужно поле Access Token скопируйте его значение и сохраните .

Далее перейдите в папку где лежит скрипт найдите там файл ```.env.dist``` откройте его и замените там значения. 

1. В строке ```X_API_APP_ID``` вставьте  ```Secret Key``` своего приложения, посмотреть его можно [тут](https://api.superjob.ru/info/)
2. В строке ```AUTHORIZATION```  вам нужно нужно вставить то значение которые вы получили в шаге выше в пункте 3.
3. После всех проделанных операций файл ```.env.dist``` нужно сохранить и переименовать в ```.env``

Для запуска скрипта используйте следующую команду
```python
python main.py
```
После чего вы должны увидеть две таблицы как на картинке ниже.

![Вывод скрипта](/img/table.png "Пример запуска")


### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
