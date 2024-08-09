import logging
import random
from datetime import datetime

import pytz
from aiogram_dialog import DialogManager, ShowMode
from dotenv import load_dotenv

from config_data.config import INTERVALS
from handlers.system_handlers import check_day_counter
from models import Phrase, ReviewStatus, UserAnswer
from services.services import normalize_text
from states import IntervalTrainingSG

load_dotenv()
logger = logging.getLogger('default')


async def check_user_answer(answer_text: str, phrase: Phrase, user, training_selected):
    normalized_question = normalize_text(phrase.text_phrase)
    normalized_answer = normalize_text(answer_text)
    now = datetime.now(pytz.UTC)

    review_status = await ReviewStatus.get_or_none(user=user, phrase=phrase)

    if review_status:
        if normalized_question == normalized_answer:
            result = True
            review_status.review_count = min(review_status.review_count + 1, len(INTERVALS) - 1)
        else:
            result = False
            review_status.review_count = max(review_status.review_count - 1, 0)
        review_status.next_review = now + INTERVALS[review_status.review_count]
    else:
        result = normalized_question == normalized_answer
        review_status = ReviewStatus(
            user=user,
            phrase=phrase,
            review_count=0,
            next_review=now + INTERVALS[0]
        )
    review_status.note = False
    await review_status.save()
    await UserAnswer.create(
        user=user,
        phrase=phrase,
        answer_text=answer_text,
        exercise=training_selected,
        result=result,
    )
    return result


async def select_phrase_for_interval_training(user_id, dialog_manager: DialogManager):
    now = datetime.now(pytz.UTC)

    # 1. Выбираем все фразы из категории
    # all_phrases = await Phrase.filter(user_id=user_id).all()
    all_phrases = await Phrase.filter(user_id=user_id, category__public=False).prefetch_related('category')
    logger.debug(f'All phrases: {all_phrases}')

    # 2. Исключаем последнюю введенную фразу, если она есть
    last_phrase = dialog_manager.dialog_data.get('question')
    if last_phrase:
        all_phrases = [phrase for phrase in all_phrases if phrase.text_phrase != last_phrase]
        logger.debug(f'Phrase without last phrase: {all_phrases}')

    # 3. Получаем все статусы повторений для пользователя и фраз
    phrase_ids = [phrase.id for phrase in all_phrases]
    review_statuses = await ReviewStatus.filter(
        user_id=user_id,
        phrase_id__in=phrase_ids
    ).prefetch_related('phrase')
    logger.debug(f'Review statuses: {review_statuses}')

    # 4. Находим фразы, которые нужно повторить
    phrases_to_review = []
    for status in review_statuses:
        print(status.next_review)
        if status.review_count < len(INTERVALS) and now >= status.next_review:
            phrases_to_review.append((status.phrase, status.next_review))
    logger.debug(f'Phrases to review: {phrases_to_review}')
    if phrases_to_review:
        # Выбираем фразу с самой ранней датой следующего повторения
        chosen_phrase, _ = min(phrases_to_review, key=lambda x: x[1])
        logger.debug(f'Chosen phrase: {chosen_phrase}')
    else:
        # Если нет фраз для повторения, выбираем случайную из тех, которые еще не изучались
        studied_phrase_ids = [status.phrase_id for status in review_statuses]
        logger.debug(f'Studied phrase ids: {studied_phrase_ids}')
        unstudied_phrases = [phrase for phrase in all_phrases if phrase.id not in studied_phrase_ids]
        logger.debug(f'Unstudied phrases: {unstudied_phrases}')
        if unstudied_phrases:
            chosen_phrase = random.choice(unstudied_phrases)
            logger.debug(f'Chosen phrase: {chosen_phrase}')
        else:
            # Если все фразы уже изучались, выбираем случайную
            chosen_phrase = random.choice(all_phrases)
            logger.debug(f'Chosen phrase: {chosen_phrase}')

    return chosen_phrase.id


