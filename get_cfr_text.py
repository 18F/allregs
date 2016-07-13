import requests
from bs4 import BeautifulSoup
from datetime import datetime
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

s = requests.Session()

retries = Retry(total=3,
                backoff_factor=0.1,
                status_forcelist=[500, 502, 503, 504])
s.mount('http://', HTTPAdapter(max_retries=retries))


volume_url = 'https://www.gpo.gov/fdsys/pkg/CFR-{0}-title{1}-vol{2}/html/CFR-{0}-title{1}-vol{2}.htm'
this_year = datetime.now().year

for title in range(1, 51):
    title_text = ''
    volume = 1
    while True:
        year = this_year
        url = volume_url.format(year, title, volume)
        r = s.get(url)
        if r.status_code is not 200:
            year = this_year - 1
            url = volume_url.format(year, title, volume)
            r = s.get(url)
            if r.status_code is not 200:
                print('failed: %s' % url)
                break
        print('success: %s' % url)
        title_text += BeautifulSoup(r.text, 'html.parser').get_text()
        volume += 1
        f = open('data/text/CFR-{0}-title{1}.txt'.format(year, title), 'w')
        f.write(title_text)
        f.close()
