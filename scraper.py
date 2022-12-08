from requests_html import AsyncHTMLSession

class Scraper:
    async def scrape(self, key, asin): # BIG MEMORY LEAK FIX ASAP TOO MANY CHROMIUM INSTANCES
        asession = AsyncHTMLSession()
        page = await asession.get(f'https://www.amazon.ca/dp/{asin}')
        print("Status:", page.status_code)
        await page.html.arender(timeout = 20) 
        match key:
            case 'price':
                data = self.get_price(page)
            case 'title':
                data = self.get_title(page)
            case 'img':
                data = self.get_img(page)
            case _:
                return 'Error'
        await asession.close()
        return data
        
    def get_price(self, page):
        try:
            price = page.html.find('.a-offscreen')[0].text.replace('$','').strip()
        except IndexError:
            whole = page.html.find('.a-price-whole')[0].text
            fraction = page.html.find('.a-price-fraction')[0].text
            price = whole+fraction  
        try:
            float(price)
            print("Price: $" + price)
        except ValueError:
            print("Out of Stock.")
            return 
        return price
        
    def get_title(self, page):
        title = page.html.find('#productTitle')[0].text 
        return title

    def get_img(self, page):
        div = page.html.find('#imgTagWrapperId')[0]
        img = div.xpath('//img/@src')[0]
        return img