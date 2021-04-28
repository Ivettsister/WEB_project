import os
import logging
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from maps_api.geocoder import get_ll_span, get_city, get_country_code, get_coordinates
from weather import get_current_weather, get_forecast_weather
from Keyboard import keyboard1, keyboard2, keyboard4, keyboard5, keyboard6, keyboard7, \
    inline_maps, reply_keyboard, keyboard_back, keyboard_number_of_companies, keyboard_get_result
from organizations import ask_for_orgs
from timetable import nearest_stations_request, get_transport
from planing_route import route_request
from error_messanger import send_message

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
PORT = int(os.environ.get('PORT', 5000))
TOKEN = os.getenv("TELEGRAMM_TOKEN")
HEROKU_APP_NAME = "web-project-yl"

info_about_bot = '❗ Этот бот, создан для помощи в ориентировании на местности.\nОн может' + \
                 ' предоставить карту по адресу запрошенного места, найти ближайшие организации' + \
                 ' по вашему запросу, показать прогноз погоды, а также найти ближайшую к Вам станцию' + \
                 ' и предоставить её расписания. Также в разработке находится функция построения маршрута!\n' \
                 'Поддерживаемые комманды:\n/start\n/help\n/stop'


def location(update, context):
    return update.message.location


def start(update, context):
    update.message.reply_text(
        '👋 Вас приветсвует бот, созданный для помощи в ориентировании на местности.\n' +
        'Я могу предоставить карту по адресу запрошенного места, посчитать время на дорогу до этого' +
        ' места (если вы предоставите свою геолокацию) и предоставить прогноз погоды.\n'
        'Введите свое имя:',
        reply_markup=ReplyKeyboardMarkup(keyboard1,
                                         one_time_keyboard=True,
                                         resize_keyboard=True))
    return ENTER_NAME


def enter_name(update, context):
    message = update.message
    name = message.text
    context.user_data['chat_id'] = message.chat.id
    if name != '↪️ Пропустить':
        context.user_data['username'] = name
    else:
        context.user_data['username'] = None

    update.message.reply_text('Где вы сейчас находитесь?', reply_markup=reply_keyboard)
    return ENTER_LOCATION


def enter_location(update, context):
    answer = update.message.text
    if answer != '↪️ Пропустить':
        context.user_data['location'] = answer
    else:
        context.user_data['location'] = None
    name = ', {}'.format(context.user_data['username']) if context.user_data[
                                                               'username'] is not None else ''
    update.message.reply_text('Добро пожаловать{}!'.format(name),
                              reply_markup=ReplyKeyboardMarkup(keyboard2))
    return MAIN_MENU


def main_menu(update, context):
    text = update.message.text
    if text == '🗺   Показать на карте':
        update.message.reply_text(
            '✅ Выберите или введите, что мне показывать (при выборе своего местоположения' +
            ' обратите внимание, что используется, тот адрес который вы указывали ранее,' +
            ' в случае необходимости обновите свое местоположение в главном меню)',
            reply_markup=ReplyKeyboardMarkup(keyboard7, resize_keyboard=True))
        return STATIC_PHOTO

    elif text == '🔎 Найти ближайшую организацию':
        update.message.reply_text(
            '✅ Выберите центр поиска (обязательно):',
            reply_markup=ReplyKeyboardMarkup(keyboard6, resize_keyboard=True))
        return GET_LL_ORGANIZATION

    elif text == '🌧  Погода':
        if context.user_data['location'] is None:
            update.message.reply_text('Сначала укажите свое местоположение ❗')
        else:
            update.message.reply_text(
                '✅ Выберите параметры, которые Вы хотите настроить',
                reply_markup=ReplyKeyboardMarkup(keyboard4, resize_keyboard=True)
            )
            return WEATHER_HANDLER

    elif text == '🧮 Построить маршрут':
        update.message.reply_text(
            'Для начала я должен понять, от какой точки мне строить ваш маршрут...' +
            '✅ Выберите или введите адрес старта, при выборе кнопки "🌍  Мое расположение"' +
            ' обратите внимание, что используется, тот адрес который вы указывали ранее,' +
            ' в случае необходимости обновите свое местоположение в главном меню):',
            reply_markup=ReplyKeyboardMarkup(keyboard6, resize_keyboard=True, one_time_keyboard=True)
        )
        return GET_ROUTE

    elif text == '🛩  Расписания':
        update.message.reply_text(
            'Для начала я должен найти ближайшие к вам станции...' +
            '✅ Выберите центр поиска (обязательно):',
            reply_markup=ReplyKeyboardMarkup(keyboard6, resize_keyboard=True)
        )
        return TIMETABLE_HANDLER

    elif text == '🔙 Указать своё местоположение':
        update.message.reply_text('Где вы сейчас находитесь (Введите точный адрес - (город, улица, дом))?',
                                  reply_markup=reply_keyboard)
        return ENTER_LOCATION
    return MAIN_MENU


