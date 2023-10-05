from selenium import webdriver
import time
import lxml
from bs4 import BeautifulSoup
import csv


# функция для сохранения html документа страницы (ничего не возвращает, сохраняет файл)
def save_html(url, file_counter='index', page_counter='', page_number=''):
    driver = webdriver.Chrome(
        executable_path=r'C:\Users\budgi\PycharmProjects\Python Projects\Диплом\парсер\chromedriver.exe')

    try:
        if page_counter != '':
            driver.get(url=f'{url}{page_counter}')
            time.sleep(10)

            with open(f'htmls\{file_counter}{page_number}.html', 'w', encoding="utf-8") as file:

                file.write(driver.page_source)

        else:
            driver.get(url=url)
            time.sleep(10)
            with open(f'htmls\{file_counter}.html', 'w', encoding="utf-8") as file:
                file.write(driver.page_source)

    except Exception as ex:
        print(ex)
    finally:
        print()
        driver.close()
        driver.quit()


def save_html_for_data(url, file_counter_for_data='index', page_counter='', page_number=''):
    driver = webdriver.Chrome(
        executable_path=r'C:\Users\budgi\PycharmProjects\Python Projects\Диплом\парсер\chromedriver.exe')

    try:
        if page_counter != '':
            driver.get(url=f'{url}{page_counter}')
            time.sleep(10)

            with open(f'htmls\{file_counter_for_data}{page_number}.html', 'w', encoding="utf-8") as file:

                file.write(driver.page_source)

        else:
            driver.get(url=url)
            time.sleep(10)
            with open(f'htmls\{file_counter_for_data}.html', 'w', encoding="utf-8") as file:
                file.write(driver.page_source)

    except Exception as ex:
        print(ex)
    finally:
        print()
        driver.close()
        driver.quit()


