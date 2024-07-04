First-hello-user-jp =
     <b>{ $username }さん、</b>ようこそ！
 Добро пожаловать!

 Я – бот-помощник Анны-сэнсэй.
 Я помогу тебе тренировать японское произношение, слова и грамматику.
 Напиши мне фразы, которые хочешь выучить, а я сделаю из них набор тренировок.


First-hello-user-en =
 Hi, <b>{ $username }</b>
 Меня зовут мистер Хацу, я твой бот-помощник.
 Я помогу тебе легко запоминать новые слова, тренировать красивое произношение и научиться бегло говорить по-английски.

 Let's start!

hello-user-jp =
 <b>{ $username }さん</b>、日本語を勉強しましょう！
 Давай выберем следующую тренировку!


hello-user-en =
 <b>{ $username }</b>, let's go to the next level!
 Давай выберем следующую тренировку!

start-training-button = 💪 Exercise

phrase-management-button = 📝 Managing phrases for training 💎

subscribe-management-button = 🔔 Manage my subscription 💎

admin-settings-button = ⚙️ Settings (for admins)

admin-panel = Admin panel

user-management = 🧑‍🤝‍🧑 User management

add-general-category = 🆕 Add general category

add-main-image = 🖼 Add a main image

generate-image-button = 🖼 Сгенерировать изображение

generate-image-dialog = Напиши промпт и я сгенерирую изображение.

starting-generate-image = Начинаю генерацию изображения. Это может занять некоторое время...

generated-image = Вот сгенерированное изображение!

failed-generate-image = Извините, не удалось сгенерировать изображение.

add-main-image = Добавить главное изображение

managing-your-own-phrases-only-available-subscription = Managing your own phrases is only available by subscription.

command-cancel =
    You have completed your training.
 Press menu /start to continue

back = ◀️ Back

cancel = ↩️ Cancel

next = ▶️ Continue

save = ✅ Save

delite = ✅ Delite

repeat = 🔄 Repeat

training-dialog = Ты в разделе тренировок. Выбирай тренировку, и погнали!

pronunciation = 🗣 Произношение

vocabulary = 🎯 Лексика

translation = 🌍 Перевод

listening = 🔊 Прослушивание

pronunciation_training_dialog =
 Я отправлю тебе аудио с одной из твоих фраз. Послушай и повтори за мной как можно точнее.
 Отправь мне голосовое сообщение с этой фразой. Я проанализирую твоё произношение и пришлю график, где ты наглядно увидишь изменение высоты тона и скорость речи.
 Синий – график оригинала.
 Оранжевый – график твоего произношения.
 Под графиком я напишу оригинал фразы, перевод и комментарий к фразе, если есть.

 Тренируйся до тех пор, пока твоё произношение не совпадёт на графике с оригиналом.

 Если тебе сложно произнести какое-то слово или часть фразы, перейди в раздел «ПРОСЛУШИВАНИЕ», напиши мне сложную часть фразы, и я озвучу только её. Потренируйся в произношении и возвращайся сюда.

 Для начала выбирай категорию:

choose-phrase = Выбирай фразу или тренируй случайную.
 Чтобы выбрать другую категорию, нажми «НАЗАД».

random-phrase = 🎲 Случайная фраза

processing-message = Минуту, обрабатываю ваше сообщение...

image-caption = <b>Оригинал:</b>
 { $text_phrase }
 { $translation }

 <b>Ваш вариант:</b> { $answer_text }

 <b>Комментарий:</b> { $comment }

try-again = Попробуй ещё или нажми «НАЗАД», чтобы выбрать другую фразу.

listen-original = Послушай оригинал и отправь мне аудиосообщение с этой фразой.

no-phrases-available = No phrases available.

error-handler = Моя твоя не понимать 🤔

lexis-training-dialog =
 Раздел для тренировки лексики.
 Я убрал из твоих фраз одно или два слова и заменил их пробелами.
 Вспомни и отправь мне фразу целиком.

 Для начала выбирай категорию:

