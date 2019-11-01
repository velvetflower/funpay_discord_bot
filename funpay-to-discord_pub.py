from bs4 import BeautifulSoup
import requests
import discord
from time import sleep
import datetime
import aiohttp
from random import randint

# created for lots in world of warcraft section

# FILL THIS VARIABLES
ourName = "yourName"
discord_bot_key = ""
PHPSESSID_key = ""
golden_key = ""
cfduid = ""

max_price = 0
min_price = 0
min_hour = 0
max_hour = 0
max_mins = 0
min_mins = 0

myPrice = 0
myAmount = 0
currentDay = datetime.datetime.now().day

headers = {
    'authority': 'funpay.ru',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36 OPR/63.0.3368.56786',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'dnt': '1',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'sec-fetch-site': 'none',
    'referer': 'https://funpay.ru/',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cookie': f'PHPSESSID={PHPSESSID_key}; golden_key={golden_key}; __cfduid={cfduid}',
}

newsess = requests.Session()
#auth = newsess.get("https://funpay.ru/", headers=headers)

def countComission(price):
    comission = (float(price)/100) * 19
    endComission = float(price) - comission - 0.01 # sub 19% and cut 0.01 from first seller's price
    return round(endComission, 2)

def get_data():
    global max_price
    global min_price
    global currentDay
    global myPrice
    global myAmount
    global min_hour
    global max_hour
    global max_mins
    global min_mins

    sellerNameList = []
    sellerPriceList = []
    sellerAmountList = []

    auth = newsess.get("https://funpay.ru/chips/114/", headers=headers).text # get page
    soup = BeautifulSoup(auth, features="html.parser") # load soup

    # поиск кол-ва сообщений
    bds = "0"
    try:
        ads = soup.find_all('div', class_='collapse navbar-collapse no-transition')
        bds = ads[0].find_all('span', {'class' : 'badge badge-chat'})[0].text
    except:
        messages = 0
    if int(bds) > 0:
        messages = int(bds)

    # основной модуль
    ads = soup.find_all('div', class_='tc-item showcase-row tc-sortable-row')
    for i in ads:
        server = i["data-server"]
        side = i["data-side"]
        try:
            status = i["data-online"]
        except:
            status = '0'
        if server == '2966' and side == '47' and status == '1':
            price = i.find_all('div', class_='tc-price price')[0].find('div').next_element.replace(" ","")
            amount = i.find_all('div', class_='tc-amount amount')[0].next
            name = i.find_all('div', class_='media-user-name')[0].text
            sellerNameList.append(name)
            sellerPriceList.append(price)
            sellerAmountList.append(amount)
    
    myPosition = 999
    if ourName in sellerNameList:
        myPosition = sellerNameList.index(ourName)
        myPrice = countComission(sellerPriceList[myPosition])
        myAmount = sellerAmountList[myPosition]
    
    if myPosition == 999:
        myPosition = f"дальше {len(sellerNameList)} места"

    cur_price = countComission(sellerPriceList[0])

    if cur_price < min_price or min_price == 0:
        min_price = cur_price
        min_hour = datetime.datetime.now().hour
        min_mins = datetime.datetime.now().minute
    if cur_price > max_price or max_price == 0:
        max_price = cur_price
        max_hour = datetime.datetime.now().hour
        max_mins = datetime.datetime.now().minute

    if datetime.datetime.now().day != currentDay:
        currentDay = datetime.datetime.now().day
        min_price = 0
        max_price = 0
    
    min_profit = min_price * int(myAmount)
    max_profit = max_price * int(myAmount)
    cur_profit = cur_price * int(myAmount)

    #continue here
    line1 = f"1. {sellerNameList[0]}  {sellerPriceList[0]}₽  ( {(countComission(sellerPriceList[0]))}₽ )  {sellerAmountList[0]}g"
    line2 = f"2. {sellerNameList[1]}  {sellerPriceList[1]}₽  ( {(countComission(sellerPriceList[1]))}₽ )  {sellerAmountList[1]}g"
    line3 = f"3. {sellerNameList[2]}  {sellerPriceList[2]}₽  ( {(countComission(sellerPriceList[2]))}₽ )  {sellerAmountList[2]}g"
    line4 = f"4. {sellerNameList[3]}  {sellerPriceList[3]}₽  ( {(countComission(sellerPriceList[3]))}₽ )  {sellerAmountList[3]}g"
    line5 = f"5. {sellerNameList[4]}  {sellerPriceList[4]}₽  ( {(countComission(sellerPriceList[4]))}₽ )  {sellerAmountList[4]}g"

    true_data = f""">>> ======================
Msg: {messages} | Upd: {'{0:%H:%M:%S}'.format(datetime.datetime.now())}
-------
{line1}
{line2}
{line3}
{line4}
{line5}
-------
Позиция: {myPosition + 1} место => {myPrice}₽ * {myAmount}g | выгода: {round(cur_profit,2)}
Макс. цена: << {max_price} >> в {max_hour}:{max_mins} | выгода: {round(max_profit,2)}
Мин. цена: << {min_price} >> в {min_hour}:{min_mins} | выгода: {round(min_profit,2)}
======================"""
    return true_data

client = discord.Client()

async def background():
    while True:
        try:
            info_text = get_data()
            await client.wait_until_ready()
            channel = client.get_channel(int(636458021135843330))
            await channel.send(info_text)
            sleep(randint(300,600))
        except Exception as e:
            print (e)
            sleep(120)
            continue

client.loop.create_task(background())
client.run(discord_bot_key)