async def translation_training(dialog_manager: DialogManager):
    phrase_id = dialog_manager.dialog_data['phrase_id']
    training_selected = dialog_manager.dialog_data['training_selected']
    data = {'phrase_id': phrase_id, 'training_selected': training_selected}
    await dialog_manager.start(state=IntervalTrainingSG.translation, data=data)


async def listening_training(dialog_manager: DialogManager):
    phrase_id = dialog_manager.dialog_data['phrase_id']
    phrase = await Phrase.get(id=phrase_id)
    if not phrase.audio_id:
        # TODO озвучить, отправить и сохранить ид в базу
        pass
    dialog_manager.dialog_data['phrase_id'] = phrase_id
    training_selected = dialog_manager.dialog_data['training_selected']
    data = {'phrase_id': phrase_id, 'training_selected': training_selected}
    await dialog_manager.start(state=IntervalTrainingSG.listening, data=data, show_mode=ShowMode.SEND)


async def lexis_training(dialog_manager: DialogManager):
    phrase_id = dialog_manager.dialog_data['phrase_id']
    training_selected = dialog_manager.dialog_data['training_selected']
    data = {'phrase_id': phrase_id, 'training_selected': training_selected}
    await dialog_manager.start(state=IntervalTrainingSG.lexis, data=data)


async def pronunciation_training(dialog_manager: DialogManager):
    phrase_id = dialog_manager.dialog_data['phrase_id']
    training_selected = dialog_manager.dialog_data['training_selected']
    data = {'phrase_id': phrase_id, 'training_selected': training_selected}
    await dialog_manager.start(state=IntervalTrainingSG.pronunciation, data=data)


async def pronunciation_text_training(dialog_manager: DialogManager):
    phrase_id = dialog_manager.dialog_data['phrase_id']
    training_selected = dialog_manager.dialog_data['training_selected']
    data = {'phrase_id': phrase_id, 'training_selected': training_selected}
    await dialog_manager.start(state=IntervalTrainingSG.pronunciation_text, data=data)


async def start_training(dialog_manager: DialogManager) -> None:
    user_id = dialog_manager.event.from_user.id
    is_day_counter = await check_day_counter(dialog_manager)
    if is_day_counter:
        phrase_id = await select_phrase_for_interval_training(user_id, dialog_manager)
        dialog_manager.dialog_data['phrase_id'] = phrase_id
        review_status = await ReviewStatus.get_or_none(user_id=user_id, phrase_id=phrase_id)

        # Получаем предыдущую тренировку, если она была
        previous_training = dialog_manager.dialog_data.get('training_selected')

        if review_status:
            if review_status.review_count > 5:
                training_selected = 'translation'
            elif review_status.review_count < 3:
                training_type = ['listening', 'lexis', 'pronunciation', 'pronunciation_text']
                if previous_training in training_type:
                    training_type.remove(previous_training)
                training_selected = random.choice(training_type)
            else:
                training_type = ['translation', 'listening', 'lexis', 'pronunciation', 'pronunciation_text']
                # Удаляем предыдущую тренировку из списка, если она там есть
                if previous_training in training_type:
                    training_type.remove(previous_training)
                training_selected = random.choice(training_type)
        else:
            training_type = ['listening', 'lexis', 'pronunciation', 'pronunciation_text']
            # Удаляем предыдущую тренировку из списка, если она там есть
            if previous_training in training_type:
                training_type.remove(previous_training)
            training_selected = random.choice(training_type)

        dialog_manager.dialog_data['training_selected'] = training_selected

        # Запуск соответствующей функции обучения
        if training_selected == 'translation':
            await translation_training(dialog_manager)
        elif training_selected == 'listening':
            await listening_training(dialog_manager)
        elif training_selected == 'lexis':
            await lexis_training(dialog_manager)
        elif training_selected == 'pronunciation':
            await pronunciation_training(dialog_manager)
        elif training_selected == 'pronunciation_text':
            await pronunciation_text_training(dialog_manager)
        else:
            logger.error(f'Неизвестный тип тренировки: {training_selected}')


if __name__ == '__main__':
    pass
