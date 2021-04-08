from dotenv import load_dotenv
from telegram.ext import Updater, MessageHandler, Filters
import os
from geocoder import get_ll_span

load_dotenv()


def geocoder(update, context):
    ll, spn = get_ll_span(update.message.text)
    static_api_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l=map"
    context.bot.send_photo(
        update.message.chat_id,
        static_api_request,
        caption="Нашёл:"
    )


def main():
    updater = Updater(os.getenv("TOKEN"), use_context=True)
    dp = updater.dispatcher
    text_handler = MessageHandler(Filters.text, geocoder)
    dp.add_handler(text_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
