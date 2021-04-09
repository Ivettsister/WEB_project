from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
import os
from geocoder import get_ll_span
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

load_dotenv()
keyboard1 = [['Пропустить']]
keyboard2 = [['Показать на карте'], ['Посчитать время на дорогу'], ['Погода'], ['Расписания'],
             ['Вернуться назад']]
keyboard3 = [['Вернуться назад']]
keyboard4 = [['Текущая погода'], ['Прогноз на n дней'], ['Вернуться назад']]
keyboard5 = [['Найти авиарейс'], ['Вернуться назад']]
keyboard7 = [['Настройка ключевых слов'], ['Настройка города'], ['Вернуться назад']]

inline_maps = InlineKeyboardMarkup([
    [InlineKeyboardButton('Карта', callback_data='map')],
    [InlineKeyboardButton('Спутник', callback_data='sat')],
    [InlineKeyboardButton('Гибрид', callback_data='sat,skl')],
])


"""def geocoder(update, context):
    ll, spn = get_ll_span(update.message.text)
    static_api_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l=map"
    context.bot.send_photo(
        update.message.chat_id,
        static_api_request,
        caption="Нашёл:"
    )"""


def start(bot, update):
    update.message.reply_text(
        'Как Вас зовут?', reply_markup=ReplyKeyboardMarkup(keyboard1), one_time_keyboard=False)
    return ENTER_NAME


def enter_name(bot, update, user_data):
    name = update.message.text
    if name != 'Пропустить':
        user_data['username'] = name
    else:
        user_data['username'] = None

        update.message.reply_text('В каком городе Вы находитесь?')
        pass


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater(os.getenv("TOKEN"), use_context=True)
    dp = updater.dispatcher
    dp.add_error_handler(error)
    dp.add_handler(conversation_handler)
    updater.start_polling()
    updater.idle()


def stop(bot, update):
    update.message.reply_text('Пока!', reply_markup=ReplyKeyboardRemove())
    update.message.reply_text('Для того, чтобы начать работу с ботом заново напишите /start')
    return ConversationHandler.END


conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)], states={
        ENTER_NAME: [MessageHandler(Filters.text, enter_name, pass_user_data=True)]
    },
    fallbacks=[CommandHandler('stop', stop)]
)


if __name__ == '__main__':
    main()
