from requests_html import HTMLSession
import json
import re

def scrape(asin):
    session = HTMLSession()
    page = session.get(f'https://www.amazon.ca/gp/product/{asin}')
    page.html.render(sleep=1)  
    title = page.html.find('#productTitle')[0].text    
    try:
        price = page.html.find('.a-offscreen')[0].text.replace('$','').strip()
    except:
        whole = page.html.find('.a-price-whole')[0].text
        fraction = page.html.find('.a-price-fraction')[0].text
        price = whole+fraction
    print(title, price)
    return price

def track(link, email, username):
    newAsin = re.search(r'/[dg]p/([^/]+)', link, flags=re.IGNORECASE).group(1)
    with open('data.json') as file:
        data = json.load(file)

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

    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)

def notify(asin):
    # use gmail api here 
    with open("data.json") as file:
        data = json.load(file)
    del data["ASIN"][asin]
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)

def comparePrice(price, asin):
    listedPrice = data["ASIN"][asin][0]["price"]
    if float(price) < listedPrice:
        discount = int(((listedPrice-float(price))/listedPrice)*100)
        print(f"Product was {listedPrice}, now on sale for {price}!! That's a savings of {discount}%.")
        notify(asin)
    else:
        print("No sale.")

with open('data.json') as file:
    data = json.load(file)

def main():
    for asin in data["ASIN"]:
        price = scrape(asin)
        comparePrice(price, asin)

main()