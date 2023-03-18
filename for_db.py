import sqlite3

import xlsxwriter
import pandas as pd


def createBD():  # инициализация класса
    con = sqlite3.connect('database.db', check_same_thread=False)  # подключение БД
    create_table1 = """CREATE TABLE IF NOT EXISTS assortment (
    id    INTEGER    PRIMARY KEY AUTOINCREMENT,
    name        STRING  NOT NULL,
    http        STRING,
    description STRING,
    category    INT     REFERENCES category (id) 
);

"""
    create_table2 = """CREATE TABLE IF NOT EXISTS discounts (
     id  INTEGER   PRIMARY KEY AUTOINCREMENT,
    name   STRING  NOT NULL,
    des_if STRING
);


"""
    create_table3 = """CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text    TEXT,
    time
);
"""
    create_table4 = """CREATE TABLE IF NOT EXISTS question_answer (
    key_words STRING NOT NULL,
    answer           NOT NULL
);
"""
    create_table5 = """CREATE TABLE IF NOT EXISTS users (
     id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name   STRING  NOT NULL,
    status BOOLEAN NOT NULL,
    id_tg  INTEGER NOT NULL
                   UNIQUE,
    username STRING
);
"""
    create_table6 = """CREATE TABLE IF NOT EXISTS category ( id INTEGER PRIMARY KEY AUTOINCREMENT,
    name STRING, 
    http STRING
);
        """
    con.cursor().execute(create_table1)  # создание отсутствующих и необходимых таблиц
    con.cursor().execute(create_table2)
    con.cursor().execute(create_table3)
    con.cursor().execute(create_table4)
    con.cursor().execute(create_table5)
    con.cursor().execute(create_table6)
    con.commit()


def get_answer(key_words):
    con = sqlite3.connect('database.db', check_same_thread=False)
    return con.cursor().execute(f'''SELECT answer FROM question_answer WHERE key_words = "{key_words.capitalize()}"''').fetchall()


def add_que_ans(question, answer):
    con = sqlite3.connect('database.db', check_same_thread=False)
    con.cursor().execute(f'''INSERT INTO question_answer(key_words, answer)
             VALUES ({question}, {answer})''')
    con.commit()


def get_id_category_of_name(name):
    con = sqlite3.connect('database.db', check_same_thread=False)
    return con.cursor().execute(f'''SELECT id FROM category WHERE name="{name}"''').fetchone()[0]


def get_category():
    con = sqlite3.connect('database.db', check_same_thread=False)
    return con.cursor().execute(f'''SELECT * FROM category''').fetchall()


def get_assort_name_category(name):
    con = sqlite3.connect('database.db', check_same_thread=False)
    id_category = get_id_category_of_name(name)
    return con.cursor().execute(f'''SELECT id, name, description, http
             FROM assortment WHERE category = "{id_category}"''').fetchall()


def get_category_assort(id_category):
    con = sqlite3.connect('database.db', check_same_thread=False)
    return con.cursor().execute(f'''SELECT id, name, description, http
          FROM assortment WHERE category = "{id_category}"''').fetchall()


def add_category(name):
    con = sqlite3.connect('database.db', check_same_thread=False)
    con.cursor().execute(f'''INSERT INTO category(name)
                         VALUES('{name}')''')
    con.commit()


def del_category(name):
    con = sqlite3.connect('database.db', check_same_thread=False)
    if not is_category(name):
        return False
    con.cursor().execute(f'''DELETE from category WHERE name = "{name}"''')
    con.commit()
    return True


def is_category(name):
    con = sqlite3.connect('database.db', check_same_thread=False)
    return len(con.cursor().execute(f'''SELECT * FROM category WHERE name="{name}"''').fetchall()) != 0


def is_status(id_tg):
    con = sqlite3.connect('database.db', check_same_thread=False)
    return len(con.cursor().execute(f'''SELECT * FROM users WHERE id_tg="{id_tg}" and status = True''').fetchall()) != 0


