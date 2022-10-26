from dis import disco
from turtle import title
from webbrowser import get
from requests_html import HTMLSession
import json
import re
from gmail import createMessage

def getData():
    with open('data.json') as file:
        data = json.load(file)
    return data

def saveData(data):
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)

def scrape(asin):
    session = HTMLSession()
    page = session.get(f'https://www.amazon.ca/gp/product/{asin}')
    page.html.render(timeout=20)  
    title = page.html.find('#productTitle')[0].text    
    try:
        price = page.html.find('.a-offscreen')[0].text.replace('$','').strip()
    except:
        whole = page.html.find('.a-price-whole')[0].text
        fraction = page.html.find('.a-price-fraction')[0].text
        price = whole+fraction
    print(title, price)
    return price, title

def track(link, email, username):
    newAsin = re.search(r'/[dg]p/([^/]+)', link, flags=re.IGNORECASE).group(1)
    data = getData()
    if newAsin in data["ASIN"] and username not in data["ASIN"][newAsin][0]["usernames"]:
        data["ASIN"][newAsin][0]["emails"].append(email)
        data["ASIN"][newAsin][0]["usernames"].append(username)
    elif newAsin not in data["ASIN"]:
        price = scrape(newAsin)
        info = {f"{newAsin}": [
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
        price_title = scrape(asin)
        comparePrice(price_title, asin)

main()