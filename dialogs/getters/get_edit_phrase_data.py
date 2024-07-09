import logging
import os

from aiogram_dialog import DialogManager
from dotenv import load_dotenv

from models import Phrase, Category

load_dotenv()
logger = logging.getLogger(__name__)


async def get_data(dialog_manager: DialogManager, **kwargs):
    if not dialog_manager.dialog_data.get('text_phrase'):
        phrase_id = dialog_manager.start_data.get("phrase_id")
        dialog_manager.dialog_data['phrase_id'] = phrase_id
        phrase = await Phrase.get(id=phrase_id).prefetch_related('category')
        if phrase:
            category_id = phrase.category_id
            category = await Category.get_or_none(id=category_id)
            dialog_manager.dialog_data["category"] = category.name
            text_phrase = phrase.text_phrase
            dialog_manager.dialog_data["text_phrase"] = text_phrase
            translation = phrase.translation or ""
            dialog_manager.dialog_data["translation"] = translation
            comment = phrase.comment or ""
            dialog_manager.dialog_data["comment"] = comment
            if phrase.audio_id:
                audio_id = phrase.audio_id
                dialog_manager.dialog_data["audio_id"] = audio_id
            if phrase.image_id:
                image_id = phrase.image_id
                dialog_manager.dialog_data["image_id"] = image_id
            prompt = phrase.translation or phrase.text_phrase
            dialog_manager.dialog_data["prompt"] = prompt

            return dialog_manager.dialog_data
    else:
        return dialog_manager.dialog_data
