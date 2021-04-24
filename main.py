from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
import os
from maps_api.geocoder import get_ll_span, get_city, get_country_code
from weather import get_current_weather, get_forecast_weather
from Keyboard import keyboard1, keyboard2, keyboard3, keyboard4, keyboard5, keyboard6, keyboard7,\
    inline_maps, reply_keyboard

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

info_about_bot = 'Этот бот, создан для помощи в ориентировании на местности.\nон может'+\
                 ' предоставить карту по адресу запрошенного места, посчитать время на'+\
                 ' дорогу до этого места (если вы предоставите свою геолокацию) и показать'+\
                 ' прогноз погоды.'

def location(update, context):
    return update.message.location


def help(update): # пока что не работает вроде, в прочем как и /stop
    update.message.reply_text(info_about_bot)


def start(update, context):
    update.message.reply_text(
        'Вас приветсвует бот, созданный для помощи в ориентировании на местности.\n' +
        'Я могу предоставить карту по адресу запрошенного места, посчитать время на дорогу до этого' +
        ' места (если вы предоставите свою геолокацию) и предоставить прогноз погоды.',
        reply_markup=ReplyKeyboardMarkup(keyboard1,
                                         one_time_keyboard=True,
                                         resize_keyboard=True))
    return ENTER_NAME


def enter_name(update, context):
    name = update.message.text
    if name != 'Пропустить':
        context.user_data['username'] = name
    else:
        context.user_data['username'] = None
    update.message.reply_text('Где вы сейчас находитесь?', reply_markup=reply_keyboard)

    return ENTER_LOCATION


def enter_location(update, context):
    answer = update.message.text
    if answer == 'Предоставить Геолокацию':
        loc = location(update, context)
        context.user_data['location'] = loc
    elif answer != 'Пропустить':
        context.user_data['location'] = answer
        # keyboard6.append([answer]) в keyboard7 заменено на кнопку "Мое местоположение"
    else:
        context.user_data['location'] = None
    name = ', {}'.format(context.user_data['username']) if context.user_data[
                                                               'username'] is not None else ''
    update.message.reply_text('Добро пожаловать{}!'.format(name),
                              reply_markup=ReplyKeyboardMarkup(keyboard2))
    return MAIN_MENU


def main_menu(update):
    text = update.message.text
    if text == 'Показать на карте':
        update.message.reply_text(
            'Выберите или введите, что мне показывать (при выборе своего местоположения'+
            ' обратите внимание, что используется, тот адрес который вы указывали ранее,'+
            ' в случае необходимости обновите свое местоположение в главном меню)',
            reply_markup=ReplyKeyboardMarkup(keyboard7, resize_keyboard=True))
        return STATIC_PHOTO

    elif text == 'Найти ближайшую организацию':
        update.message.reply_text(
            'Выберите, от какой точки мне производить поиск:',
            reply_markup=ReplyKeyboardMarkup(keyboard6)
        )
        pass

    elif text == 'Погода':
        update.message.reply_text(
            'Выберите параметры, которые Вы хотите настроить',
            reply_markup=ReplyKeyboardMarkup(keyboard4)
        )
        return WEATHER_HANDLER

    elif text == 'Посчитать время на дорогу':
        update.message.reply_text(
            'Выберите параметры, которые Вы хотите настроить',
            reply_markup=ReplyKeyboardMarkup(keyboard5)
        )
        pass

    elif text == 'Вернуться назад':
        update.message.reply_text('Где вы сейчас находитесь?', reply_markup=reply_keyboard)
        return ENTER_LOCATION
    return MAIN_MENU


def static_photo(update, context):
    text = update.message.text
    if text == 'Мое расположение':
        if context.user_data['location'] is not None:
            text = context.user_data['location']
        else:
            update.message.reply_text('Вы не предоставляли собственного местоположения.')
            text = 'Вернуться назад'
    if text == 'Вернуться назад':
        update.message.reply_text('Возвращаю вас в главное меню...',
                                  reply_markup=ReplyKeyboardMarkup(keyboard2))
        return MAIN_MENU
    else:
        if 'need_adresses' in context.user_data.keys():
            context.user_data['need_adresses'].append(text)
        else:
            context.user_data['need_adresses'] = [text]
        update.message.reply_text('Выберите тип карты снимка:', reply_markup=inline_maps)
    # return STATIC_PHOTO


def get_photo_handler(update, context):
    query = update.callback_query
    context.user_data['need_maptype'] = query.data
    ll, spn = get_ll_span(context.user_data['need_adresses'][-1])
    static_api_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l={context.user_data['need_maptype']}"
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="[​​​​​​​​​​​]{}".format(static_api_request, 'Нашёл:'),
        parse_mode='markdown',
        reply_markup=inline_maps
    )


def need_adress(update, context):
    return static_photo(update, context)


def weather(update, context):
    text = update.message.text
    if text == 'Текущая погода':
        city, code = get_city(context.user_data['location']), get_country_code(context.user_data['location'])
        update.message.reply_text(
            get_current_weather(city, code, os.getenv("WEATHER_TOKEN"), get_city(context.user_data['location'], 'ru-RU')))
    elif text == 'Прогноз на 6 дней':
        city, code = get_city(context.user_data['location']), get_country_code(context.user_data['location'])
        update.message.reply_text(
            get_forecast_weather(city, code, os.getenv("WEATHER_TOKEN"),
                                 get_city(context.user_data['location'], 'ru-RU')))
    elif text == 'Вернуться назад':
        update.message.reply_text('Возвращаю вас в главное меню...)', reply_markup=ReplyKeyboardMarkup(keyboard2))
        return MAIN_MENU


def stop(update):
    update.message.reply_text('Пока!', reply_markup=ReplyKeyboardRemove())
    update.message.reply_text('Для того, чтобы начать работу с ботом заново напишите /start')
    return ConversationHandler.END


def main():
    updater = Updater(os.getenv("TELEGRAMM_TOKEN"), use_context=True)
    dp = updater.dispatcher
    dp.add_handler(conversation_handler)
    updater.start_polling()
    updater.idle()


(
    ENTER_NAME, ENTER_LOCATION, MAIN_MENU, STATIC_PHOTO, NEED_ADRESS, WEATHER_HANDLER
) = range(6)


conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],

    states={
        ENTER_NAME: [MessageHandler(Filters.text, enter_name, pass_user_data=True)],
        MAIN_MENU: [MessageHandler(Filters.text, main_menu, pass_user_data=True)],
        ENTER_LOCATION: [MessageHandler(Filters.text, enter_location, pass_user_data=True)],
        STATIC_PHOTO: [MessageHandler(Filters.text, static_photo, pass_user_data=True),
                       CallbackQueryHandler(get_photo_handler, pass_user_data=True)],
        NEED_ADRESS: [MessageHandler(Filters.text, need_adress, pass_user_data=True)],
        WEATHER_HANDLER: [MessageHandler(Filters.text, weather, pass_user_data=True)]
    },
    fallbacks=[CommandHandler('stop', stop)]
)


if __name__ == '__main__':
    main()
