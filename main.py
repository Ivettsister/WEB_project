from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
import os
from maps_api.geocoder import get_ll_span
from weather import get_current_weather, get_forecast_weather


import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


load_dotenv()
keyboard1 = [['Пропустить']]
keyboard2 = [['Показать на карте'], ['Найти ближайшую организацию'], ['Посчитать время на дорогу'], ['Погода'], ['Расписания'],
             ['Вернуться назад']]
keyboard3 = [['Вернуться назад']]
keyboard4 = [['Текущая погода'], ['Прогноз на n дней'], ['Вернуться назад']]
keyboard5 = [['Пешком'], ['На общественном транспорте'], ['На машине']]
keyboard6 = [['Ввести адрес центральной точки поиска']]
keyboard7 = [['Ввести адрес']]

inline_maps = InlineKeyboardMarkup([
    [InlineKeyboardButton('Карта', callback_data='map')],
    [InlineKeyboardButton('Спутник', callback_data='sat')],
    [InlineKeyboardButton('Гибрид', callback_data='sat,skl')],
])


def start(update, context):
    update.message.reply_text(
        'Как Вас зовут?', reply_markup=ReplyKeyboardMarkup(keyboard1, one_time_keyboard=False))
    return ENTER_NAME


def enter_name(update, context):
    name = update.message.text
    if name != 'Пропустить':
        context.user_data['username'] = name
    else:
        context.user_data['username'] = None
    update.message.reply_text('Где вы сейчас находитесь?')
    return ENTER_LOCATION


def enter_location(update, context):
    location = update.message.text

    if location != 'Пропустить':
        context.user_data['location'] = location
        keyboard6.append([location])
        keyboard7.append([location])
    else:
        context.user_data['location'] = None
    name = ', {}'.format(context.user_data['username']) if context.user_data['username'] is not None else ''
    update.message.reply_text('Добро пожаловать{}!'.format(name), reply_markup=ReplyKeyboardMarkup(keyboard2))
    return MAIN_MENU


def main_menu(update, context):
    text = update.message.text

    if text == 'Показать на карте':
        update.message.reply_text(
            'Выберите, что мне показывать:',
            reply_markup=ReplyKeyboardMarkup(keyboard7)
        )
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
        pass

    elif text == 'Посчитать время на дорогу':
        update.message.reply_text(
            'Выберите параметры, которые Вы хотите настроить',
            reply_markup=ReplyKeyboardMarkup(keyboard5)
        )
        pass
    return MAIN_MENU


def static_photo(update, context):
    text = update.message.text
    if text == 'Ввести адрес':
        return NEED_ADRESS
    else:
        if 'need_adresses' in context.user_data.keys():
            context.user_data['need_adresses'].append(text)
        else:
            context.user_data['need_adresses'] = [text]
    update.message.reply_text(
        'Выберите тип карты снимка:',
        parse_mode='markdown',
        reply_markup=inline_maps
    )
    return GET_PHOTO_HANDLER


def get_photo_handler(update, context):
    query = update.callback_query
    print(query.data)
    print('here1')
    context.user_data['need_maptype'] = query.data
    ll, spn = get_ll_span(context.user_data['need_adresses'][-1])
    static_api_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l=map"
    context.bot.send_photo(
        update.message.chat_id,
        static_api_request,
        caption="Нашёл:"
    )
    return STATIC_PHOTO


def need_adress(update, context):
    return STATIC_PHOTO


def choose_map_type(bot, update, user_data):
    query = update.callback_query
    bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,
                          text="[​​​​​​​​​​​]({}){}".format(get_static_map(user_data, query.data),
                                                            'Карта для города ' + get_city(
                                                                user_data['current_response'], 'ru-RU')),
                          parse_mode='markdown', reply_markup=inline_maps)


def weather(bot, update, user_data):
    text = update.message.text

    if text == 'Текущая погода':
        city, code = get_city(user_data['current_response']), get_country_code(user_data['current_response'])
        update.message.reply_text(
            get_current_weather(city, code, WEATHER_TOKEN, get_city(user_data['current_response'], 'ru-RU')))

    elif text == 'Прогноз на n дней':
        city, code = get_city(user_data['current_response']), get_country_code(user_data['current_response'])
        update.message.reply_text(
            get_forecast_weather(city, code, WEATHER_TOKEN, get_city(user_data['current_response'], 'ru-RU')))

    elif text == 'Вернуться назад':
        update.message.reply_text('Выберите одну из возможных функций для данного местоположения:',
                                  reply_markup=ReplyKeyboardMarkup(keyboard2))

        pass


def stop(bot, update):
    update.message.reply_text('Пока!', reply_markup=ReplyKeyboardRemove())
    update.message.reply_text('Для того, чтобы начать работу с ботом заново напишите /start')
    return ConversationHandler.END


def main():
    updater = Updater(os.getenv("TOKEN"), use_context=True)
    dp = updater.dispatcher
    dp.add_handler(conversation_handler)
    updater.start_polling()
    updater.idle()


(
    ENTER_NAME, ENTER_LOCATION, MAIN_MENU, STATIC_PHOTO, NEED_ADRESS, GET_PHOTO_HANDLER
) = range(6)


conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],

    states={
        ENTER_NAME: [MessageHandler(Filters.text, enter_name, pass_user_data=True)],
        MAIN_MENU: [MessageHandler(Filters.text, main_menu, pass_user_data=True)],
        ENTER_LOCATION: [MessageHandler(Filters.text, enter_location, pass_user_data=True)],
        STATIC_PHOTO: [MessageHandler(Filters.text, static_photo, pass_user_data=True)],
        GET_PHOTO_HANDLER: [MessageHandler(Filters.text, get_photo_handler, pass_user_data=True),
            CallbackQueryHandler(choose_map_type, pass_user_data=True)],
        NEED_ADRESS: [MessageHandler(Filters.text, need_adress, pass_user_data=True)]
    },

    fallbacks=[CommandHandler('stop', stop)]
)


if __name__ == '__main__':
    main()
