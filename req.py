import requests
from bs4 import BeautifulSoup


def get_links():
    url = "https://news.google.com/home"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    links = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.startswith("./articles/"):
            article_url = "https://news.google.com" + href
            links.append(article_url)
    return article_url


