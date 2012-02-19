from BeautifulSoup import BeautifulSoup
from scrapemark import scrape

def parse(spider, resp):
    html = BeautifulSoup(resp.body).prettify()

    res = scrape(
    """{* 
        <tr>
            <td>
                <a>{{ [sen].nombre }}</a>
                {* <strong>({{ [sen].ref }})</strong> *}
            </td>
            <td>
                <font>partido {{ [sen].partido }}</font>
            </td>
        </tr>
    *}""",
    html=html)
    
    print res
