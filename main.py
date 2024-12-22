import os
import datetime
import math
import time

from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError

def main():
    load_dotenv()
    api_id = int(os.getenv('API_ID', '0'))
    api_hash = os.getenv('API_HASH')
    if not api_id or not api_hash:
        print("Ошибка: не найдены API_ID и(или) API_HASH в файле .env")
        return

    client = TelegramClient('my_session', api_id, api_hash)
    client.start()

    all_dialogs = client.get_dialogs()
    dialogs_list = list(all_dialogs)

    page_size = 20
    total_dialogs = len(dialogs_list)
    total_pages = max(1, math.ceil(total_dialogs / page_size))

    current_page = 1

    while True:
        start_index = (current_page - 1) * page_size
        end_index = start_index + page_size
        page_dialogs = dialogs_list[start_index:end_index]

        print(f"\nСтраница {current_page}/{total_pages}")
        for i, dialog in enumerate(page_dialogs, start=1):
            chat_index = start_index + i
            chat_title = dialog.name if dialog.name else "Без названия"
            print(f"{chat_index}. {chat_title}")

        print("\nДоступные действия:")
        print("  [N] - следующая страница (next)")
        print("  [P] - предыдущая страница (prev)")
        print("  [C] - выбрать чат для очистки")
        print("  [Q] - выйти")

        cmd = input("\nВведите команду: ").strip().lower()
        
        if cmd == 'n':
            if current_page < total_pages:
                current_page += 1
            else:
                print("Это последняя страница!")
        elif cmd == 'p':
            if current_page > 1:
                current_page -= 1
            else:
                print("Это первая страница!")
        elif cmd == 'c':
            try:
                chat_num = int(input("Введите номер чата, из которого нужно удалить сообщения: "))
                if 1 <= chat_num <= total_dialogs:
                    selected_dialog = dialogs_list[chat_num - 1]
                    perform_deletion(client, selected_dialog)
                else:
                    print("Некорректный номер чата!")
            except ValueError:
                print("Нужно ввести число.")
        elif cmd == 'q':
            print("Выход.")
            break
        else:
            print("Неизвестная команда. Попробуйте ещё раз.")

def perform_deletion(client, selected_dialog):
    date_str = input("Введите дату в формате ДД.ММ.ГГГГ (например, 25.12.2023): ")
    try:
        delete_before_date = datetime.datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError:
        print("Ошибка: Неверный формат даты. Возврат в меню.")
        return

    chat_entity = selected_dialog.entity
    print("Начинаем удалять ваши сообщения (с параметром revoke=True), может занять некоторое время...")

    offset_id = 0
    total_deleted = 0

    while True:
        try:
            # Загружаем только ваши сообщения (from_user='me') до delete_before_date
            messages = client.get_messages(
                entity=chat_entity,
                from_user='me',
                offset_id=offset_id,
                offset_date=delete_before_date,
                limit=100
            )
            if not messages:
                break

            message_ids = [m.id for m in messages]
            # Удаляем эти сообщения "для всех" (revoke=True)
            client.delete_messages(chat_entity, message_ids, revoke=True)

            offset_id = messages[-1].id
            total_deleted += len(messages)
            print(f"Удалено сообщений: {total_deleted}", end='\r')

        except FloodWaitError as e:
            print(f"\nПойман FloodWaitError: нужно подождать {e.seconds} секунд.")
            time.sleep(e.seconds)
        except Exception as e:
            print(f"\nПроизошла ошибка: {e}")
            break

    print(f"\nГотово. Всего удалено сообщений: {total_deleted}\n")

if __name__ == "__main__":
    main()
