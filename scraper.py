from requests_html import AsyncHTMLSession

async def scrape(type, asin):
    asession = AsyncHTMLSession() 
    page = await asession.get(f'https://www.amazon.ca/gp/product/{asin}')
    await page.html.arender(timeout = 20)  
    if type == 'price':
        try:
            price = page.html.find('.a-offscreen')[0].text.replace('$','').strip()
        except IndexError:
            whole = page.html.find('.a-price-whole')[0].text
            fraction = page.html.find('.a-price-fraction')[0].text
            price = whole+fraction
        await asession.close() 
        print(price)
        return price
    elif type == 'details':
        title = page.html.find('#productTitle')[0].text 
        div = page.html.find('#imgTagWrapperId')[0]
        img = div.xpath('//img/@src')[0]
        await asession.close() 
        return title, img