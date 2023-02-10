import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from selenium.common import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import random
import json

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
}
options = webdriver.ChromeOptions()


def get_source_html(url):
    driver = webdriver.Chrome("/home/walilentin/PycharmProjects/Parsing_site/chromedriver", options=options)

    driver.maximize_window()

    try:
        driver.get(url=url)
        time.sleep(5)

        while True:

            try:
                find_more_element = driver.find_element(By.CLASS_NAME, f"show-more__text").click()
                time.sleep(3)
                if driver.find_elements(By.CLASS_NAME,
                                        "button button--gray button--medium pagination__direction pagination__direction--forward ng-star-inserted pagination__direction--disabled"):
                    break
            except NoSuchElementException:
                with open("sourse_page.html", "w") as file:
                    file.write(driver.page_source)
                break
            # else:
            #     actions = ActionChains(driver)
            #     actions.move_to_element(find_more_element).perform()
            #     time.sleep(5)

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def get_items_url(file):
    with open(file) as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")
    item_a = soup.find_all("div", class_="goods-tile__inner")
    urls = []
    for item in item_a:
        item_url = item.find("a", class_="goods-tile__picture ng-star-inserted").get("href")
        urls.append(item_url)

    with open("items_url.txt", "w") as file:
        for url in urls:
            file.write(f"{url}\n")
    return "[INFO] urls are append"


def get_data(file):
    with open(file) as file:
        urls_list = [url.strip() for url in file.readlines()]

        # urls_list = file.readlines()
        # print(urls_list)
        # clear_urls = []
        # for i in urls_list:
        #     i = i.strip()
        #     clear_urls.append(i)
        # #print(clear_urls)
    resoul_list = []
    urls_count = len(urls_list)
    count = 1
    for url in urls_list:
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")

        item_name_laptop_main = []
        my_url = []
        presence = ''
        try:
            try:
                presence_yes = soup.find("p", class_="status-label status-label--green ng-star-inserted").find(
                    "use").get("href")
                if presence_yes == "#icon-okay":
                    presence += 'Є в наявності'

            except Exception as ex:
                presence_yes = soup.find("p", class_="status-label status-label--orange ng-star-inserted").find(
                    "use").get("href")
                if presence_yes == "#icon-clock":
                    presence += 'Закінчується'

        except Exception as ex:
            presence += 'Немає в наявності'

        try:
            item_url = soup.find(type="alternate").get("href")
            my_url.append(item_url)
        except Exception as ex:
            my_url = None

        try:
            item_laptop = soup.find("h1", class_="product__title").text.strip()
            item_name_laptop_main.append(item_laptop)
        except Exception as ex:
            item_name_laptop_main = None
        item_no_action_price_main = ''

        try:
            item_no_action_price = soup.find("p", class_="product-prices__small ng-star-inserted").text.strip()
            # item_no_action_price_main.append(item_no_action_price)
            for i in item_no_action_price[0:-1]:
                x = i.isdigit()
                if x == True:
                    item_no_action_price_main += i
                else:
                    item_no_action_price_main += '.'
        except Exception as ex:
            item_no_action_price_main += 'Ціна не вказана на сайті'
            # item_no_action_price = soup.find("p", class_="product-prices__big").text.strip()
            # # item_no_action_price_main.append(item_no_action_price)
            # for i in item_no_action_price[0:-1]:
            #     x = i.isdigit()
            #     if x == True:
            #         item_no_action_price_main += i
            #     else:
            #         item_no_action_price_main += '.'

        item_with_action_price = ''
        
        try:
            item_action_price = soup.find("p", class_="product-prices__big product-prices__big_color_red").text.strip()
            # item_with_action_price.append(item_action_price)
            for i in item_action_price[0:-1]:
                x = i.isdigit()

                if x == True:
                    item_with_action_price += i
                else:
                    item_with_action_price += '.'

        except Exception as ex:
            item_name = None
        resoul_list.append({
            "Модель": item_name_laptop_main,
            "Ціна зі знижкою:": item_with_action_price,
            "Ціна без знижки:": item_no_action_price_main,
            "Посилання:": url,
            "Наявність:": presence,
        })
        print(f"[+] Processed: {count}/{urls_count}")
        count += 1
    with open("pars.json", "w") as file:
        json.dump(resoul_list, file, indent=4, ensure_ascii=False)
    return print("[INFO] Data collected succssefully!")


def main():
    # get_source_html(url="https://rozetka.com.ua/notebooks/c80004/producer=apple/")
    # print(get_items_url(file="/home/walilentin/PycharmProjects/Parsing_ROZETKA/sourse_page.html"))
    print(get_data(file="/home/walilentin/PycharmProjects/Parsing_ROZETKA/items_url.txt"))


if __name__ == "__main__":
    main()
