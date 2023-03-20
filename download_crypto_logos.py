from requests_html import HTMLSession, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
from time import sleep
import argparse

BASE_URL = "https://cryptologos.cc/"

try:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true") 
    args = parser.parse_args()

    session = HTMLSession()
    response = session.get(BASE_URL)
    response.html.render()
    soup = BeautifulSoup(response.html.html, "html.parser")

    a_tags = soup.select("div.col > div > a")

    coins = []
    for a_tag in a_tags:
        coins.append(urljoin(BASE_URL,a_tag["href"]))

    if args.fast:
        downloaded_coins = os.listdir("./logos")
    else:
        downloaded_coins = []

    for coin in coins:
        URL = coin
        DIC_PATH = urlparse(coin).path.split("/")[-1]

        if DIC_PATH in downloaded_coins:
            print("skipped")
            continue

        RETRY_COUNT = 3
        continue_flag = False
        for i in range(RETRY_COUNT):
            session = HTMLSession()
            response = session.get(coin)
            if response.status_code != 200:
                if i == RETRY_COUNT-1:
                    continue_flag = True
                print("Error. Retry after 10 seconds.")
                sleep(10)
                continue
            response.html.render(timeout=20)
            break
        
        if continue_flag:
            continue
        
        soup = BeautifulSoup(response.html.html, "html.parser")
        div_tags = soup.select("div.site-content > div > div > div.product-content")

        logo_urls = []
        for div in div_tags:
            logo_urls.append(urljoin(URL,div.select_one("div > a")["href"]))

        for url in logo_urls:
            RETRY_COUNT = 3
            for _ in range(RETRY_COUNT):
                response = requests.get(url)

                if response.status_code != 200:
                    print("Error. Retry after 10 seconds.")
                    sleep(10)
                    continue
                else:
                    print(url)

                data = response.content

                file_path = os.path.join("./logos", DIC_PATH, urlparse(url).path.split("/")[-1])
                if not os.path.exists(os.path.join("./logos", DIC_PATH)):
                    os.makedirs(os.path.join("./logos", DIC_PATH))
                
                with open(file_path, "wb") as f:
                    f.write(data)

                break
            sleep(1)
except KeyboardInterrupt as e:
    print(e)

except Exception as e:
    print(e)