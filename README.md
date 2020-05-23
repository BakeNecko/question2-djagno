## Запуск контейнера Docker:

sudo нужно использовать при необходимости

1. `sudo docker-compose up --buld` #можно добавить флаг -d

Чтобы создать супер пользователя:
`sudo docker-compose exec questions-server python3 ./backend/manage.py createsupseruser`
(По умолчанию супер пользователь admin/admin)

Получаем 1 сервис Gunicorn на localhost:8000

**Расширенная докумаентация для API доступна по двум URL:**

- `http://localhost:8000/swagger/`
- `http://localhost:8000/redoc/`

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
   GET метод разрешен для всех и возращает все активные на данный момент опросы.
   Производя пагинацию по 20 Опросов. В сумме возращая 100 овопросов.
   Пример ответа на GET запрос:

   ```json
   {
     "count": 3,
     "next": "http://localhost:8000/api/v1/poll/?page=2",
     "previous": null,
     "results": [
       {
         "id": 4,
         "name": "Change Test Pool",
         "description": "Change New Test Poll",
         "published": "2020-05-23",
         "date_start": "2020-05-30",
         "date_end": "2020-05-31",
         "questions": [
           {
             "id": 10,
             "text": "How many u drink?",
             "question_type": "TEXT_RESPONSE",
             "answer_choices": null,
             "poll": 4
           },
           {
             "id": 11,
             "text": "New Questoin",
             "question_type": "MULTIPLE_CHOICE_ANSWER",
             "answer_choices": {
               "1": "first answer",
               "2": "secont answer"
             },
             "poll": 4
           }
         ]
       }
     ]
   }
   ```

   POST защищенный метод для администраторов, создающий опросы. Пример Данных POST запроса:

   ```json
   {
   "name": "New Test Poll",
   "description": "New Test Poll",
   "date_start": "2020-05-23",
   "date_end": "2020-05-31",
   "questions_list": [
       {
           "text": "How many u drink?",
           "question_type": "TEXT_RESPONSE"
       },
       {
           "text": "New Questoin",
           "question_type": "MULTIPLE_CHOICE_ANSWER",
           "answer_choices": {
               "1": "first answer",
               "2": "secont answer"
           }
       }
   ]}
   }
   ```

   Варианты question_type: ONE_CHOICE_ANSWER, TEXT_RESPONSE, MULTIPLE_CHOICE_ANSWER
   Если вопрос с множеством ответов то в answer_choices нужно передать варианты ответа на него.

4 `poll/<int:pk>/` Метод поддерживает 3 типа запросов **GET DELETE PUT**, не трудно догадаться,
что он работает с конкретной моделью опроса.

GET метод разрешен абсолютно для всех что бы его вызвать нужно просто в url передать id Опроса
Пример: poll/32/

PUT защищенный метод для администраторов, Пример данных PUT запроса:

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
  "poll": 1,
  "question_type": "MULTIPLE_CHOICE_ANSWER",
  "text": "Text of question",
  "answer_choices": {
    "1": "first answer",
    "2": "secont answer"
  }
}
```

      poll является id Опроса, для которого создается вопрос.
      в answer_choices добавляются варинты выбора ответа
      Удобный метод для добавленияя вопрос в уже созданный опросник.

6. `question/<int:pk>/` Метод очень поход на 4. Так же поддерживает 3 типа запросов **GET, DELETE, PUT**
   Полностью админский метод. Примеры:

   GET: `question/12/` где 12 это id вопроса в БД

   PUT: Примеры данных

   ```json
   {
     "question_type": "MULTIPLE_CHOICE_ANSWER",
     "text": "New Text of Question",
     "answer_choices": {
       "1": "New  answer",
       "2": "secont answer"
     }
   }
   ```

DELETE такой же как и GET Пример: ``question/11/`

7. `report/` **POST** Метод для создания ответа пользователя. Разрешен всем, даже анонимным.
   Данные структурируются так:

   ```json
   {
     "poll": 1,
     "user_report_id": 123,
     "answers_list": [
       {
         "answer": "First answer",
         "question": 1
       },
       {
         "answer": "1 2",
         "question": 2
       }
     ]
   }
   ```

   **Ответить на определенный Poll можно только 1н раз, дргуие попытки ответить на опрос будут блокированны**
   В данном примере poll_id это id Опросника, а question_id это id вопроса
   с которым связывается соответсвующий ответ пользователя.
   Если ответ содерижт множетсво вариантов ответа то их нужно указывать в строку разделяя проебалми.
   В соответствии с answer_choices объетка question (см 5 endpoint)
   user_report_id это уникальный ID пользователя для получения и связывания с ним его репортов.

   **В запросе можно не указывать user_report_id, тогда он будет браться из request.user и устанавливаться автоматически.
   Или устанавливаться как null**

Также есть метод **GET**
который возращает список всех опросников пройденных пользователем вызывается просто
`report/` всю необходимую информацю View берет из request.
Но в этот раз прямой связи нет у каждого user есть поле report_id, по которому он получает ответы.

8. `report/<int:pk>/` Метод для получения информации о конкретном отчете пользователя.
   Метод защищен, и не дает другим пользователям доступ к ответм других юзеров.
   т.к queryset фильтруется на основе уникально поля user модели.
   Но также предусмнотрнно что администратор может получить доступ к любому представлению.
   Вызывается просто: `report/23/` где 23 это id отчета.

9. `report/user_report_id/` Метод принимает только POST запросы в которых указывается user_report_id (уникальный id для
   каждого пользователя который связывает его ответы с его репортами).
   Разрешен только для аунтифицированных пользователей. Защищен от несанксионированного просмотра пользователей результатов
   других пользователей. При это на администратора таких ограничений нет
   Пример запроса
   ```json
   {
     "user_report_id": "123"
   }
   ```
