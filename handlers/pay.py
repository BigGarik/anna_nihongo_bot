import logging
import os
from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from dotenv import load_dotenv

load_dotenv()

router = Router()
logger = logging.getLogger('default')


# @router.callback_query()
async def order(callback: CallbackQuery, bot: Bot):
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="Тест платежа",
        description="Описание платежа",
        payload='Платеж через бота',
        provider_token=os.getenv("PROVIDER_TOKEN"),
        currency="RUB",
        prices=[
            LabeledPrice(
                label="1 месяц",
                amount=int(os.getenv("PRICE_ONE_MONTH"))  # Corrected typo in env variable name
            ),
        ],
        start_parameter="test",
        provider_data=None,
        photo_url=None,
        photo_size=100,
        need_name=False,
        need_phone_number=False,
        need_email=False,
        need_shipping_address=False,
        send_phone_number_to_provider=False,
        send_email_to_provider=False,
        is_flexible=False,
        disable_notification=False,
        protect_content=False,
        allow_sending_without_reply=True,
        request_timeout=60,
    )


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    print(pre_checkout_query)


@router.message(F.successful_payment)
async def success_payment(message: Message):
    msg = f'Спасибо за оплату {message.successful_payment.total_amount // 100} {message.successful_payment.currency}'
    await message.answer(msg)
    print(msg)
