import pathlib
import csv
import re
from heapq import merge

# Директории хранения файлов .csv
inputPath = 'input'
outputPath = 'output'

# Наименование поля в котором осуществляется поиск
column_name = 'Contacts'

# Символ разделения полей
delimiter = ';'

# Регулярные выражения для поиска E-mail и телефонных номеров
email_pattern = re.compile(r'[0-9a-zA-Z\.-_]+@[\w\-_]+\.{1}\w{1,}')
phone_pattern = re.compile(r'(\+7\s?|8\s?|7\s?)?\(?\-?\d{3,}\s?\d*\)?\s?\-?\d*\-?\s?\d*\-?\d*\s?\d*\s?\d*')

# Нормализация телефонов
def normalizePhone(phone):
    phone = re.sub(r'[^\d]', '', phone)
    if len(phone) == 11: return re.sub(r'^(7|8)', '+7', phone)
    if len(phone) == 10: return '+7' + str(phone)
    if len(phone) == 6: return phone

# Обработка всех .csv файлов
inputDirectory = pathlib.Path(inputPath)

for input_file in inputDirectory.glob('*.csv'):  
    with open(input_file, encoding = 'cp1251') as File:
        reader = csv.DictReader(File, delimiter = delimiter)
        # Выходные данные для записи в итоговый файл
        output_data = []
        
        # Заголовки для новой таблицы
        table_headers = reader.fieldnames
        email_headers = []
        phone_headers = []
        
        # Построчный обход исходного файла
        for row in reader:
            emails_list = []
            phones_list = []
            
            # Разбитие строки для удобства обработки
            processing_data = re.split(r'[#,\:]', row[column_name])
            
            # Поиск необходимых контактных данных в полученном списке
            for contact_data in processing_data:
                # Проверка на наличие E-mail если email не найден попробуем найти телефон (сначала проверяем являются ли данные email, так как регулярное выражения для поиска номеров далеко от идеала)
                email = email_pattern.search(contact_data)
                if email:
                    emails_list.append(email.group(0))
                else:
                    phone = phone_pattern.search(contact_data)
                    if phone:
                        phone = normalizePhone(phone.group(0))
                        if phone: phones_list.append(phone)
            
            # Формирование словаря E-email
            if len(emails_list) > 0:
                emails = {}
                i = 0
                for email in sorted(set(emails_list)):
                    i += 1
                    key = 'email' + str(i)
                    emails.update({key: email})
                    # Добавление заголовка если такого ещё нет
                    if not key in email_headers: email_headers.append(key)
                row.update(emails)
            
            # Формирование словаря телефонов
            if len(phones_list) > 0:
                phones = {}
                i = 0
                for phone in sorted(set(phones_list)):
                    i += 1
                    key = 'phone' + str(i)
                    phones.update({key: phone})
                    # Добавление заголовка если такого ещё нет
                    if not key in phone_headers: phone_headers.append(key)
                row.update(phones)
            
            # Добвление новой строки в итоговые данные для конечного файла
            output_data.append(row)

        # Слияние списка заголовков дляитоговой таблицы
        table_headers = list(merge(table_headers, email_headers, phone_headers))
        
        # Файл итоговой таблицы
        output_file_name = str(input_file).replace(inputPath + '/', outputPath + '/result_')

        with open(output_file_name, 'w') as output_file:
            fieldnames = table_headers
            writer = csv.DictWriter(output_file, fieldnames = fieldnames, delimiter = delimiter)
        
            writer.writeheader()
            writer.writerows(output_data)

        print(len(output_data), table_headers)

        