def get_ll_organization(update, context):
    text = update.message.text
    if text == '🌍  Мое расположение':
        if context.user_data['location'] is not None:
            text = context.user_data['location']
        else:
            update.message.reply_text('Вы не предоставляли собственного местоположения ❗')
            text = '🔙  Вернуться назад'
    if text == '🔙  Вернуться назад':
        update.message.reply_text('Возвращаю вас в главное меню...',
                                  reply_markup=ReplyKeyboardMarkup(keyboard2))
        return MAIN_MENU
    else:
        context.user_data['ll_organization'] = get_coordinates(text)
        update.message.reply_text('❗ Введите информацию об организации: телефон, название, '
                                  'тип организации(например кинотеатр, музей и т.д.) адрес и др.\n'
                                  'Обратите внимание, что если вы хотите изменить центральную точку'
                                  ' поиска, то это можно сделать нажав кнопку "🔙  Вернуться назад"',
                                  reply_markup=ReplyKeyboardMarkup(keyboard_back, resize_keyboard=True))
        return GET_INFO_ABOUT_COMPANY


def get_info_about_company(update, context):
    text = update.message.text
    if text == '🔙  Вернуться назад':
        update.message.reply_text('Возвращаю вас к выбору центральной точки поиска организации',
                                  reply_markup=ReplyKeyboardMarkup(keyboard6, resize_keyboard=True))
        return GET_LL_ORGANIZATION
    else:
        context.user_data['text_organization'] = text
        update.message.reply_text('✅ Выберите до скольки найденных организаций отобразить'
                                  '(выберите число от 1 до 50).'
                                  'По умолчанию число: 10',
                                  reply_markup=ReplyKeyboardMarkup(keyboard_number_of_companies, resize_keyboard=True))
        return GET_NUMBER_OF_COMPANIES


def get_number_of_companies(update, context):
    text = update.message.text
    if text == '↪️ Пропустить':
        context.user_data['number'] = 10
        update.message.reply_text('Выбрано число 10', reply_markup=ReplyKeyboardMarkup(keyboard_get_result))
        return GET_ORGANIZATIONS
    elif text == '🔙  Вернуться назад':
        update.message.reply_text('Возвращаю вас к вводу информации об организации' +
                                  ' (ВНИМАНИЕ: бот запоминает только последний ввод информации об организации!)',
                                  reply_markup=ReplyKeyboardMarkup(keyboard_back, resize_keyboard=True))
        return GET_INFO_ABOUT_COMPANY
    else:
        try:
            if 1 <= int(text) <= 50:
                context.user_data['number'] = int(text)
                update.message.reply_text(f'Выбрано число {int(text)}',
                                          reply_markup=ReplyKeyboardMarkup(keyboard_get_result))
                return GET_ORGANIZATIONS
            else:
                update.message.reply_text('Введено некорректное число, введите число из диапазона от 1 до 50 ❗')
        except:
            update.message.reply_text('Некорректный ввод, попробуйте еще раз ❗')


def get_organizations(update, context):
    context.user_data['ll_organization'] = str(context.user_data['ll_organization'][0]) + ', ' + \
                                           str(context.user_data['ll_organization'][1])
    answer = ask_for_orgs(context.user_data['ll_organization'], context.user_data['text_organization'],
                          context.user_data['number'])
    if answer is None:
        send_message(context.user_data['chat_id'], 'Во время исполнения программы произошла ошибка.\n'
                                                   'Для продолжения корректной работы программы перезапустите бота, '
                                                   'используя комманды /stop /start')
        return MAIN_MENU
    if answer['size'] == 0:
        update.message.reply_text('Ничего не найдено ❗')
    else:
        for info in answer['orgs']:
            update.message.reply_text(info)
    update.message.reply_text('Возвращаю вас в главное меню',
                              reply_markup=ReplyKeyboardMarkup(keyboard2, resize_keyboard=True))
    return MAIN_MENU


