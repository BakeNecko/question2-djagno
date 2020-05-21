## Запуск контейнера Docker: 
sudo нужно использовать при необходимости 
1. `sudo docker-compose up --buld`   #можно добавить флаг -d 
2. `sudo service postgresql stop `
3. `sudo docker-compose exec questions-database psql --username=postgres`
4. `CREATE DATABASE questions_db OWNER postgres;` # Затем выходим из psql
5. `sudo docker-compose exec questions-server python3 ./backend/manage.py makemigrations`
6. `sudo docker-compose exec questions-server python3 ./backend/manage.py migrate`
7. `sudo docker-compose exec questions-server python3 ./backend/manage.py createsupseruser`

Получаем 2 сервиса nginx на localhost:8080 и Gunicorn на localhost:8000
Nginx нормально, не настроен, не обрабатывает staticfiles и media. Только проксирует запросы. Он только для демонстрации.

**Расширенная докумаентация для API доступна по двум URL:**

* `http://localhost:8000/swagger/`
* `http://localhost:8000/redoc/`

Там можно посмотреть информацию о типе полей, правах и т.д

В этом REST API, я использовал `JWT` токены, они удобные, защещенные и хорошо подходят для REST т.к 
их удобно хранить на любом устройстве и это позваляет нашему API поддерживать не только WEB, а также моб приложения и им подобные.
Для указания своей авторизованности нужно в `Headers` в поле `Authorization` устанавливать значение `JWT <access token>` (с пробелом между ними)

Досуп к корневому api осуществляется по шлюзу `http://localhost:8000/api/v1/`

## Методы API: 
1. `token/refresh/` Метод для обновления токена доступа в **JWT**
Принимает только один параметр: **refresh**. Являющийся refresh токеном

2. `log_in` Метод для авторизации, возращает 2 токена **access и refresh**. 
Принимает username и password пользователя.

3. `poll/` Метод поддерживающий 4 типа запросов **GET**, **PUT**, **DELETE**, **POST**.
    GET метод разрешен для всех и возращает все активные на данный момент опросы
    POST защищенный метод для администраторов, создающий опросы. Пример Данных POST запроса:
    ```json
    {
      "name": "Test Poll",  
      "description": "New Test Poll",
      "date_start": "2020-05-23",
      "date_end": "2020-05-31",
      "questions": [   
      // Это поле соделжит в себе вопросы этого опроса При сохранении модели Poll они будут связанны с ним 
          {
              "text": "How many u drink?",
              "question_type": "TEXT_RESPONSE"
          },
          {
              "text": "New Questoin",
              "question_type": "MULTIPLE_CHOICE_ANSWER"
          }
      ]
    }```
 4 `poll/<int:pk>/` Метод поддерживает 3 типа запросов **GET DELETE PUT**, не трудно догадаться, 
                    что он работает с конкретной моделью опроса.
                    
    GET метод разрешен абсолютно для всех что бы его вызвать нужно просто в url передать id Опроса
    Пример: poll/32/
    
    PUT  защищенный метод для администраторов, Пример данных PUT запроса: 
   
      {
        "name": "Change Test Pool",
        "description": " Change New Test Poll",
        "date_end": "2020-05-26"
      }
    
    Так же замечу что при попытке изменить поле date_start возникнит ошибка 400 с ифнормацией 
    
    DELETE разрешен толко для администраторов. Вызывается так же как GET:
    `poll/<int:pk>/`

5.  `question/` Метод (Толко для админов) для создания вопроса принимает **POST** запрос. Пример данных:
```json
        {
            "poll_id": 12, 
            "text": "New test",
            "question_type": "ONE_CHOICE_ANSWER"
        }
```     
      poll_id является id Опроса, для которого создается вопрос.
      Удобный метод для добавленияя вопрос в уже созданный опросник.
 
 
6. `question/<int:pk>/` Метод очень поход на 4. Так же поддерживает 3 типа запросов **GET, DELETE, PUT**
     Полностью админский метод. Примеры:
     
     GET: `question/12/` где 12 это id вопроса в БД
     
     PUT: Примеры данных
     ```json
     {
    "text": "New test test",
    "question_type": "ONE_CHOICE_ANSWER"
    }
    ```
    DELETE такой же как и GET Пример: ``question/11/`
    
    
7. `report/` **POST** Метод для создания ответа пользователя. Разрешен всем, даже анонимным.
    Данные структурируются так:
    ```json
    { 
        "poll_id": 3 
        "answers": [
            {
                "answer": "First answer",
                "question_id": 124,              
            },
            {
                "answer": "Two answer",
                "question_id": 521,              
            },
            {
                "answer": "Three answer",
                "question_id": 123,              
            }
        ]
    }
    ```
    В данном примере poll_id это id Опросника, а question_id это id вопроса 
    с которым связывается соответсвующий ответ пользователя. 
    
    Также есть метод **GET** 
    который возращает список всех опросников пройденных пользователем вызывается просто 
    `report/` всю необходимую информацю View берет из request.
    
8. `report/<int:pk>/` Метод для получения информации о конкретном отчете пользователя. 
    Метод защищен, и не дает другим пользователям доступ к ответм других юзеров. 
    т.к queryset фильтруется на основе request.user
    Но также предусмнотрнно что администратор может получить доступ к любому представлению.
    Вызывается просто: `report/23/` где 23 это id отчета.
