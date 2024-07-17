import logging
import random
from datetime import datetime, timedelta

import pytz
from aiogram_dialog import DialogManager
from dotenv import load_dotenv

from models import Phrase, Category, ReviewStatus

from services.services import replace_random_words

load_dotenv()
logger = logging.getLogger(__name__)


async def select_phrase_for_interval_training(user_id, category_id, dialog_manager: DialogManager) -> Phrase:
    intervals = [
        timedelta(minutes=15),
        timedelta(hours=6),
        timedelta(days=1),
        timedelta(days=2),
        timedelta(days=8),
        timedelta(weeks=3),
        timedelta(days=60)
    ]

    now = datetime.now(pytz.UTC)

    # 1. Выбираем все фразы из категории
    all_phrases = await Phrase.filter(category_id=category_id).all()

    # 2. Исключаем последнюю введенную фразу, если она есть
    last_phrase = dialog_manager.dialog_data.get('question')
    if last_phrase:
        all_phrases = [phrase for phrase in all_phrases if phrase.text_phrase != last_phrase]

    # if not all_phrases:
    #     logger.warning("No phrases available in the category after excluding the last phrase.")
    #     return None

    # 3. Получаем все статусы повторений для пользователя и фраз в этой категории
    phrase_ids = [phrase.id for phrase in all_phrases]
    review_statuses = await ReviewStatus.filter(
        user_id=user_id,
        phrase_id__in=phrase_ids
    ).prefetch_related('phrase')

    # 4. Находим фразы, которые нужно повторить
    phrases_to_review = []
    for status in review_statuses:
        if status.review_count < len(intervals) and now >= status.next_review:
            phrases_to_review.append((status.phrase, status.next_review))

    if phrases_to_review:
        # Выбираем фразу с самой ранней датой следующего повторения
        chosen_phrase, _ = min(phrases_to_review, key=lambda x: x[1])
    else:
        # Если нет фраз для повторения, выбираем случайную из тех, которые еще не изучались
        studied_phrase_ids = [status.phrase_id for status in review_statuses]
        unstudied_phrases = [phrase for phrase in all_phrases if phrase.id not in studied_phrase_ids]
        if unstudied_phrases:
            chosen_phrase = random.choice(unstudied_phrases)
        else:
            # Если все фразы уже изучались, выбираем случайную
            chosen_phrase = random.choice(all_phrases)

    # Обновляем данные диалога
    dialog_manager.dialog_data['with_gap_phrase'] = replace_random_words(chosen_phrase.spaced_phrase)
    dialog_manager.dialog_data['question'] = chosen_phrase.text_phrase
    dialog_manager.dialog_data['audio_id'] = chosen_phrase.audio_id
    dialog_manager.dialog_data['translation'] = chosen_phrase.translation
    dialog_manager.dialog_data['counter'] = 0

    category = await Category.get(id=category_id)
    dialog_manager.dialog_data['category'] = category.name
    dialog_manager.dialog_data['category_id'] = category_id


if __name__ == '__main__':
    pass
