import logging
import re
import paramiko
import psycopg2
import os


from psycopg2 import Error
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
RM_HOST = os.getenv("RM_HOST")
RM_PORT = os.getenv("RM_PORT")
RM_USER = os.getenv("RM_USER")
RM_PASSWORD = os.getenv("RM_PASSWORD")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")

# Подключение логирования
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def send_long_message(update: Update, context, message: str):
    splitted_text = []
    for part in range(0, len(message), 4096):
        splitted_text.append(message[part:part + 4096])
    for part in splitted_text:
        update.message.reply_text(part)
def helpCommand(update: Update, context):
    send_long_message(update, context,
                   "/start - начать общение с ботом.\n"
                   "/find_phone_number - поиск номеров в тексте.\n"
                   "/find_email - поиск Email-адресов в тексте.\n"
                   "/verify_password - проверка пароля на сложность.\n"
                   "/get_release - информация о релизе.\n"
                   "/get_uname - информация об архитектуре процессора, имени хоста системы и версии ядра.\n"
                   "/get_uptime - информация о времени работы.\n"
                   "/get_df - информация о состоянии файловой системы.\n"
                   "/get_free - информация о состоянии оперативной памяти.\n"
                   "/get_mpstat - информация о производительности системы.\n"
                   "/get_w - информация о работающих в данной системе пользователях.\n"
                   "/get_auths - последние 10 входов в систему.\n"
                   "/get_critical - последние 5 критических события.\n"
                   "/get_ps - информация о запущенные процессах.\n"
                   "/get_ss - информация об используемых портах.\n"
                   "/get_apt_list - информация об установленных пакет(ах/e).\n"
                   "/get_services - информация о запущенных процессах.\n"
                   "/get_repl_logs - логи о репликации БД.\n"
                   "/get_emails - Email-адреса из БД.\n"
                   "/get_phone_numbers - телефонные номера из БД."
                   )

def ssh_connect(command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=RM_HOST, username=RM_USER, password=RM_PASSWORD, port=RM_PORT)
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    return data
def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска Email: ')
    return 'findEmail'

def findEmail(update: Update, context):
    user_input = update.message.text
    emailRegex = re.compile(r'[\w\.-]+@[\w\.-]+')
    global emailList
    emailList = emailRegex.findall(user_input)
    if not emailList:
        update.message.reply_text('Emails не найдены')
        return
    emails = ''
    for i in range(len(emailList)):
        emails += f'{i + 1}. {emailList[i]}\n'

    update.message.reply_text(emails)
    update.message.reply_text('Загрузить в базу данных? y/n')
    return 'db_email'

def db_email(update: Update, context):
    user_input = update.message.text
    if user_input == 'y':
        try:
            connection = psycopg2.connect(user=DB_USER,
                                          password=DB_PASSWORD,
                                          host=DB_HOST,
                                          port=DB_PORT,
                                          database=DB_DATABASE)

            cursor = connection.cursor()
            cursor.execute("SELECT emailid FROM emails;")
            data = cursor.fetchall()
            a = max(data)
            n = 1
            for i in range(len(emailList)):
                cursor.execute(f"INSERT INTO emails (emailid, email) VALUES ('{a[0] + n}', '{emailList[i]}');")
                connection.commit()
                n += 1
            logging.info("Команда успешно выполнена")
            update.message.reply_text('Загрузка выполнена!')
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
            update.message.reply_text('Что-то пошло не так, попробуйте позже!')
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
            return ConversationHandler.END
    else:
        update.message.reply_text('Загрузка отменена!')
        return ConversationHandler.END

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'findPhoneNumbers'

def findPhoneNumbers(update: Update, context):
    user_input = update.message.text
    phoneNumRegex = re.compile(r'(?:8|\+7)[\s\-]?(?:\(\d{3}\)|\d{3})[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}')
    global phoneNumberList
    phoneNumberList = phoneNumRegex.findall(user_input)
    if not phoneNumberList:
        update.message.reply_text('Телефонные номера не найдены')
        return
    else:
        phoneNumbers = ''
        for i in range(len(phoneNumberList)):
            phoneNumbers += f'{i + 1}. {phoneNumberList[i]}\n'
        update.message.reply_text(phoneNumbers)
        update.message.reply_text('Загрузить в базу данных? y/n')
        return 'db_phone'

