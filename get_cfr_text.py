import requests
from bs4 import BeautifulSoup
from datetime import datetime
from os import makedirs

makedirs('data/text', exist_ok=True)

volume_url = 'https://www.gpo.gov/fdsys/pkg/CFR-{0}-title{1}-vol{2}/html/CFR-{0}-title{1}-vol{2}.htm'

title = 11

title_text = ''
this_year = datetime.now().year
volume = 1

while True:
    year = this_year
    url = volume_url.format(year, title, volume)
    r = requests.get(url)
    if r.status_code is not 200:
        year = this_year - 1
        url = volume_url.format(year, title, volume)
        r = requests.get(url)
        if r.status_code is not 200:
            break
    print(url)
    title_text += BeautifulSoup(r.text, 'html.parser').get_text()
    volume += 1
    f = open('data/text/CFR-{0}-title{1}.txt'.format(year, title), 'w')
    f.write(title_text)
    f.close()
