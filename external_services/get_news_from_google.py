import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime


def get_today_news_from_sheet(sheet_name):
    # Настройка доступа к Google Sheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file('../anna-nihongo-bot-96c6f518f0cd.json', scopes=scope)
    client = gspread.authorize(creds)

    # Открытие таблицы
    sheet = client.open(sheet_name).sheet1

    # Получение всех данных из таблицы
    data = sheet.get_all_values()

    # Получение сегодняшней даты в формате "YYYY-MM-DD"
    # today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today = datetime.now().date()

    # Поиск новости за сегодня с 'Y' в колонке I
    for row in data[0:]:
        news_date = datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S").date()
        print(news_date)
        print(row[8])
        print(today)
        print(news_date == today)
        print(row[8].upper() == 'Y')
        if news_date == today and row[8].upper() == 'Y':  # Предполагаем, что дата в первом столбце, а 'Y' в 9-м (индекс 8)
            return {
                'title': row[1],
                'link': row[2],
                'image': row[3],
                'date': row[4],
                'full_text': row[5],
                'translated_text': row[6],
                'dictionary': row[7],
            }

    return None  # Возвращаем None, если подходящая новость не найдена


# Пример использования
def main():
    sheet_name = 'news_nhk_or_jp'
    news = get_today_news_from_sheet(sheet_name)

    if news:
        print("Новость за сегодня:")
        print(f"Заголовок: {news['title']}")
        dictionary = news['dictionary'].split('\n')

        print(f"dictionary: {dictionary}")
    else:
        print("Нет подходящей новости за сегодня.")


if __name__ == "__main__":
    main()