def db_phone(update: Update, context):
    user_input = update.message.text
    if user_input == 'y':
        try:
            connection = psycopg2.connect(user=DB_USER,
                                          password=DB_PASSWORD,
                                          host=DB_HOST,
                                          port=DB_PORT,
                                          database=DB_DATABASE)

            cursor = connection.cursor()
            cursor.execute("SELECT phoneid FROM phonenum;")
            data = cursor.fetchall()
            a = max(data)
            n = 1
            for i in range(len(phoneNumberList)):
                cursor.execute(f"INSERT INTO phonenum (phoneid, phonenumbers) VALUES ('{a[0] + n}', '{phoneNumberList[i]}');")
                connection.commit()
                n += 1
            logging.info("Команда успешно выполнена")
            update.message.reply_text('Загрузка выполнена!')
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
            update.message.reply_text('Что-то пошло не так, попробуйте позже!')
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
            return ConversationHandler.END
    else:
        update.message.reply_text('Загрузка отменена!')
        return ConversationHandler.END

def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите текст для проверки пароля: ')
    return 'verifyPassword'

def verifyPassword(update: Update, context):
    user_input = update.message.text
    if re.fullmatch(r'[A-Za-z0-9!@#$%^&*().]{8,}', user_input):
        update.message.reply_text('Пароль сложный')
    else:
        update.message.reply_text('Пароль простой')
    return ConversationHandler.END

def get_release(update: Update, context):
    data = ssh_connect("lsb_release -a")
    update.message.reply_text(data)

def get_uname(update: Update, context):
    data = ssh_connect("uname -a")
    update.message.reply_text(data)

def get_uptime(update: Update, context):
    data = ssh_connect("uptime")
    update.message.reply_text(data)

def get_df(update: Update, context):
    data = ssh_connect("df -h")
    update.message.reply_text(data)

def get_free(update: Update, context):
    data = ssh_connect("free -h")
    update.message.reply_text(data)

def get_mpstat(update: Update, context):
    data = ssh_connect("mpstat")
    update.message.reply_text(data)

def get_w(update: Update, context):
    data = ssh_connect("w")
    update.message.reply_text(data)

def get_auths(update: Update, context):
    data = ssh_connect("last -n 10")
    update.message.reply_text(data)

def get_critical(update: Update, context):
    data = ssh_connect("journalctl -p crit -n 5")
    update.message.reply_text(data)

def get_ps(update: Update, context):
    data = ssh_connect("ps")
    send_long_message(update, context, data)

def get_ss(update: Update, context):
    data = ssh_connect("ss -tulpn")
    update.message.reply_text(data)

def get_apt_listCommand(update: Update, context):
    update.message.reply_text('Введите название службы или all')
    return 'get_apt_list'

def get_apt_list(update: Update, context):
    user_input = update.message.text
    if user_input.lower() == 'all':
        data = ssh_connect("apt list --installed")
        send_long_message(update, context, data)
    else:
        data = ssh_connect(f"apt list --installed | grep {user_input}")
        send_long_message(update, context, data)
    return ConversationHandler.END

def get_services(update: Update, context):
    data = ssh_connect("service --status-all | grep +")
    update.message.reply_text(data)

def get_repl_logs(update: Update, context):
    data = ssh_connect(f"echo {RM_PASSWORD} | sudo -S docker logs db | grep repl")
    update.message.reply_text(data[:3000])

def get_emails(update: Update, context):
    try:
        connection = psycopg2.connect(user=DB_USER,
                                      password=DB_PASSWORD,
                                      host=DB_HOST,
                                      port=DB_PORT,
                                      database=DB_DATABASE)

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM emails;")
        data = cursor.fetchall()
        a = ''
        for i in data:
            for j in i:
                a += str(j) + ' '
            a += '\n'
        update.message.reply_text(a)
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

def get_phone_numbers(update: Update, context):
    try:
        connection = psycopg2.connect(user=DB_USER,
                                      password=DB_PASSWORD,
                                      host=DB_HOST,
                                      port=DB_PORT,
                                      database=DB_DATABASE)

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM phonenum;")
        data = cursor.fetchall()
        a = ''
        for i in data:
            for j in i:
                a += str(j) + ' '
            a += '\n'
        update.message.reply_text(a)
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'db_phone': [MessageHandler(Filters.text & ~Filters.command, db_phone)]
        },
        fallbacks=[]
    )
    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailCommand)],
        states={
            'findEmail': [MessageHandler(Filters.text & ~Filters.command, findEmail)],
            'db_email': [MessageHandler(Filters.text & ~Filters.command, db_email)]
        },
        fallbacks=[]
    )
    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)],
        },
        fallbacks=[]
    )
    convHandlerget_apt_list = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_listCommand)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )


    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(convHandlerget_apt_list)
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    # Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()

