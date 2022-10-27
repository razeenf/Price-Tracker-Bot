from requests_html import AsyncHTMLSession
import asyncio
import json
from gmail import createMessage

def getData():
    with open('data.json') as file:
        data = json.load(file)
    return data

def saveData(data):
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)

from requests_html import AsyncHTMLSession
import asyncio

async def scrape(asin):
    asession = AsyncHTMLSession() 
    page = await asession.get(f'https://www.amazon.ca/gp/product/{asin}')
    await page.html.arender(timeout = 10) # sleeping is optional but do it just in case 
    try:
        title = page.html.find('#productTitle')[0].text 
        price = page.html.find('.a-offscreen')[0].text.replace('$','').strip()
    except:
        whole = page.html.find('.a-price-whole')[0].text
        fraction = page.html.find('.a-price-fraction')[0].text
        price = whole+fraction
    await asession.close() # this part is important otherwise the Unwanted Kill.Chrome Error can Occur 
    print(title, price)
    return price, title

async def track(asin, email, username):
    data = getData()
    if asin in data["ASIN"] and username not in data["ASIN"][asin][0]["usernames"]:
        data["ASIN"][asin][0]["emails"].append(email)
        data["ASIN"][asin][0]["usernames"].append(username)
    elif asin not in data["ASIN"]:
        price = (await scrape(asin))[0]
        info = {f"{asin}": [
            {
                "price": float(price),
                "emails": [
                    f"{email}"
                ],
                "usernames": [
                    f"{username}"
                ]
            }
        ]}
        data["ASIN"].update(info)
    saveData(data)

def notify(asin, title, price, listedPrice, discount):
    data = getData()
    emailList = data["ASIN"][asin][0]["emails"]
    index = 0
    for email in emailList:
        username = data["ASIN"][asin][0]["usernames"][index]
        createMessage(email, username, title, price, listedPrice, discount, asin) 
        index+=1
    del data["ASIN"][asin]
    saveData(data)

def comparePrice(price_title, asin):
    price = price_title[0]
    title = price_title[1]
    data = getData()
    listedPrice = data["ASIN"][asin][0]["price"]
    if float(price) < listedPrice:
        discount = int(((listedPrice-float(price))/listedPrice)*100)
        print("On sale. Sending out emails...")
        notify(asin, title, price, listedPrice, discount)
    else:
        print("No sale.")

def main():
    data = getData()
    for asin in data["ASIN"]:
        price_title = asyncio.run(scrape(asin))
        comparePrice(price_title, asin)

if __name__ == "__main__":
    main()