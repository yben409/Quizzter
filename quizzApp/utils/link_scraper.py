from quizzApp.utils.dependecies import *

def link_scraper(link):
    r = requests.get(link) #Gets all the informations of the website
    soup = BeautifulSoup(r.text,'html.parser') #Gets the HTML tree structure
    results = soup.find_all(['p'])
    text_ = [result.text for result in results]
    text = ' '.join(text_)
    return text