import datetime
import logging
import threading

import schedule as schedule
from telegram import ForceReply, Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from for_db import *
from geocod import *
from work_of_api import *

# Enable logging
logging.basicConfig(filename='logging.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
                    )

logger = logging.getLogger(__name__)

TOKEN = "6189612026:AAGu8wUuvcjZrPrk5baN4_WOgSq6ABBAQcU"
MARKUP = None


# Define a few command handlers. These usually take the two arguments update and
# context.

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    add_user(user.id, f"{user.first_name} {user.last_name}", user.username)
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

def build_menu(buttons, n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправит список команд, когда будет выдана команда /help."""

    if is_status(update.message.chat_id):
        reply_keyboard = [['/catalog',
                           '/doc_post'],
                          ['/send_message',
                           '/stop'],
                          ['/help']]
        await update.message.reply_text('Команды: \n/catalog - показывает каталог товаров магазина\n/document\n'
                                        '/doc_post - загрузка файла Базы данных. \n'
                                        '/send_message - отправка уведомлений пользователям\n'
                                        '/stop - остановка сложных процессов\n',
                                        reply_markup=reply_keyboard)
    else:
        reply_keyboard = [['/catalog', '/contacts'], ['/joining_the_club', '/club_of_privileges'],
                          ['/work_schedule', '/geo', '/help']]
        await update.message.reply_text('Команды: \n'
                                        '/contacts - Наши соц сети и сайт 🌐\n'
                                        '/joining_the_club - Клуб Привилегий ⭐\n'
                                        '/club_of_privileges - Преимущества участников  Клуба Привилегий ⭐\n'
                                        '/work_schedule - Режим работы ⏰\n'
                                        '/geo - Адреса наших магазинов 🗺\n'
                                        '/admin - Контакты администратора 📞\n'
                                        '/catalog - Каталог товаров 💄\n'
                                        '/help - Список всех команд\n',
                                        reply_markup=reply_keyboard)


async def document_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправит xls файл, когда будет выдана команда /document."""
    if is_status(update.effective_user.id):
        get_info_for_base()
        await update.message.reply_document(document='Таблица_Excel_БД.xlsx')
    else:
        await update.message.reply_text('У вас нет прав для данной команды.')


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Повторите сообщение пользователя."""
    answer = get_answer(update.message.text)
    print(answer)
    await update.message.reply_text('Пожалуйста, переформулируйте вопрос.' if len(answer) == 0 else answer[0][0])


async def doc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ждет файл xlxs т администратора"""
    await update.message.reply_text('Отпавте файл xlsx с изминениями')
    return 0


async def statys(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Назначает пользователя администратором, когда будет выдана команда /statys [password]."""
    password = update.message.text[8:]
    user = update.effective_user
    if password == '1234':
        remove_status(user.id)
        await update.message.reply_html(rf"{user.mention_html()} назначен администратором!",
                                        reply_markup=ForceReply(selective=True), )
    else:
        await update.message.reply_text('У вас нет прав!!!')


async def check_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Повторите сообщение пользователя."""
    a = update.message.document
    if not a:
        await update.message.reply_text('не то')
        return ConversationHandler.END

    get_file_of_tg(a.file_id, TOKEN)
    if not check_file_of_tg():
        await update.message.reply_text('pppp')
    else:
        await update.message.reply_text('Полностью ')
        return 1
    return ConversationHandler.END


async def remove_bzd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dow_remove_for_tg(update.message.text)
    await update.message.reply_text('несены изменения')
    return ConversationHandler.END


async def catalog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправит список разделов товаров, когда будет выдана команда /catalog."""
    a = '\n'.join(list(map(lambda x: ' ' + str(x[0]) + ' - ' + x[1], get_category())))
    await update.message.reply_text('Католог товаров у нас большой:\n' + a)
    return 0


async def contacts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправит вырианты связи с магазином, когда будет выдана команда /contacts."""
    await update.message.reply_text('У нас есть сайт, на котором можно найти много полезной информации. \n'
                                    'Также присоединяйтесь к нам ВКонтакте.\n'
                                    'Вконтакте: https://vk.com/soblaznarzamas \n'
                                    'Сайт: https://soblaznarz.uds.app/c/join?ref=xvvs0921 \n')


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Связь с админимтратором, когда будет выдана команда /admin."""
    await update.message.reply_text('Администратор ответит на все интересующие вас вопросы. '
                                    'С ним можно связаться по телефону: +79202980333')


async def geo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Магазины на карте, когда будет выдана команда /geo."""
    try:
        maps = maps_global()
        print(maps)
        await update.message.reply_photo(maps)
        await update.message.reply_text('У нас две точки по адресам:'
                                        '\n\t 1. г.Арзамас, просп. Ленина, 121, TЦ «Метро» 3 здание, 1 этаж'
                                        '\n\t 2. г.Арзамас, Парковая ул., 14А, ТЦ «Славянский»,1 этаж, отдел номер 7')
    except RuntimeError as ex:
        await update.message.reply_text('Что то пошло не по плану')


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Магазины на карте, когда будет выдана команда /geo."""
    await update.message.reply_text('stop')
    return ConversationHandler.END


async def asortiment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Магазины на карте, когда будет выдана команда /geo."""
    text = update.message.text.rstrip()
    # number = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    # name = ['Наборы', 'Детская косметика', 'Лаки, пенки для волос, расчёски', ' Уход за волосами в домашних условиях',
    #         'Косметика Мирра Люкс', 'Insight профуход за волосами', 'Крема для лица, тела и рук, очищение',
    #         'Женские духи', 'Парфюм Niche- духи унисекс', 'Elements- парфюм унисекс', 'Продукция с Aloe Vera']
    number = list(map(lambda x: str(x[0]), get_category()))
    name = list(map(lambda x: x[1], get_category()))
    if text in name:
        up_text = get_assort_name_category(text)
        if len(up_text) == 0:
            await update.message.reply_text(f'В этой категории не присутствуют товары.')
        else:
            await update.message.reply_text(f'В этой категории присутствуют товары: \n')
            for i in [[str(i[1]) + ' : ' + str(i[2]), i[3]] for i in up_text]:
                await update.message.reply_photo(i[1])
                await update.message.reply_text(i[0] + '\n')
    elif text in number:
        up_text = get_category_assort(int(text))
        if len(up_text) == 0:
            await update.message.reply_text(f'В этой категории не присутствуют товары.')
        else:
            await update.message.reply_text(f'В этой категории присутствуют товары: \n')
            for i in [[str(i[1]) + ' : ' + str(i[2]), i[3]] for i in up_text]:
                await update.message.reply_photo(i[1])
                await update.message.reply_text(i[0] + '\n')
    else:
        print(text, number)
        await update.message.reply_text(f'Возможно вы ошиблись.\nПопробйте ещё раз.')
    return ConversationHandler.END


async def joining_the_club_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """вступления в Клуб Привилегий, когда будет выдана команда /joining_the_club."""
    await update.message.reply_text('Хочешь получать крутые преимущества? \n'
                                    'Вступай в Клуб Привилегий. Что бы вступить нужно сделать некоторые действия: \n'
                                    ' - Зайти в PlayMarket или AppStore и скачать приложение "UDS APP" \n'
                                    ' - Зарегистрироваться и перейти по ссылке: '
                                    'https://soblaznarz.uds.app/c/join?ref=dwac1210 \n'
                                    ' - Получите первые 100 баллов на бонусный счет! (1 балл = 1 рубль) \n'
                                    'Для того что бы ознокомиться с примуществами команда: /club_of_privileges')


async def club_of_privileges_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Преимущества Клуба Привилегий, когда будет выдана команда /club_of_privileges."""
    await update.message.reply_text('У нас есть Клуба Привилегий, участникам он даёт некоторые примущества:\n'
                                    ' - Получают скидку на первую покупку \n'
                                    ' - Получают персональные уведомления о новинках и акциях \n '
                                    ' - Копят баллы с каждой покупки и забирают товар БЕСПЛАТНО \n'
                                    ' - Рекомендуют нас друзьям и получают баллы с их покупок \n'
                                    'Что бы ознокомится с инструкцией вступления команда: /joining_the_club')


async def work_schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправит график работы магазинов, когда будет выдана команда /catalog."""
    await update.message.reply_text('У нас два магазина: \n'
                                    ' - Магазин по адресу г.Арзамас, Парковая ул., 14А, ТЦ «Славянский». \n'
                                    'Работает по графику: \n\t пн – пт 9.00-19.00 \n\t сб – вс 9.00-18.00 \n'
                                    ' - Магазин по адресу г.Арзамас, просп. Ленина, 121, TЦ «Метро». \n'
                                    'Работает по графику: \n\t пн – вс 9.00-20.00 \n'
                                    'Будем вас в наших магазинах, '
                                    'их место положение можно узнать с помощью команды /geo')


async def send_of_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Связь с админимтратором, когда будет выдана команда /admin."""
    await update.message.reply_text('Введите текст, который вы планнируете отправить пользователям.')
    return 0


async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Связь с админимтратором, когда будет выдана команда /admin."""
    context.user_data['0'] = update.message.text

    await update.message.reply_text('Введите дату в формате год:месяц:день, например, 2023:03:19\n'
                                    'Если вы хотите отправить сообщение сейчас отправьте "сейчас".')
    return 1


def send_message(flag, text=''):
    if flag:
        today = ':'.join(
            [str(datetime.date.today().year), str(datetime.date.today().month), str(datetime.date.today().day)])
        print(today)
        text = [i[1] for i in get_notification() if i[2] == today]
        text = '\n'.join(text)
        print(text)
    for i in get_no_admin_id():
        sendMessage(i, text, TOKEN)


async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Связь с админимтратором, когда будет выдана команда /admin."""
    if update.message.text == 'сейчас':
        send_message(False, text=context.user_data['0'])
    else:
        add_notification(context.user_data['0'], update.message.text)
    await update.message.reply_text('Успешно!')
    return ConversationHandler.END


def threat():  # второй поток для рассылки
    while True:
        schedule.run_pending()


def main() -> None:
    """Запустите бота."""
    # Создайте приложение и передайте ему токен вашего бота.
    application = Application.builder().token(TOKEN).build()
    schedule.every().day.at("16:04").do(send_message, True)  # рассылка уведомлений
    threading.Thread(target=threat).start()
    script_doc = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('doc_p'
                                     'ost', doc)],
        # Состояние внутри диалога.
        states={
            0: [MessageHandler(filters.ALL & ~filters.COMMAND, check_file)],
            1: [MessageHandler(filters.ALL & ~filters.COMMAND, remove_bzd)]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        allow_reentry=False,
        fallbacks=[CommandHandler('stop', stop)]
    )
    script_catalog = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('catalog', catalog_command)],
        # Состояние внутри диалога.
        states={
            0: [MessageHandler(filters.TEXT & ~filters.COMMAND, asortiment)]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        allow_reentry=False,
        fallbacks=[CommandHandler('stop', stop)]
    )
    script_send = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler("send_message", send_of_admin_message)],
        # Состояние внутри диалога.
        states={
            0: [MessageHandler(filters.ALL & ~filters.COMMAND, get_text)],
            1: [MessageHandler(filters.ALL & ~filters.COMMAND, get_time)]
        },
        # Точка прерывания диалога. В данном случае — команда /stop.
        allow_reentry=False,
        fallbacks=[CommandHandler('stop', stop)]
    )
    # по разным командам - отвечайте в Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", statys))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("contacts", contacts_command))
    application.add_handler(CommandHandler("administrator", admin_command))
    application.add_handler(CommandHandler("geo", geo_command))
    application.add_handler(CommandHandler("joining_the_club", joining_the_club_command))
    application.add_handler(CommandHandler("club_of_privileges", club_of_privileges_command))
    application.add_handler(script_doc)
    application.add_handler(script_catalog)
    application.add_handler(script_send)
    application.add_handler(CommandHandler("document", document_command))
    application.add_handler(CommandHandler("work_schedule", work_schedule_command))
    # по некомандному, то есть сообщению - повторить сообщение в Telegram
    createBD()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    # Запускайте бота до тех пор, пока пользователь не нажмет Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