def static_photo(update, context):
    text = update.message.text
    if text == '🌍  Мое расположение':
        if context.user_data['location'] is not None:
            text = context.user_data['location']
        else:
            update.message.reply_text('Вы не предоставляли собственного местоположения ❗')
            text = '🔙  Вернуться назад'
    if text == '🔙  Вернуться назад':
        update.message.reply_text('Возвращаю вас в главное меню...',
                                  reply_markup=ReplyKeyboardMarkup(keyboard2))
        return MAIN_MENU
    else:
        context.user_data['need_adresses'] = text
        update.message.reply_text('✅ Выберите тип карты снимка:', reply_markup=inline_maps)


def get_photo_handler(update, context):
    query = update.callback_query
    context.user_data['need_maptype'] = query.data
    ll, spn = get_ll_span(context.user_data['need_adresses'])
    if ll is None or spn is None:
        send_message(context.user_data['chat_id'], 'Во время исполнения программы произошла ошибка.\n'
                                                   'Для продолжения корректной работы программы перезапустите бота, '
                                                   'используя комманды /stop /start')
        return MAIN_MENU
    static_api_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l={context.user_data['need_maptype']}"
    try:
        context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text="[​​​​​​​​​​​]{}".format(static_api_request, '💡 Нашёл:'),
            parse_mode='markdown',
            reply_markup=inline_maps)
    except:
        send_message(context.user_data['chat_id'], 'Во время исполнения программы произошла ошибка.\n'
                                                   'Для продолжения корректной работы программы перезапустите бота, '
                                                   'используя комманды /stop /start')
        return MAIN_MENU


def need_adress(update, context):
    return static_photo(update, context)


def get_route_from(update, context):
    text = update.message.text
    if text == '🌍  Мое расположение':
        if context.user_data['location'] is not None:
            text = context.user_data['location']
        else:
            update.message.reply_text('Вы не предоставляли собственного местоположения ❗')
            text = '🔙  Вернуться назад'
    if text == '🔙  Вернуться назад':
        update.message.reply_text('Возвращаю вас в главное меню...',
                                  reply_markup=ReplyKeyboardMarkup(keyboard2))
        return MAIN_MENU
    else:
        if 'from_adresses' in context.user_data.keys():
            context.user_data['from_adresses'].append(text)
        else:
            context.user_data['from_adresses'] = [text]
        update.message.reply_text(
            '✅ Пришлите мне точку финиша планируемого Вами маршрута!',
            reply_markup=ReplyKeyboardMarkup(keyboard_back))
        return GET_ROUTE_TO


def get_route_to(update, context):
    text = update.message.text
    if text == '🔙  Вернуться назад':
        update.message.reply_text(
            'Возвращаю вас к выбору точки старта маршрута...',
            reply_markup=ReplyKeyboardMarkup(keyboard6))
        return GET_ROUTE
    if 'to_adresses' in context.user_data.keys():
        context.user_data['to_adresses'].append(text)
    else:
        context.user_data['to_adresses'] = [text]
    update.message.reply_text('✅ Выберите, как Вы планируете добираться до места назначения:',
                              reply_markup=ReplyKeyboardMarkup(keyboard5))
    return GET_ROUTE_HOW


def get_route_how(update, context):
    text = update.message.text
    if text == '🧍 Пешком':
        context.user_data['way_how'] = 'walking'
    elif text == '🚎 На общественном транспорте':
        context.user_data['way_how'] = 'transit'
    elif text == '🚘 На машине':
        context.user_data['way_how'] = 'driving'
    else:
        update.message.reply_text('✅ Возвращаю вас к выбору места назначения:',
                                  reply_markup=ReplyKeyboardMarkup(keyboard_back))
        return GET_ROUTE_TO
    update.message.reply_text('✅ Ваши данные записаны, выберите тип карты маршрута:',
                              reply_markup=inline_maps)