def is_assort(name):
    con = sqlite3.connect('database.db', check_same_thread=False)
    return len(con.cursor().execute(f'''SELECT * FROM assortment WHERE name="{name}"''').fetchall()) != 0


def add_assort(name, opisanie, http, category):
    con = sqlite3.connect('database.db', check_same_thread=False)
    con.cursor().execute(f'''INSERT INTO assortment(name, http, description, category)
                                 VALUES('{name}', '{http}', '{opisanie}', {category})''')
    con.commit()


def del_assort(name):
    con = sqlite3.connect('database.db', check_same_thread=False)
    if not is_category(name):
        return False
    con.cursor().execute(f'''DELETE from assortment WHERE name = "{name}"''')
    con.commit()
    return True


def del_que_ans(question):
    con = sqlite3.connect('database.db', check_same_thread=False)
    con.cursor().execute(f'''DELETE from question_answer WHERE key_words = "{question}"''')
    con.commit()


def remove_answer(question, answer):
    con = sqlite3.connect('database.db', check_same_thread=False)
    con.cursor().execute(f'''UPDATE question_answer
            SET answer = '{answer}' WHERE key_words = "{question}"''')
    con.commit()


def add_user(id_tg, name, username):
    con = sqlite3.connect('database.db', check_same_thread=False)
    con.cursor().execute(f'''INSERT INTO users(name, status, id_tg, username)
                                 VALUES('{name}', False, {id_tg}, "{username}")''')
    con.commit()


def remove_status(id_tg):
    con = sqlite3.connect('database.db', check_same_thread=False)
    con.cursor().execute(f'''UPDATE users
                    SET status = True WHERE id_tg = "{id_tg}"''')
    con.commit()


def get_discount():
    con = sqlite3.connect('database.db', check_same_thread=False)
    return con.cursor().execute('''SELECT * FROM discounts''').fetchall()


def add_discount(name, des):
    con = sqlite3.connect('database.db', check_same_thread=False)
    con.cursor().execute(f'''INSERT INTO discounts(name, des_if)
                                         VALUES('{name}', "{des}")''')
    con.commit()


def remove_discount(name, des):
    con = sqlite3.connect('database.db', check_same_thread=False)
    con.cursor().execute(f'''UPDATE discounts
                            SET des_if="{des}" WHERE name = "{name}"''')
    con.commit()


def del_discount(name):
    con = sqlite3.connect('database.db', check_same_thread=False)
    con.cursor().execute(f'''DELETE from discounts WHERE name = "{name}"''')
    con.commit()


def get_notification():
    con = sqlite3.connect('database.db', check_same_thread=False)
    return con.cursor().execute('''SELECT * FROM notifications''').fetchall()


def add_notification(text, time):
    con = sqlite3.connect('database.db', check_same_thread=False)
    con.cursor().execute(f'''INSERT INTO notifications(text, time)
                                         VALUES("{text}", "{time}")''')
    con.commit()


def remove_notification(text, time):
    con = sqlite3.connect('database.db', check_same_thread=False)
    con.cursor().execute(f'''UPDATE notifications
                            SET  time ="{time}" WHERE text="{text}"''')
    con.commit()


def del_notification(text):
    con = sqlite3.connect('database.db', check_same_thread=False)
    con.cursor().execute(f'''DELETE from notifications WHERE  text = "{text}"''')
    con.commit()


