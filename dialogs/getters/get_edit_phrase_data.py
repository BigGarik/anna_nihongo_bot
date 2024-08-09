import logging
import os

from aiogram_dialog import DialogManager
from dotenv import load_dotenv

from models import Phrase, Category, User, Subscription

load_dotenv()
logger = logging.getLogger('default')


async def get_data(dialog_manager: DialogManager, **kwargs):
    response = {}
    # Если есть ключ phrase_id в старт дата значит перешли из менеджера фраз
    if dialog_manager.start_data.get("phrase_id"):
        msg_photo_id = dialog_manager.start_data.get("msg_photo_id")
        msg_audio_id = dialog_manager.start_data.get("msg_audio_id")
        phrase_id = dialog_manager.start_data.get("phrase_id")
        dialog_manager.start_data.clear()
        response['phrase_id'] = phrase_id
        if msg_photo_id:
            response['msg_photo_id'] = msg_photo_id
        if msg_audio_id:
            response['msg_audio_id'] = msg_audio_id
        phrase = await Phrase.get(id=phrase_id).prefetch_related('category')
        if phrase:
            category_id = phrase.category_id
            response["category_id"] = category_id
            category = await Category.get_or_none(id=category_id)
            response["category"] = category.name
            text_phrase = phrase.text_phrase
            response["text_phrase"] = text_phrase
            translation = phrase.translation or ""
            response["translation"] = translation
            comment = phrase.comment or ""
            response["comment"] = comment
            if phrase.audio_id:
                audio_id = phrase.audio_id
                response["audio_id"] = audio_id
            if phrase.image_id:
                image_id = phrase.image_id
                response["image_id"] = image_id
            prompt = phrase.translation or phrase.text_phrase
            response["prompt"] = prompt
            dialog_manager.dialog_data.update(response)
    # Иначе перешли из диалога добавления фразы и она еще не сохранена в базе данных
    else:
        if dialog_manager.dialog_data.get('category_id'):
            response['category_id'] = dialog_manager.dialog_data['category_id']
        else:
            response['category_id'] = dialog_manager.start_data.get('category_id')

        if dialog_manager.dialog_data.get('category'):
            response['category'] = dialog_manager.dialog_data['category']
        else:
            response['category'] = dialog_manager.start_data.get('category')

        if dialog_manager.dialog_data.get('text_phrase'):
            response['text_phrase'] = dialog_manager.dialog_data['text_phrase']
        else:
            response['text_phrase'] = dialog_manager.start_data.get('text_phrase')

        if dialog_manager.dialog_data.get('spaced_phrase'):
            response['spaced_phrase'] = dialog_manager.dialog_data['spaced_phrase']
        else:
            response['spaced_phrase'] = dialog_manager.start_data.get('spaced_phrase')

        if dialog_manager.dialog_data.get('translation'):
            response['translation'] = dialog_manager.dialog_data['translation']
        else:
            response['translation'] = dialog_manager.start_data.get('translation')

        if dialog_manager.dialog_data.get('prompt'):
            response['prompt'] = dialog_manager.dialog_data['prompt']
        else:
            response['prompt'] = dialog_manager.start_data.get('prompt')

        if dialog_manager.dialog_data.get('audio_id'):
            response['audio_id'] = dialog_manager.dialog_data['audio_id']
        else:
            response['audio_id'] = dialog_manager.start_data.get('audio_tg_id')

        if dialog_manager.dialog_data.get('image_id'):
            response['image_id'] = dialog_manager.dialog_data['image_id']
        else:
            response['image_id'] = dialog_manager.start_data.get('image_id')

        if dialog_manager.dialog_data.get('comment'):
            response['comment'] = dialog_manager.dialog_data['comment']
        else:
            response['comment'] = dialog_manager.start_data.get('comment')
        dialog_manager.dialog_data.update(response)

    subscription = await Subscription.get(user_id=dialog_manager.event.from_user.id).prefetch_related('type_subscription')
    if subscription.type_subscription.name != 'Free':
        dialog_manager.dialog_data['is_subscriber'] = True

    return dialog_manager.dialog_data