def get_route_handler(update, context):
    query = update.callback_query
    context.user_data['need_maptype'] = query.data
    point_from = ",".join([str(i) for i in get_coordinates(context.user_data["from_adresses"][-1])])
    point_to = ",".join([str(i) for i in get_coordinates(context.user_data["to_adresses"][-1])])
    point_from = point_from.split(',')
    point_from = f"{point_from[1]},{point_from[0]}"
    point_to = point_to.split(',')
    point_to = f"{point_to[1]},{point_to[0]}"
    waypoints = route_request(point_from, point_to, context.user_data['way_how'])
    if waypoints is None:
        send_message(context.user_data['chat_id'], 'Во время исполнения программы произошла ошибка.\n'
                                                   'Для продолжения корректной работы программы перезапустите бота, '
                                                   'используя комманды /stop /start')
        return MAIN_MENU
    static_api_request = f"http://static-maps.yandex.ru/1.x/?l={context.user_data['need_maptype']}&pl={waypoints}"
    try:
        context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text="[​​​​​​​​​​​]{}".format(static_api_request, '💡 Нашёл:'),
            parse_mode='markdown',
            reply_markup=inline_maps)
    except:
        send_message(context.user_data['chat_id'], 'Во время исполнения программы произошла ошибка.\n'
                                                   'Для продолжения корректной работы программы перезапустите бота, '
                                                   'используя комманды /stop /start')
        return MAIN_MENU


def weather(update, context):
    text = update.message.text
    if text == '🌤  Текущая погода':
        city, code = get_city(context.user_data['location']), get_country_code(context.user_data['location'])
        if city is None or code is None:
            update.message.reply_text('Во время выполнения программы произошла ошибка')
            update.message.reply_text('Возвращаю вас в главное меню...)',
                                      reply_markup=ReplyKeyboardMarkup(keyboard2))
            return MAIN_MENU
        update.message.reply_text(
            get_current_weather(city, code, os.getenv("WEATHER_TOKEN"),
                                get_city(context.user_data['location'], 'ru-RU')))
    elif text == '☔️Прогноз на 6 дней':
        city, code = get_city(context.user_data['location']), get_country_code(context.user_data['location'])
        if city is None or code is None:
            update.message.reply_text('Во время выполнения программы произошла ошибка')
            update.message.reply_text('Возвращаю вас в главное меню...)',
                                      reply_markup=ReplyKeyboardMarkup(keyboard2))
            return MAIN_MENU
        update.message.reply_text(
            get_forecast_weather(city, code, os.getenv("WEATHER_TOKEN"),
                                 get_city(context.user_data['location'], 'ru-RU')))
    elif text == '🔙  Вернуться назад':
        update.message.reply_text('Возвращаю вас в главное меню...)',
                                  reply_markup=ReplyKeyboardMarkup(keyboard2))
        return MAIN_MENU


def timetable(update, context):
    text = update.message.text
    if text == '🌍  Мое расположение':
        if context.user_data['location'] is not None:
            text = context.user_data['location']
        else:
            update.message.reply_text('Вы не предоставляли собственного местоположения ❗')
            text = '🔙  Вернуться назад'
    if text == '🔙  Вернуться назад':
        update.message.reply_text('Возвращаю вас в главное меню...',
                                  reply_markup=ReplyKeyboardMarkup(keyboard2))
        return MAIN_MENU
    else:
        strok = ", ".join([str(i) for i in get_coordinates(text)])
        context.user_data['ll_station'] = strok.split(', ')
        find_stations = nearest_stations_request(float(context.user_data['ll_station'][1]),
                                                 float(context.user_data['ll_station'][0]))
        context.user_data['find_stations'] = find_stations
        context.user_data["keyboard_all_stations"] = [['🔙  Вернуться назад']]
        if len(context.user_data['find_stations']) == 0:
            update.message.reply_text(
                'Я не нашёл ни одной станции (остановки) в радиусе 2 км от вас ❗',
                reply_markup=ReplyKeyboardMarkup(context.user_data["keyboard_all_stations"]))
            return GET_INFO_STATION
        else:
            for key in find_stations.keys():
                context.user_data["keyboard_all_stations"].append([key])
            update.message.reply_text(
                '💡 Я нашёл следующие станции в радиусе 2 км....(выберите наиболее интересующую вас кнопку)',
                reply_markup=ReplyKeyboardMarkup(context.user_data["keyboard_all_stations"]))
            return GET_INFO_STATION


