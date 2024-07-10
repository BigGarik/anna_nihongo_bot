command-start = Let's start training

command-language = Language selection

command-cancel = Complete training

First-hello-user-jp =
     <b>{ $username }さん、</b>ようこそ！
 Welcome!

 My name is Hatsu.
 I'll help you perfect your Japanese pronunciation, grammar and vocabulary.
 Give me the phrases you want to practice and I'll make exercises for you.

 じゃ、始めましょう！

First-hello-user-en =
 Hi, <b>{ $username }</b>!

 My name is Hatsu.
 I'll help you perfect your English pronunciation, grammar and vocabulary.
 Give me the phrases you want to practice and I'll make exercises for you.

 Let's start!

hello-user-jp =
 <b>{ $username }さん</b>、日本語を勉強しましょう！
 It's time to study Japanese!

 Tap EXERCISES to start a new training.
 Tap MANAGE PHRASES FOR MY EXERCISES to add or delete phrases.

hello-user-en =
 <b>{ $username }</b>, let's go to the next level!
 Choose your next exercise!

start-training-button = 💪 Exercises

phrase-management-button = 📝 Manage phrases for my exercises 💎

subscribe-management-button = 🔔 Manage my subscription 💎

admin-settings-button = ⚙️ Settings (for admins)

admin-panel = Admin panel

user-management = ‍🧑‍🤝‍🧑 Manage users

add-general-category = 🆕 Add general category

generate-image-button = 🖼 Generate AI image

generate-image-dialog = Send me a prompt and I'll generate an image for you.

starting-generate-image = Starting image generation. It can take few minutes...

generated-image = Here is your image!

failed-generate-image = I'm sorry, I couldn't generate this image. This function is running in test mode. Please try again later.

add-main-image = Add main image

managing-your-own-phrases-only-available-subscription = Managing phrases is available in Pro-version.

command-cancel =
    You've finnished your training.
 Press /start in the menu to continue.

back = ◀️ Back

cancel = ↩️ Cancel

next = ▶️ Next

save = ✅ Save

delite = ✅ Delete

repeat = 🔄 Repeat

training-dialog = Here are the exercises. Choose your next exercise and let's go!

pronunciation = 🗣 Pronunciation

vocabulary = 🎯 Vocabulary

translation = 🌍 Back translation

listening = 🔊 Listening

pronunciation_training_dialog =
 I will send you an audio with one of your phrases. Listen and try to repeat it.
 When you are ready send me a voice message where you are saying this phrase.
 I'll analyse it and provide you with a graph where you can see comparison of your speed and voice pitch to the original sound.
 Blue - original sound
 Orange - your message
 Under the graph you'll find the original phrase, it's translation, and comment if there is any.

 Continue practicing until the two graphs become similar.

 Choose a category:

choose-phrase = Choose a phrase or practice with a random one.

 Tap BACK to choose different category.

random-phrase = 🎲 Random phrase

processing-message = Analysing your message...

image-caption = <b>Original phrase:</b>
 { $text_phrase }
 { $translation }

 <b>You said:</b> { $answer_text }

 <b>Comment:</b> { $comment }

try-again = Try again or tap BACK to choose another phrase.

listen-original = Listen and send me a voice message where you're saying this phrase.

no-phrases-available = No phrases available.

error-handler = Come again? I didn't quite catch it 🤔

lexis-training-dialog =
 Here you can practice vocabulary.
 I've gapped one or two words in your phrases.
 Try to remember the original phrase and send it me.
 Please, write the whole phrase.

 First, choose a category:

lexis-training =
    Try to remember the whole phrase and write it to me.
 Tap SKIP to go to the next task.
 Tap BACK to choose another category.

selected-category = <b>Selected category:</b> { $category }

lexis-training-phrase = Phrase:
 <strong>{ $with_gap_phrase }</strong>

training-translation = Translation:
 <tg-spoiler>{ $translation }</tg-spoiler>

training-try-again = Try again!

enter-answer-text = Enter your answer:

congratulations-spoken-answer = You said:
 { $answer }

 Great job!!! 🥳

spoken-answer =
 You said what sounded like:
 { $answer}

congratulations = 🏆 Great job!!! 🥳

listen = 🎧 Listen

translate-training-dialog = Here you can practice back translation.
 You will see the translation of your phrase. Remember the original phrase and write it to me.
 Choose a category:

