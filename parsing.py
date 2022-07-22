import requests
import bs4
from fake_useragent import UserAgent
import os
import time
import json

# Функции

def URL_to_Soup(url):
    headers = {
        "user-agent": UserAgent().random
    }
    # Добавляем условие на случай TimeoutError
    try:
        html = requests.get(url, headers=headers)
    except:
        t = 15
        for i in range(1,t+1):
            time.sleep(1)
            os.system('cls')
            print(f'Timeout {t + 1 - i} s')
        URL_to_Soup(url)

    return bs4.BeautifulSoup(html.content, 'lxml')

def Page_to_Characteristics(el):
    # time.sleep(random.randint(1, 2))
    url_product = url + '/product/' + el
    soup = URL_to_Soup(url_product)

    # Исключим страницы с курсами, на которых нет карточек товаров
    if soup.find('span', class_="music-course__pins-pin") == None:
        # Наименование
        try:
            name_product = soup.find('h1', class_='product-title').text
        except AttributeError:
            try:
                name_product = soup.find('li', class_='active').find('span', itemprop='name').text
            except AttributeError:
                name_product = 'Нет наименования'

        # Цена
        try:
            price = soup.find('li', class_='product-price').find('p').text.strip().replace(' р.', '').replace(' ', '')
        except AttributeError:
            price = 'Цена не установлена/Цена по запросу'

        # Цена по акции
        try:
            action_price = soup.find('h1', class_='product-title').text
        except AttributeError:
            try:
                action_price = soup.find('li', class_='active').find('span', itemprop='name').text
            except AttributeError:
                action_price = 'Скидки нет'

        # Цена аренды в сутки, если есть аренда
        try:
            rent = soup.find('a', class_='button rent').text.strip().replace('В аренду от ', '').replace(' руб. в день', '')
        except AttributeError:
            rent = 'Аренды нет'

        # Оценка
        try:
            rating = soup.find('span', class_='rating__value').text
        except AttributeError:
            rating = 'Оценок нет'

        # Категория товара
        try:
            category = soup.find('span', class_='product-category').text
        except AttributeError:
            category = 'Без категории'

        # Ссылка на изображение
        try:
            img = soup.find('img', alt=name_product).get('data-src')
        except AttributeError:
            img = 'Нет изображения'

        # Наличие
        try:
            Availability = soup.find('div', class_="product-info__available").text
        except AttributeError:
            Availability = "Нет информации"

        # Краткое описание
        try:
            short_description = soup.find('div', class_="product-info__i _description").text.replace('\n', '').strip()
        except AttributeError:
            short_description = 'Нет'

        # Основные характеристики
        characteristics = {
            "Ссылка на товар": url_product,
            "Ссылка на изображение": img,
            "Категория товара": category,
            "Наименование": name_product,
            "Артикул": el,
            "Наличие": Availability,
            "Краткое описание": short_description,
            "Цена": price,
            "Цена по акции": action_price,
            "Начальная цена аренды в день": rent,
            "Рейтинг": rating
        }

        # Дополнительные характеристики
        list_char = soup.find_all('li')
        additional_characteristics = {}
        for el in list_char:
            str_el = el.text.strip()
            if len(str_el) <= 150 and (str_el.find(': ') != -1):
                list_el = el.text.strip().split(': ')
                additional_characteristics.update({list_el[0]: list_el[1]})

        # Полное описание товара
        try:
            full_description = ''
            description = soup.find('div', itemprop="description").get_text()
            for el in description.split('\n'):
                if el.find(': ') != -1 and len('el') < 150:
                    sub_el = el.split(': ')
                    additional_characteristics.update({sub_el[0]: sub_el[1]})
                else:
                    full_description = ''.join([full_description, el.replace('\n', '')]).strip()
        except AttributeError:
            full_description = 'Нет'

        # Дополнение списка характеристик
        characteristics.update({"Полное описание": full_description})
        characteristics.update(additional_characteristics)
        #pprint(characteristics)
        return characteristics

# Базовый адрес
url = 'https://www.muztorg.ru'

# # 1. Забираем главную страницу с сайта и записываем в файл, чтобы не делать запросы на сайт
# html = URL_to_Soup(url)
# with open('data/homepage.html', 'w', encoding='UTF-8') as file:
#     file.write(html.text)
#     file.close()

# # 2. Работаем с сохранённой страницей
# with open('data/homepage.html', encoding='UTF-8') as file:
#     html = file.read()
#     file.close()
# soup = bs4.BeautifulSoup(html, 'lxml')
# list_soup_category = soup.find_all('div', class_='catalog-menu__i')

# # 3. Формируем список ссылок на категории товаров, имеющиеся на сайте
# categories_list = []
# for category in list_soup_category:
#     list_sub_category = category.find_all('div', class_='catalog-menu__category')
#     for sub_category in list_sub_category:
#         # print(sub_category.find('a').get('href'))
#         categories_list.append(url + sub_category.find('a').get('href'))

# 4. Формируем список артикулов товаров по категориям, записываем артикулы каждой категории в отдельный файл
for cat in range(1, len(categories_list)):
    category = categories_list[cat-1]
    soup = URL_to_Soup(category)
    category_name ='0'*(3-len(str(cat))) + str(cat) +  '_' + soup.find('h1').text.strip().replace('/', 'и')
    print(category_name)
    try:
        pages = int(soup.find('span', class_='category-head__badge').text)
    except AttributeError:
        pages = 1
    if pages % 24 == 0:
        pages = int(pages/24)
    else:
        pages = int(pages/24) + 1
    product_info = []
    for page in range(1, pages + 1):
        url = category + '?in-stock=1&pre-order=1&page=' + str(page)
        soup = URL_to_Soup(url)
        product_card_list = soup.find_all('a', itemprop="image")
        for page in product_card_list:
            product_info.append(page.get('href').replace('/product/',''))
    with open(os.getcwd() + '\\list\\' + f'{category_name}.txt', 'w', encoding='UTF-8') as file:
        for i in product_info:
            file.write(i + '\n')
        file.close()