def get_info_for_base():
    con = sqlite3.connect('database.db', check_same_thread=False)
    itog = []
    users = 'Пользователи', [
        ('ID', 'ФИО', 'Должность(1-админ, 0-клиент', 'ID TG', 'UserName')] + con.cursor().execute(f'''SELECT id, name, 
            status, id_tg, username FROM Users''').fetchall()
    itog.append(users)
    ssort = 'Асортимент', [
        ('ID', 'Название', 'Ссылка', 'Описание', 'Категория')] + \
               con.cursor().execute(f'''SELECT * FROM assortment''').fetchall()
    itog.append(ssort)
    categories = 'Категории', [
        ('ID Категории', 'Название категории')] + \
                 con.cursor().execute(f'''SELECT id, name FROM category''').fetchall()
    itog.append(categories)
    mailings = 'Уведомления', [
        ('Сообщение', 'Дата отправления')] + \
               con.cursor().execute(f'''SELECT text, time FROM notifications''').fetchall()
    itog.append(mailings)
    questions = 'Вопросы', [
        ('Вопрос', 'Ответ')] + \
                con.cursor().execute(f'''SELECT key_words, answer FROM question_answer''').fetchall()
    itog.append(questions)

    questions = 'Скидки', [
        ('Название', 'Описание')] + \
                con.cursor().execute(f'''SELECT name, des_if FROM discounts''').fetchall()
    itog.append(questions)
    workbook = xlsxwriter.Workbook('Таблица_Excel_БД.xlsx')
    for sheet in itog:
        name, stroki = sheet
        worksheet = workbook.add_worksheet(name)
        for row, stroka in enumerate(stroki):
            for i in range(len(stroka)):
                worksheet.write(row, i, stroka[i])
    workbook.close()
    return


def dow_remove_for_tg(format):
    if format == 1:
        del_all()
        print('delete')
    df = pd.read_excel(io='dow.xlsx', sheet_name=0)
    book = df.head(10000).values
    for lis in book:
        add_user(int(lis[3]), lis[1], lis[4])
        if lis[2]:
            remove_status(int(lis[3]))
    df = pd.read_excel(io='dow.xlsx', sheet_name=2)
    book = df.head(10000).values
    print(book)
    for lis in book:
        add_category(lis[1])
    df = pd.read_excel(io='dow.xlsx', sheet_name=1)
    book = df.head(10000).values
    print(book)
    for lis in book:
        add_assort(lis[1], lis[2], lis[3], int(lis[4]))

    df = pd.read_excel(io='dow.xlsx', sheet_name=3)
    book = df.head(10000).values
    for lis in book:
        add_notification(lis[0], lis[1])
    df = pd.read_excel(io='dow.xlsx', sheet_name=4)
    book = df.head(10000).values
    for lis in book:
        add_que_ans(lis[0], lis[1])
    df = pd.read_excel(io='dow.xlsx', sheet_name=5)
    book = df.head(10000).values
    for lis in book:
        add_discount(lis[0], lis[1])
    print(book)


def del_all():
    con = sqlite3.connect('database.db', check_same_thread=False)
    con.cursor().execute(f'''DELETE from notifications''')
    con.cursor().execute(f'''DELETE from assortment''')
    con.cursor().execute(f'''DELETE from category''')
    con.cursor().execute(f'''DELETE from discounts''')
    con.cursor().execute(f'''DELETE from notifications''')
    con.cursor().execute(f'''DELETE from question_answer''')
    con.cursor().execute(f'''DELETE from users''')
    con.commit()


def get_no_admin_id():
    con = sqlite3.connect('database.db', check_same_thread=False)
    return con.cursor().execute(f'''SELECT id_tg FROM users WHERE status = False''')



# add_que_ans('12', '34')
# print(con.get_assort())
# print(con.get_category_assort(0))
# add_category('name', 'ooo')
# del_category('Мужское')
# print(con.is_category('12'))
# print(con.is_assort('12'))
# con.del_assort('12')
# con.del_que_ans('12')
# con.remove_answer('12', '78')
# con.add_user('1233')
# con.remove_status('12')
# add_discount('12', '23')
# print(con.get_discount())
# con.remove_discount('12', '56')
# con.del_discount('12')
# add_notification('12', '122')
# add_assort('789', '98', '00', 1)
# print(con.get_notification())
# con.remove_notification('12', '98')
# con.del_notification('12')
# print(get_info_for_base())
# print(is_status(89))
# dow_remove_for_tg(0)
# add_category('Продукция с Aloe Vera', '1')
