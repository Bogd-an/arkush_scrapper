import requests
from bs4 import BeautifulSoup
import re
from FB2 import FictionBook2, Author
from urllib import request


while True:
    global title, soup, arkush
    arkush = 'https://arkush.net'
    URL = input(f'Введіть посилання на книгу з {arkush} : ')
    
    try:
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        title = soup.select('h1.name')[0].text.strip()
    except:
        print('Помилка')
        continue
    print(f'Це правильна назва "{title}"?')
    right = input('y/f або так/ні або +/-: ')
    if right in 'y так +':
        break
    print('Помилка')

book = FictionBook2()

book.titleInfo.lang = "uk"
book.titleInfo.title = title
book.titleInfo.annotation = soup.select('div.annotation')[0].text.strip()

nicname = soup.select('span.name')[0].text.strip()
if nicname[-5:] == 'автор': nicname = nicname[:-5]

genres = re.findall('.[^А-Я]*', 
                    [genres.text.strip() for genres in soup.select('div.genres')][0])

tags = [genres.text.strip() for genres in soup.select('div.tags')][0].split('#')[1:]


book.titleInfo.authors = [Author(   nickname=nicname,
                                    homePages=['https://arkush.net'+soup.select('a.author')[0]['href']])]
book.titleInfo.genres = genres + tags
book.titleInfo.coverPageImages = [
    request.urlopen('https://arkush.net'+soup.select('div.cover-wrapper')[0].select('img')[0]['src']).read()]
book.titleInfo.sequences = [("Example books", 2)]
book.documentInfo.authors = [nicname]
book.documentInfo.version = "1.1"

parts = [(part.select('a')[0].text.strip(), part.select('a')[0]['href']) for part in soup.select('div.part')]

for name, url in parts:
    page = requests.get(arkush+url)
    soup = BeautifulSoup(page.content, "html.parser")
    conteiner = soup.select('div.book-read')[0]
    title_part = conteiner.select('h2')[0].text.strip()
    print(f'Завантажено {title_part}')       
    book.chapters.append((title_part, 
        [ p.text.strip() for p in conteiner.select('div.book-content')[0].select('p') ]
    ))


book.write(f"{title} ({nicname}).fb2")
