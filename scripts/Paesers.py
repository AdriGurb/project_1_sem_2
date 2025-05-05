import re
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


def to_num(str_) -> int:
    str_ = str_.replace('\u2006', ' ')
    int_ = int(re.sub(r"[^0-9]", "", str_))
    return int_

def ozon(req, driver, df):
    # поиск
    time.sleep(0.3)
    search_input = driver.find_element("css selector", 'input[placeholder="Искать на Ozon"]')
    search_input.click()
    search_input.clear()
    search_input.send_keys(req)
    search_input.send_keys(Keys.RETURN)
    #прогрузка динамического контента
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1.5)
    
    # Собираем данные и парсим
    from bs4 import BeautifulSoup
    html_text = driver.page_source
    soup = BeautifulSoup(html_text, "html.parser")
    items = soup.find_all('div', class_="jr8_25")
    
    #записываем в датафрейм
    for item in items:
        try:
            # Название товара
            title = item.find('span', class_='tsBody500Medium').text.strip()
            # Цена
            price = item.find('span', class_='tsHeadline500Medium').text.strip()
        
            rating_block = item.find_all('span', class_="p6b21-a4")
            len_rb = len(rating_block)
            rating = rating_block[len_rb - 2].find_all('span')[0].text.strip()
            reviews = to_num(rating_block[len_rb - 1].find_all('span')[0].text.strip())
            # Ссылка на товар
            link = item.find('a', class_='tile-clickable-element')['href']
            full_link = f"https://www.ozon.ru{link}" if link.startswith('/') else link
        except:
            continue
        df.loc[len(df)] = [title, price, rating, reviews, "ozon", full_link, req]
        
    return df

def yand(req, driver, df):
    time.sleep(0.4)
    search_input = driver.find_element(By.ID, "header-search")
    search_input.click()
    search_input.clear()
    search_input.send_keys(req)
    search_input.send_keys(Keys.RETURN)
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        driver.execute_script("window.scrollBy(0, -200)")
        time.sleep(1.9)
    
    from bs4 import BeautifulSoup
    html_text = driver.page_source
    soup = BeautifulSoup(html_text, "html.parser")
    items = soup.find_all('div', class_="_1H-VK")
    #
    for item in items:
        try:
            # Название товара
            title = item.find('div', class_='cia-cs _1pFpJ').text.strip()
            # Цена
            price = to_num(item.find('span', class_='ds-valueLine DPiFo').text.strip())
        
            rating = item.find('span', class_='ds-text ds-text_weight_bold ds-text_color_text-rating ds-text_proportional ds-text_typography_text ds-rating__value ds-text_text_tight ds-text_text_bold').text.strip()
            reviews = to_num(item.find('span', class_='ds-text ds-text_lineClamp_1 ds-text_weight_reg ds-text_color_text-secondary ds-text_proportional ds-text_typography_text ds-text_text_tight ds-text_text_reg ds-text_lineClamp').text.strip())
            # Ссылка на товар
            link = item.find('a', href=lambda href: href and href.startswith('/product'))['href']
            full_link = f"https://market.yandex.ru{link}" if link.startswith('/') else link
        except:
            continue
        df.loc[len(df)] = [title, price, rating, reviews, "yand", full_link, req]
        
    return df

def cuter(str_):
    "обрезает строку, передаёт её и место до куда обрезали. Нужна для парсинга вб"
    if str_[1] == ".":
        return str_[:3], 3
    else:
        str_[0], 0

def wb(req, driver, df):
    time.sleep(0.3)
    search_input = driver.find_element(By.ID, "searchInput")
    search_input.click()
    search_input.clear()
    search_input.send_keys(req)
    search_input.send_keys(Keys.RETURN)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        driver.execute_script("window.scrollBy(0, -200)")
        time.sleep(1.9)
    
    from bs4 import BeautifulSoup
    html_text = driver.page_source
    soup = BeautifulSoup(html_text, "html.parser")
    items = soup.find_all('article', class_='product-card')
    #
    for item in items:
        try:
            # Название товара
            title = item.find('a', class_='product-card__link j-card-link j-open-full-product-card').get('aria-label')
            # Цена
            price = item.find('div', class_='product-card__price price').text.strip()
            price = to_num(price[:price.find("₽")])
            
            rating, len_ = cuter(item.find('p', class_='product-card__rating-wrap').text.strip().replace(',', '.'))
            reviews = to_num(item.find('p', class_='product-card__rating-wrap').text.strip()[len_:])
            # Ссылка на товар
            link = item.find('a', class_='product-card__link j-card-link j-open-full-product-card').get('href')
            full_link = f"https://market.yandex.ru{link}" if link.startswith('/') else link
        except:
            continue
        df.loc[len(df)] = [title, price, rating, reviews, "wb", full_link, req]
        
    return df