translate-training = Enter this phrase in English.
 Tap SKIP to go to the next task.
 Tap BACK to choose another category.

translate-training-phrase = Phrase:
 <strong>{ $translation }</strong>


listening-training-dialog = Here you can practice listening.
 There are no tasks here.
 Write me a word or a phrase you want to listen, and I'll voice it for you.

listen-repeat =
 Listen and repeat until you get used to the way it sounds.

phrase-limit = You can not add new phrases to this category. Maximum number of phrases in each category is 15.
 Delete some of the existing phrases from this category or create a new one.

phrase-management-dialog = Here you can add phrases for your exercises.

 All of the phrases are stocked in categories.

 Tap on the category to add or delete phrases.
 You can add up to 15 phrases to each category.

 Choose a category or create a new one.

add-category-button = ➕ Create new category

delite-category-button = ❌ Delete category

editing-category = Category: <b>{ $category }</b>

 Tap ADD PHRASE to add a new phrase
 Tap on the phrases you want to delete and then tap DELETE SELECTION

add-phrase-button = ➕ Add new phrase

delete-selected-button = ❌ Delete selection

delete-selected-ones = <b>Delete selected phrases?</b>

delete-selected-category = <b>Delete selected categories with all the phrases</b>❓

delite-category = Choose the category you want to delete:
 ❗❗❗ All the phrases in the selected categories will also be deleted.

subscribe-button = Subscribe

change-subscribe-button = Manage my subscription

unsubscribe = Unsubscribe

user-subscribe-info-dialog = You subscription type: <b>{ $type_subscription }</b>
 Subscription period ends on: <b>{ $date_end }</b>

text-phrase = <b>Phrase:</b> { $text_phrase }

input-text-phrase = 💬 Enter new phrase:

input-translate = 🌐 Enter translation or tap SKIP and I'll translate it for you:

translation-phrase = <b>Translation:</b> { $translation }

add-comment = <b>Here you can add a comment:</b>

summary-information = Summary:
 <b>Category:</b> { $category }
 <b>Phrase:</b> { $text_phrase }
 <b>Translation:</b> { $translation }
 <b>Comment:</b> { $comment }
 <b>Save this phrase?</b>

add-audio = <b>Add audio</b>

add-audio-info-first = 🔊 Send me a audio file or an voice message with the new phrase or tap on <b>VOICE USING AI</b>.

add-audio-info-second = Chack the sound and tap <b>CONTINUE</b> or send me another audio message.

voice-with-ai-button = 🤖 Voice using AI

add-image-info = <b>🎨 Send me an image for your phrase, generate the image using AI, or just skip this step:</b>




en = 🇬🇧 English

ru = 🇷🇺 Russian

select-language = Select bot language

language-changed = Language changed to


summary-information-to-edit = Суммарная информация
 <b>Выбранная категория:</b> { $category }
 <b>Текст:</b> { $text_phrase }
 <b>Перевод:</b> { $translation }
 <b>Комментарий:</b> { $comment }
 Выбирай, что редактировать.

select-phrase-to-delete = Select to delete

text-phrase-to-edit = Phrase text

translation-to-edit = Translation

audio-to-edit = Audio

image-to-edit = Photo

comment-to-edit = Comment

send-text-phrase-to-edit = Отправь текст фразы для изменения

send-translation-to-edit = Отправь перевод для изменения

send-audio-to-edit = Отправь аудио или голосовое сообщение для изменения

send-image-to-edit = Отправь фото или сгенерируй новое для изменения

send-comment-to-edit = Отправь комментарий для изменения

one-month-subscription-button = Подписка на 1 месяц

one-month-subscription-description = Подписка на один месяц

three-month-subscription-button = Подписка на 3 месяца

three-month-subscription-description = Подписка на три месяца

six-month-subscription-button = Подписка на 6 месяцев

six-month-subscription-description = Подписка на шесть месяцев

error-adding-category = Error adding category

you-already-have-category = You already have such a category

category-added-successfully = Category added successfully

enter-name-new-category = Enter the name of the new category:

already-added-this-phrase = You have already added this phrase. Try something else 😉

failed-save-phrase = Error when saving phrase

phrase-saved = Фраза добавлена! ✅

voice-acting = Voice acting