# Authorization
Authorization/Registration


app
    План приложения.
        1. Регистрация
            Заполняем обязательные поля для создания нового пользователя.
                username - uniq
                password
                password2
                email - uniq
            создаётся новый пользователь в базе.
            Отправка сообщения на указанный email для подтверждения.
                В email должен указываться юзернэйм.
        2. Смена пароля
            2.1
                Для сменны пароля требуется указать свой username и email. 
                Далее на email отправляется письмо с сылкой на страницу изменения пароля.
            2.2   
                Указывается старый пароль
                На страницы изменения пароля водится новый пароль password
                еще раз ввод нового пароля password2
                изменения сохраняютсяю в базу.
                Отправляется email с сообщением о изменении пароля.
        3. Смена email.
            2.1
                Для смены email в поле указывается новый email
                По указанному адерссу отправляется email с сылкой на подтверждение.
            2.2
                После перехода по ссылке email будет изменнён. 
        4. Удаление пользователя.(+)
            Для удаления заполняются поля username and password.
            Происходит удаление.
        5. Редактирование профайла пользователя. Готово(+)
            Заполняются поля личной информацией с последующим сохранением.
        6. Востановить пароль. Готово(+)
            2.1
                Для сменны пароля требуется указать свой username и email. 
                Далее на email отправляется письмо с сылкой на страницу изменения пароля.
            2.2
                На страницы изменения пароля водится новый пароль password
                еще раз ввод нового пароля password2
                изменения сохраняютсяю в базу.
                Отправляется email с сообщением о изменении пароля.
        


поменять названия ченьдж и рековери пасс.
Написать тесты к АПИ
Верифай



MODELS
    User
        username
        email
        verified
        secret_code
    Profile
        firstname
        lastname
        age
        avatar
        date_joined    