lexis-training =
    Вспомни фразу целиком и напиши её в сообщении.
 Чтобы перейти к следующему заданию, нажми «ПРОПУСТИТЬ»
 Чтобы выбрать другую категорию, нажми «НАЗАД».

selected-category = <b>Выбранная категория:</b> { $category }

lexis-training-phrase = Фраза:
 <strong>{ $with_gap_phrase }</strong>

training-translation = Перевод:
 <tg-spoiler>{ $translation }</tg-spoiler>

training-try-again = Попробуй еще раз ))

enter-answer-text = Введи текст ответа:

congratulations-spoken-answer = Ты произнес:
 { $answer }

 Ура!!! Ты лучший! 🥳

spoken-answer =
 Кажется ты произнес:
 { $answer}

congratulations = 🏆 Ура!!! Ты лучший! 🥳

listen = 🎧 Послушать

translate-training-dialog = Раздел для тренировки перевода.
 Я дам тебе перевод твоих фраз; вспомни и напиши их по-японски.
 Выбирай категорию:

translate-training = Введи перевод фразы.
 Чтобы перейти к следующему заданию, нажмите «ПРОПУСТИТЬ»
 Чтобы выбрать другую категорию, нажми «НАЗАД».

translate-training-phrase = Фраза:
 <strong>{ $translation }</strong>


listening-training-dialog = Раздел для тренировки слушания.
 Здесь нет заданий.
 Отправь мне слово или фразу, и я озвучу.

listen-repeat =
 Слушай и повторяй до тех пор, пока фраза не станет привычной.

phrase-limit = В эту категорию нельзя добавить фразы. Максимальное количество фраз: 15
 Удалите существующие фразы или создайте новую категорию.

phrase-management-dialog = Здесь ты можешь добавить фразы для тренировок.

 Все фразы хранятся в категориях.

 Нажми на категорию, чтобы добавить или удалить фразы.
 В каждую категорию можно добавить не больше 15 фраз.

 Выбери категорию или создай новую.

add-category-button = ➕ Добавить категорию

delite-category-button = ❌ Удаление категорий

editing-category = Категория: <b>{ $category }</b>

 Чтобы добавить новую фразу, нажми «ДОБАВИТЬ ФРАЗУ»
 Чтобы удалить, выбери фразы и нажми «УДАЛИТЬ ВЫБРАННОЕ»

add-phrase-button = ➕ Добавить фразу

delete-selected-button = ❌ Удалить выбранные

delete-selected-ones = <b>Удалить выбранные?</b>

delete-selected-category = <b>Удалить выбранные категории со всеми фразами</b>❓

delite-category = Выбери категории для удаления:
 ❗❗❗ Все фразы в выбранных категориях будут удалены

subscribe-button = Оформить подписку

change-subscribe-button = Изменить подписку

unsubscribe = Отменить подписку

subscribe-info-dialog = Твоя подписка: <b>{ $type_subscription }</b>
 Дата окончания: <b>{ $date_end }</b>

text-phrase = <b>Текст:</b> { $text_phrase }

input-text-phrase = 💬 Введи текст новой фразы:

input-translate = 🌐 Введи перевод новой фразы или жми "Пропустить" и я переведу автоматически:

translation-phrase = <b>Перевод:</b> { $translation }

add-comment = <b>Здесь можно добавить комментарий к фразе:</b>

summary-information = Суммарная информация
 <b>Выбранная категория:</b> { $category }
 <b>Текст:</b> { $text_phrase }
 <b>Перевод:</b> { $translation }
 <b>Комментарий:</b> { $comment }
 <b>Сохранить фразу?</b>

add-audio = <b>Добавление аудио</b>

add-audio-info-first = 🔊 Отправь мне аудио новой фразы, голосовое сообщение или нажми <b>Озвучить с помощью ИИ</b>.

add-audio-info-second = Если все ОК, жми <b>Продолжить</b> или отправь еще раз

voice-with-ai-button = 🤖 Озвучить с помощью ИИ

add-image-info = <b>🎨 Отправь иллюстрацию для фразы, сгенерируй при помощи ИИ или просто пропусти этот шаг:</b>