# фанкция для поиска ссылок на квартиры в html файле, вызывает функцию save_html для каждой ссылки на странице (чтобы
# сохранить html файл) (функция не подходит для парсинга самих объявлений (выгруженных ссылок))
# Ничего не возвращает, обращается к save_html()
def get_urls(file_counter='index'):
    with open(f'htmls\{file_counter}.html', encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    links = soup.find_all('a', class_='title-root-zZCwT')

    counter = 0
    for link in links:
        a = 'https://www.avito.ru' + link['href']
        save_html_for_data(url=a, file_counter_for_data=f'{file_counter} {counter}')

        counter += 1


# Функция для парсинга объявлений, получение информации о цене, этажах, количества комнат и т.д. Функция должна
# работать со всеми видами заполнения характеристик квартиры (некоторые не заполняют вкладку "санузес", "мебель" и т.д.
def get_data(file_counter):
    with open(f'D:/Диплом МГИМО/htmls/htmls/{file_counter}.html', encoding="utf-8") as file:
        src = file.read()
    soup = BeautifulSoup(src, 'lxml')

    # Списки со всеми характеристиками квартиры и дома
    list_for_characteristics_flat = []
    list_for_characteristics_house = []
    for i in soup.find_all('li', class_='params-paramsList__item-appQw'):
        list_for_characteristics_flat.append(i.text)
    for j in soup.find_all('li', class_='style-item-params-list-item-aXXql'):
        list_for_characteristics_house.append(j.text)

    # Список всех возможных характеристик квартиры
    full_list_characteristics_flat = ['Тип жилья', 'Этаж', 'Количество комнат', 'Тип комнат', 'Общая площад',
                                      'Площадь кухни', 'Жилая площадь', 'Высота потолков', 'Санузел', 'Окна', 'Отделка',
                                      'Ремонт']

    # Проверка на тип квартиры
    flat_type = None
    if 'Об апартаментах' in soup.find('span', class_='params-item-params-title-Of4wk').text:
        flat_type = 'Апартаменты'
    elif 'О квартире' in soup.find('span', class_='params-item-params-title-Of4wk').text:
        flat_type = 'Квартира'

    # Проверка на тип дома Вторичка/Новостройка
    building_type = None
    building_type_list = []
    for i in soup.find_all('span', class_='breadcrumbs-linkWrapper-jZP0j'):
        building_type_list.append(i.text)

    for k in building_type_list:
        if 'Новострой' in k:
            building_type = 'Новостройка'
        elif 'Вторич' in k:
            building_type = 'Вторичка'

    # Создание пустых значений характеристик,
    # в последующем они будут заменены на нормальные значения, если такие имеются на странице
    floor = None
    max_floor = None
    rooms = None
    rooms_type = None
    apartment_area = None
    kitchen_area = None
    living_area = None
    ceiling_height = None
    bathroom = None
    renovation = None
    finishing = None

    # Заполнение характеристик по условиям
    for character in list_for_characteristics_flat:
        for personal_character in full_list_characteristics_flat:
            if personal_character in character:
                if personal_character == 'Этаж':
                    floor = int(character.split()[-3])
                    max_floor = int(character.split()[-1])
                elif personal_character == 'Количество комнат':
                    try:
                        rooms = int(character.split()[-1])
                    except:
                        rooms_type = character.split()[-1]
                        rooms = character.split()[-1]
                elif personal_character == 'Тип комнат':
                    rooms_type = character.split()[-1]
                elif personal_character == 'Общая площад':
                    apartment_area = float(character.split()[-2])
                elif personal_character == 'Площадь кухни':
                    kitchen_area = float(character.split()[-2])
                elif personal_character == 'Жилая площадь':
                    living_area = float(character.split()[-2])
                elif personal_character == 'Высота потолков':
                    ceiling_height = float(character.split()[-2])
                elif personal_character == 'Санузел':
                    bathroom = character.split()[-1]
                elif personal_character == 'Ремонт':
                    renovation = character.split()[-1]
                elif personal_character == 'Отделка':
                    finishing = character.split()[-1]

    # Тоже тип дома, но тут уже не пр овторичку или новостройку, а про материал (кирпичный, монолитный)
    house_type = None
    for i in list_for_characteristics_house:
        if 'Тип дома' in i:
            house_type = i.split()[-1]

    # Название населенного пункта
    locality_name = None
    locality_list = []
    for i in soup.find_all('span', class_='style-item-address__string-wt61A'):
        locality_list.append(i.text)

    if locality_list != []:
        locality_name = locality_list

    # Ближайшее метро
    underground_list = []
    for i in soup.find_all('span', class_='style-item-address-georeferences-item-TZsrp'):
        underground_list.append(i.text)

    underground_nearest = None
    und = []
    for i in underground_list[0].split(): # Изменение = удалил [0] с конца (.split()[0])
        und.append(i) # Изменение = теперь без проверки
        '''try:
            int(i)
        except:
            if i != '–':
                und.append(i)'''

    if und != []:
        underground_nearest = ' '.join(und) # Изменение = поставил пробел

    # Цена, содавать None не надо, потому что если ее нет, то ее все равно потом удалять
    price = soup.find('span',
                      class_='js-item-price style-item-price-text-_w822 text-text-LurtD text-size-xxl-UPhmI').text
    price_lst = []
    for i in price.split():
        try:
            int(i)
            price_lst.append(i)
        except:
            pass

    price = int(''.join(price_lst))

    lst = [flat_type, floor, max_floor, rooms, rooms_type, apartment_area, kitchen_area, living_area,
           ceiling_height, bathroom, renovation, building_type, house_type, finishing, underground_nearest,
           locality_name, price]

    return lst


# Запись строк в csv файл
def append_to_csv(c):
    with open('data_v2.csv', 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        # w.writerow(['flat_type', 'floor', 'max_floor', 'rooms', 'rooms_type', 'apartment_area', 'kitchen_area',
        # 'living_area', 'ceiling_height', 'bathroom', 'renovation', 'building_type', 'house_type',
        # 'finishing', 'underground_nearest', 'locality_name', 'price'])
        try:
            w.writerow(get_data(c))
        except Exception as haha:
            print(haha)
            print(c)

# Список ссылок, по которым уже прошелся
'''list_of_urls = ['https://www.avito.ru/moskva/kvartiry/prodam-ASgBAgICAUSSA8YQ',
                    'https://www.avito.ru/moskva/kvartiry/prodam/1-komnatnye-ASgBAQICAUSSA8YQAUDKCBSAWQ?f=ASgBAQECAUSSA8YQAUDKCBSAWQFFxpoMF3siZnJvbSI6MCwidG8iOjk1MDAwMDB9',
                    'https://www.avito.ru/moskva/kvartiry/prodam/1-komnatnye-ASgBAQICAUSSA8YQAUDKCBSAWQ?f=ASgBAQECAUSSA8YQAUDKCBSAWQFFxpoMHnsiZnJvbSI6OTUwMDAwMCwidG8iOjE0MDAwMDAwfQ',
                    'https://www.avito.ru/moskva/kvartiry/prodam/1-komnatnye-ASgBAQICAUSSA8YQAUDKCBSAWQ?f=ASgBAQECAUSSA8YQAUDKCBSAWQFFxpoMGHsiZnJvbSI6MTQwMDAwMDAsInRvIjowfQ',
                    'https://www.avito.ru/moskva/kvartiry/prodam/2-komnatnye-ASgBAQICAUSSA8YQAUDKCBSCWQ?f=ASgBAQECAUSSA8YQAUDKCBSCWQFFxpoMGHsiZnJvbSI6MCwidG8iOjExNTAwMDAwfQ',
                    'https://www.avito.ru/moskva/kvartiry/prodam/2-komnatnye-ASgBAQICAUSSA8YQAUDKCBSCWQ?f=ASgBAQECAUSSA8YQAUDKCBSCWQFFxpoMH3siZnJvbSI6MTE1MDAwMDAsInRvIjoxNDAwMDAwMH0',
                    'https://www.avito.ru/moskva/kvartiry/prodam/2-komnatnye-ASgBAQICAUSSA8YQAUDKCBSCWQ?f=ASgBAQECAUSSA8YQAUDKCBSCWQFFxpoMH3siZnJvbSI6MTE1MDAwMDAsInRvIjoxNDAwMDAwMH0&localPriority=0'.
                    'https://www.avito.ru/moskva/kvartiry/prodam/2-komnatnye-ASgBAQICAUSSA8YQAUDKCBSCWQ?f=ASgBAQECAUSSA8YQAUDKCBSCWQFFxpoMH3siZnJvbSI6MTQwMDAwMDAsInRvIjoxODAwMDAwMH0&localPriority=0'.
                    'https://www.avito.ru/moskva/kvartiry/prodam/2-komnatnye-ASgBAQICAUSSA8YQAUDKCBSCWQ?f=ASgBAQECAUSSA8YQAUDKCBSCWQFFxpoMH3siZnJvbSI6MTgwMDAwMDAsInRvIjoyNjAwMDAwMH0&localPriority=0',
                    'https://www.avito.ru/moskva/kvartiry/prodam/2-komnatnye-ASgBAQICAUSSA8YQAUDKCBSCWQ?f=ASgBAQECAUSSA8YQAUDKCBSCWQFFxpoMGHsiZnJvbSI6MjYwMDAwMDAsInRvIjowfQ',
                    'https://www.avito.ru/moskva/kvartiry/prodam/3-komnatnye-ASgBAQICAUSSA8YQAUDKCBSEWQ?f=ASgBAQECAUSSA8YQAUDKCBSEWQFFxpoMGHsiZnJvbSI6MCwidG8iOjE4MDAwMDAwfQ',
                    'https://www.avito.ru/moskva/kvartiry/prodam/3-komnatnye-ASgBAQICAUSSA8YQAUDKCBSEWQ?f=ASgBAQECAUSSA8YQAUDKCBSEWQFFxpoMH3siZnJvbSI6MTgwMDAwMDAsInRvIjoyNzAwMDAwMH0',
                    'https://www.avito.ru/moskva/kvartiry/prodam/3-komnatnye-ASgBAQICAUSSA8YQAUDKCBSEWQ?f=ASgBAQECAUSSA8YQAUDKCBSEWQFFxpoMH3siZnJvbSI6MjcwMDAwMDAsInRvIjo1MDAwMDAwMH0',
                    'https://www.avito.ru/moskva/kvartiry/prodam/3-komnatnye-ASgBAQICAUSSA8YQAUDKCBSEWQ?f=ASgBAQECAUSSA8YQAUDKCBSEWQFFxpoMGHsiZnJvbSI6NTAwMDAwMDAsInRvIjowfQ',
                    'https://www.avito.ru/moskva/kvartiry/prodam/4-komnatnye-ASgBAQICAUSSA8YQAUDKCBSGWQ',
                    'https://www.avito.ru/moskva/kvartiry/prodam-ASgBAgICAUSSA8YQ?f=ASgBAQICAUSSA8YQAUDKCGSKWZqsAZisAZasAZSsAYhZ',
                    'https://www.avito.ru/moskva/kvartiry/prodam/svobodnaya_planirovka-ASgBAQICAUSSA8YQAUDKCBT8zzI']'''


# Список названий файлов
'''list_of_file_names = ['index', 'index_1_room', 'index_second_1_room', 'index_third_1_room',
                         'index_2_room', 'index_second_2_room', 'index_third_2_room', 'index_fourth_2_room', 'index_fifth_2_room', 'index_sixth_2_room', 
                         'index_3_room', 'index_second_3_room',  'index_third_3_room', 'index_fourth_3_room',
                         'index_4_room',
                         'index_5_room',
                         'index_free_room']'''


if __name__ == '__main__':
    list_of_file_names = ['index', 'index_1_room', 'index_second_1_room', 'index_third_1_room',
                          'index_2_room', 'index_second_2_room', 'index_third_2_room', 'index_fourth_2_room',
                          'index_fifth_2_room', 'index_sixth_2_room',
                          'index_3_room', 'index_second_3_room', 'index_third_3_room', 'index_fourth_3_room',
                          'index_4_room',
                          'index_5_room',
                          'index_free_room']

    # Код для добавления данных в csv файл
    for index in list_of_file_names:
        for page in range(101):
            for apartment in range(53):
                if page == 0:
                    apartment_index = index + " " + str(apartment)
                else:
                    apartment_index = index + str(page) + " " + str(apartment)

                try:
                    append_to_csv(apartment_index)
                except Exception as ex:
                    print(ex)











'''    # Код для сохранения хтмл страниц с 52 ссылками (для дальнейшего парсинга)
    url = 'https://www.avito.ru/moskva/kvartiry/prodam/svobodnaya_planirovka-ASgBAQICAUSSA8YQAUDKCBT8zzI'
    for i in range(1, 12):
        try:
            if i == 1:
                k = ''
            else:
                # Переименовать переменную, которая задает ссылку для новой страницы
                k = f'?p={i}' #------------------------ Эта часть может менятся ----------------------
            # ---------ВНИМЕНИЕ!!! file_counter надо менять, когда запускаем скрипт для новой ссылки---------------
            save_html(url=url, page_counter=k, page_number=i, file_counter='index_free_room')
        except Exception as ex:
            print('--------------------------------')
            print(url)
            print(f'file_counter = index{i}')
            print(f'page_counter = {i}')
            print()
            print(ex)


    # Код для прохождения по страницам с 52 объявлениями
    for i in range(1, 12):
        try:
            if i == 1:
                j = ''
                # ---------ВНИМЕНИЕ!!! file_counter надо менять, когда запускаем скрипт для новой ссылки---------------
                get_urls(file_counter=f'index_free_room{j}')
            else:
                get_urls(file_counter=f'index_free_room{i}')
        except Exception as ex:
            print('--------------------------------')
            print()
            print(ex)'''








