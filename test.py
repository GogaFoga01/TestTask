import requests
import sqlite3
import random
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import multiprocessing


# SQLite Module
def create_database():
    conn = sqlite3.connect('profiles.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS cookie_profile
                 (id INTEGER PRIMARY KEY,
                  created_at TEXT NOT NULL,
                  cookies TEXT,
                  last_launch TEXT,
                  total_launches INTEGER)''')

    for i in range(15):
        created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        c.execute(f"INSERT INTO cookie_profile (created_at) VALUES ('{created_at}')")

    conn.commit()
    conn.close()


def update_profile(profile_id, cookies):
    conn = sqlite3.connect('profiles.db')
    c = conn.cursor()

    last_launch = time.strftime('%Y-%m-%d %H:%M:%S')
    c.execute(f"UPDATE cookie_profile SET cookies = '{cookies}', last_launch = '{last_launch}', total_launches = total_launches + 1 WHERE id = {profile_id}")

    conn.commit()
    conn.close()


# Requests module
def get_news_links():
    url = "https://news.google.com/home"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    links = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.startswith("./articles/"):
            article_url = "https://news.google.com" + href[1:]
            links.append(article_url)

    return links


# Selenium module
def process_profile(profile):
    options = webdriver.ChromeOptions()
    if profile[2]:
        cookies = {c.split("=")[0]: c.split("=")[1] for c in profile[2].split("; ")}
        options.add_argument(f"user-data-dir=./chrome-data/{profile[0]}")
        options.add_argument("--profile-directory=Default")
        options.add_argument(f"--user-agent={random.choice(user_agents)}")
        for key, value in cookies.items():
            options.add_argument(f'--cookie="{key}"="{value}"')

    driver = webdriver.Chrome(options=options)

    try:
        links = get_news_links()
        if links:
            link = random.choice(links)
            driver.get(link)
            time.sleep(random.uniform(5.0, 10.0))
            cookies = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in driver.get_cookies()])
            update_profile(profile[0], cookies)
    except Exception as e:
        print(f"Error processing profile with id {profile[0]}: {str(e)}")
    finally:
        driver.quit()


# Main function
if __name__ == "__main__":
    create_database()

    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
    ]

    conn = sqlite3.connect('profiles.db')
    c = conn.cursor()

    # We collect profiles from the Cookie Profile table (number of streams)
    profiles = c.execute("SELECT * FROM cookie_profile").fetchall()

    # We use Pool to create streams for each profile (limit of 5 simultaneous streams)
    pool = multiprocessing.Pool(processes=5)
    results = [pool.apply_async(process_profile, args=(profile,)) for profile in profiles]

    # Wait for all processes to complete
    for result in results:
        result.wait()

    conn.close()
