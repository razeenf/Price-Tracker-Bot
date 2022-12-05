from requests_html import AsyncHTMLSession

class Scraper():

    async def req(self, asin):
        session = await AsyncHTMLSession().get(f'https://www.amazon.ca/gp/product/{asin}')
        print("Status:", session.status_code)
        await session.html.arender(timeout = 20) 
        return session
        
    async def get_price(self, asin):
        session = await self.req(asin) 
        try:
            price = session.html.find('.a-offscreen')[0].text.replace('$','').strip()
        except IndexError:
            whole = session.html.find('.a-price-whole')[0].text
            fraction = session.html.find('.a-price-fraction')[0].text
            price = whole+fraction  
        session.close()
        try:
            float(price)
            print("Price: $" + price)
        except ValueError:
            print("Out of Stock.")
            return 
        return price
        
    async def get_details(self, asin):
        session = await self.req(asin)
        title = session.html.find('#productTitle')[0].text 
        div = session.html.find('#imgTagWrapperId')[0]
        img = div.xpath('//img/@src')[0]
        session.close()
        return title, img