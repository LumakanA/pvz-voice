import time
import assemblyai as aai
import pyodbc
import scipy.io.wavfile as wav
import sounddevice as sd


# Функция для приемки заказов на ПВЗ
def receive_order_at_pvz():
    # Подключение к базе данных
    conn = pyodbc.connect(
        'DRIVER={SQL Server};SERVER=NFURY\\SQLEXPRESS;DATABASE=PVZ_CHEMP')

    # Создание курсора
    cursor = conn.cursor()

    # Запрос таблицы Orders для получения ожидающих заказов
    query = "SELECT OrderNumber, ClientPhoneNumber FROM Orders WHERE Status = 'Pending'"
    cursor.execute(query)

    # Получение всех ожидающих заказов
    pending_orders = cursor.fetchall()

    if not pending_orders:
        print("Нет ожидающих заказов.")
        return

    # Вывод ожидающих заказов
    print("Ожидающие заказы:")
    for order in pending_orders:
        print(f"Номер заказа: {order.OrderNumber}, Телефон клиента: {order.ClientPhoneNumber}")

    # Получение от пользователя номера заказа для приемки
    order_number_to_receive = input("Пожалуйста, введите номер заказа для приемки: ")

    # Обновление статуса полученного заказа в базе данных
    update_query = f"UPDATE Orders SET Status = 'Received' WHERE OrderNumber = '{order_number_to_receive}'"
    cursor.execute(update_query)
    conn.commit()

    print(f"Заказ {order_number_to_receive} успешно принят.")

    # Закрытие курсора и соединения с базой данных
    cursor.close()
    conn.close()


# Функция для поиска заказа по номеру телефона клиента
def find_order_by_phone(phone_number):
    # Подключение к базе данных
    conn = pyodbc.connect(
        'DRIVER={SQL Server};SERVER=NFURY\\SQLEXPRESS;DATABASE=PVZ_CHEMP')

    # Создание курсора
    cursor = conn.cursor()

    # Запрос таблицы Orders
    query = f"SELECT RackID, CellID FROM Orders WHERE ClientPhoneNumber = '{phone_number}'"
    cursor.execute(query)

    # Получение результата
    row = cursor.fetchone()

    if row:
        rack_id, cell_id = row
        return f"Номер складской ячейки: {rack_id}-{cell_id}"
    else:
        return "Заказ не найден"

    # Закрытие курсора и соединения с базой данных
    cursor.close()
    conn.close()


# Функция для транскрибации аудио с помощью AssemblyAI
def transcribe_audio(audio_file):
    aai.settings.api_key = "d2010a481d314166949f17afb6cd9710"
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)
    return transcript.text


# Функция для выдачи заказа
def issue_order():
    # Реализация процедуры выдачи заказа с голосовым управлением
    # Может включать подтверждение деталей заказа с пользователем
    # и пометку заказа как выданного в системе
    # Замените этот код своей реализацией
    print("Заказ успешно выдан.")


# Функция для обработки других функций с голосовым управлением
def other_functions():
    # Реализация других функций по необходимости
    # Замените этот код своей реализацией
    print("Другие функции успешно обработаны.")


# Основная функция для записи аудио, транскрибации и выполнения команд
def main():
    duration = 3  # Длительность записи в секундах
    fs = 44100  # Частота дискретизации
    print("Произнесите вашу команду...")
    myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    for i in range(duration, 0, -1):
        print(f"Запись завершится через {i} секунд(ы)...")
        time.sleep(1)
    sd.wait()  # Ожидание завершения записи
    wav.write('command.wav', fs, myrecording)  # Сохранение записи в файл
    command_text = transcribe_audio('command.wav')  # Транскрибация аудио
    print("Команда:", command_text)

    # Проверка команды и выполнение соответствующей функции
    if "Find order." in command_text:
        phone_number = input("Пожалуйста, укажите номер телефона клиента: ")
        result = find_order_by_phone(phone_number)
        print(result)
    elif "Issue order." in command_text:
        issue_order()
    elif "Receive order." in command_text:
        receive_order_at_pvz()
    else:
        other_functions()


if __name__ == "__main__":
    main()