def get_info_station(update, context):
    need_station = update.message.text
    if need_station == '🔙  Вернуться назад':
        update.message.reply_text('Возвращаю Вас к выбору местоположения... ' +
                                  '✅ Выберите или введите, что мне показывать (при выборе своего местоположения' +
                                  ' обратите внимание, что используется, тот адрес который вы указывали ранее,' +
                                  ' в случае необходимости обновите свое местоположение в главном меню)'
                                  ,
                                  reply_markup=ReplyKeyboardMarkup(keyboard6))
        return TIMETABLE_HANDLER
    else:
        find_stations = context.user_data['find_stations']
        spic = get_transport(find_stations[need_station])
        if len(spic) == 0:
            update.message.reply_text('С этой станции (остановки) не найдено никаких рейсов, кроме внутригородских ❗')
        else:
            update.message.reply_text('💡 С данной станции (остановки) зарегистрированны следующие маршруты:')
            for elem in spic:
                update.message.reply_text(f"📌 {str(elem)}")
        return GET_INFO_STATION


def stop(update, context):
    update.message.reply_text('👋 Пока!', reply_markup=ReplyKeyboardRemove())
    update.message.reply_text('Для того, чтобы начать работу с ботом заново напишите /start')
    return ConversationHandler.END


def help(update, context):
    update.message.reply_text(info_about_bot)


def main():
    updater = Updater(os.getenv("TELEGRAMM_TOKEN"), use_context=True)
    dp = updater.dispatcher
    dp.add_handler(Stop)
    dp.add_handler(Help)
    dp.add_handler(conversation_handler)
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN, webhook_url=f"https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}")
    updater.idle()


(
    ENTER_NAME, MAIN_MENU, ENTER_LOCATION, STATIC_PHOTO, NEED_ADRESS, GET_LL_ORGANIZATION,
    GET_INFO_ABOUT_COMPANY, GET_NUMBER_OF_COMPANIES, GET_ORGANIZATIONS, WEATHER_HANDLER,
    TIMETABLE_HANDLER, GET_INFO_STATION, GET_ROUTE, GET_ROUTE_TO, GET_ROUTE_HOW
) = range(15)

Help = CommandHandler('help', help)
Stop = CommandHandler('stop', stop)
Start = CommandHandler('start', start)
conversation_handler = ConversationHandler(
    entry_points=[Start],

    states={
        ENTER_NAME: [MessageHandler(Filters.text, enter_name, pass_user_data=True)],
        MAIN_MENU: [MessageHandler(Filters.text, main_menu, pass_user_data=True)],
        ENTER_LOCATION: [MessageHandler(Filters.text, enter_location, pass_user_data=True)],
        STATIC_PHOTO: [MessageHandler(Filters.text, static_photo, pass_user_data=True),
                       CallbackQueryHandler(get_photo_handler, pass_user_data=True)],
        NEED_ADRESS: [MessageHandler(Filters.text, need_adress, pass_user_data=True)],
        GET_LL_ORGANIZATION: [MessageHandler(Filters.text, get_ll_organization, pass_user_data=True)],
        GET_INFO_ABOUT_COMPANY: [MessageHandler(Filters.text, get_info_about_company, pass_user_data=True)],
        GET_NUMBER_OF_COMPANIES: [MessageHandler(Filters.text, get_number_of_companies, pass_user_data=True)],
        GET_ORGANIZATIONS: [MessageHandler(Filters.text, get_organizations, pass_user_data=True)],
        WEATHER_HANDLER: [MessageHandler(Filters.text, weather, pass_user_data=True)],
        TIMETABLE_HANDLER: [MessageHandler(Filters.text, timetable, pass_user_data=True)],
        GET_INFO_STATION: [MessageHandler(Filters.text, get_info_station, pass_user_data=True)],
        GET_ROUTE: [MessageHandler(Filters.text, get_route_from, pass_user_data=True)],
        GET_ROUTE_TO: [MessageHandler(Filters.text, get_route_to, pass_user_data=True)],
        GET_ROUTE_HOW: [MessageHandler(Filters.text, get_route_how, pass_user_data=True),
                        CallbackQueryHandler(get_route_handler, pass_user_data=True)]
    },
    fallbacks=[Stop], allow_reentry=True
)

if __name__ == '__main__':
    main()
