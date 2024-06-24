import logging

from aiogram import Router
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Cancel, Start
from aiogram_dialog.widgets.text import Const

from states import AddOriginalPhraseSG, AdminDialogSG

# Инициализируем роутер уровня модуля
router = Router()

logger = logging.getLogger(__name__)

admin_dialog = Dialog(
    Window(
        Const('Админка'),

        Start(Const('🆕 Добавить оригинальную фразу'),
              id='go_add_original_phrase_dialog',
              state=AddOriginalPhraseSG.text_phrase
              ),
        Cancel(Const('↩️ Отмена'), id='button_cancel'),
        state=AdminDialogSG.start,
    ),
)
