#!venv/bin/python
import logging
from aiogram import Bot, Dispatcher, executor, types
logging.basicConfig(level=logging.INFO)
from mysql.connector import Error, MySQLConnection
from configparser import ConfigParser

bot = Bot(token='1365474889:AAGmwok4NdQOBiGBHurzx9Juf4ZcS7kzt7o')
dp = Dispatcher(bot)

def read_db_config(filename='config.ini', section='mysql'):
    """ Read database configuration file and return a dictionary object
    :param filename: name of the configuration file
    :param section: section of database configuration
    :return: a dictionary of database parameters
    """
    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)
    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))
    return db

def query_with_fetchall(tgmid):
    try:
        if tgmid == "all":
            dbconfig = read_db_config()
            conn = MySQLConnection(**dbconfig)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM redirection")
            rowss = cursor.fetchall()
            return rowss
        else:
            dbconfig = read_db_config()
            conn = MySQLConnection(**dbconfig)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM redirection WHERE tgm_id = " + str(tgmid))
            rowss = cursor.fetchall()
            return rowss
    except Error as e:
        print(e)

    finally:
        cursor.close()
        conn.close()

def query_phone_with_fetchall(phone):
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM redirection WHERE internal = " + str(phone))
        rowss = cursor.fetchall()
        return rowss
    except Error as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

def query_edit_changerow(rowid, is_enabled):
    # read database configuration
    db_config = read_db_config()

    # prepare query and data
    query = """ UPDATE redirection
                SET is_enabled = %s
                WHERE id = %s """

    data = (is_enabled, rowid)

    try:
        conn = MySQLConnection(**db_config)

        # update redirection title
        cursor = conn.cursor()
        cursor.execute(query, data)
        # accept the changes
        conn.commit()

    except Error as error:
         print(error)

    finally:
         cursor.close()
         conn.close()

def query_edit_changeallrowexept(rowid, phone):
    # read database configuration
    db_config = read_db_config()

    # prepare query and data
    query = """ UPDATE redirection
                SET is_enabled = 0
                WHERE (id != %s) AND (internal = %s) """

    data = (rowid, phone)

    try:
        conn = MySQLConnection(**db_config)

        # update redirection title
        cursor = conn.cursor()
        cursor.execute(query, data)
        # accept the changes
        conn.commit()

    except Error as error:
         print(error)

    finally:
         cursor.close()
         conn.close()


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    poll_keyboard = types.ReplyKeyboardMarkup(resize_keyboard= True, one_time_keyboard = True)
    poll_keyboard.add(types.KeyboardButton(text="Переключить телефон"))
    poll_keyboard.add(types.KeyboardButton(text="Отмена"))
    await message.answer("Вегос-М | переключение с рабочего на мобильный и обратно:", reply_markup=poll_keyboard)
    print (message.chat.id)

@dp.message_handler(lambda message: message.text == "Отмена")
async def action_cancel(message: types.Message):
    remove_keyboard = types.ReplyKeyboardRemove()
    await message.answer("Действие отменено. Введите /start, чтобы начать заново.", reply_markup=remove_keyboard)

@dp.message_handler(lambda message: message.text == "Переключить телефон")
async def action_check(message: types.Message):
          tgmid = message.from_user.id
          rows = query_with_fetchall(tgmid)
          markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
          for row in rows:
                print(row)
                ss1 = str(row[2])
                if row[4] == 0:
                   ss = 'Переключить ' + ss1
                   cb_d = str(row[0]) + str(row[4])
                   ss2 = ss1 + ' переадресация отключена'
                   await bot.send_message(message.chat.id, ss2)
                else:
                   ss = 'Переключить ' + ss1
                   cb_d = str(row[4]) + str(row[0])
                   ss2 = ss1 + ' переадресация включена'
                   await bot.send_message(message.chat.id, ss2)
                markup.add(types.InlineKeyboardButton(ss, callback_data=cb_d))
          markup.add(types.InlineKeyboardButton("Отмена"))
          await message.answer("Нажмите для переключения:", reply_markup=markup)

@dp.message_handler(regexp='Переключить\s\d\d\d')
async def action_change(message: types.Message):
          tgmid = message.from_user.id
          rows = query_with_fetchall(tgmid)
          mestext = message.text
          localnumber = mestext[12:16]

          for row in rows:
                ss1 = str(row[2])
                if (row[4] == 0) and (ss1 == localnumber):
                    query_edit_changeallrowexept(row[0], localnumber)
                    query_edit_changerow(row[0],1)
                    await bot.send_message(message.chat.id, localnumber + " переадресация включена")
                elif (row[4] == 1) and (ss1 == localnumber):
                    query_edit_changerow(row[0], 0)
                    await bot.send_message(message.chat.id, localnumber + " переадресация выключена")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)