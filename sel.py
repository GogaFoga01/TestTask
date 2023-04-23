import random
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from sqlite3 import connect
from datetime import datetime
from req import get_links
import sqlite3
from datetime import datetime


def create_database():
    conn = sqlite3.connect('profilers.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS cookie_profiles
                 (id INTEGER PRIMARY KEY,
                  created_at TEXT NOT NULL,
                  profile TEXT,
                  last_launch TEXT,
                  num_launches INTEGER)''')

    for i in range(15):
        created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        c.execute(f"INSERT INTO cookie_profiles (created_at) VALUES ('{created_at}')")

    conn.commit()
    conn.close()


def create_session(profile_id=None):
    conn = connect('profilers.db')
    c = conn.cursor()
    if profile_id:
        c.execute("SELECT * FROM cookie_profiles WHERE id=?", (profile_id,))
        row = c.fetchone()
        if row:
            profile = webdriver.FirefoxProfile(row[2])
            driver = webdriver.Firefox(profile)
            driver.get('https://news.google.com/')
            return driver
    # Create new session
    driver = webdriver.Firefox()
    driver.get('https://news.google.com/')
    return driver


def follow_link(driver, urls):
    url = random.choice(urls)
    driver.get(url)
    time.sleep(random.randint(5, 15))


def scroll_page(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.randint(5, 15))


def save_cookies(driver, profile_id):
    profile = driver.profile
    cookies = profile.get_cookies()
    cookie_str = str(cookies)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = connect('profilers.db')
    c = conn.cursor()
    c.execute("UPDATE cookie_profiles SET profile=?, last_launch=?, num_launches=num_launches+1 WHERE id=?", (cookie_str, now, profile_id))
    conn.commit()


def close_session(driver):
    driver.quit()


def main():

    urls = get_links()

    conn = connect('profilers.db')
    c = conn.cursor()
    c.execute("SELECT id FROM cookie_profiles")
    profile_ids = [row[0] for row in c.fetchall()]

    from multiprocessing import Pool
    pool = Pool(processes=5)

    for profile_id in profile_ids:
        driver = create_session(profile_id)
        pool.apply_async(follow_link, args=(driver, urls))
        pool.apply_async(scroll_page, args=(driver,))
        pool.apply_async(save_cookies, args=(driver, profile_id))
        pool.apply_async(close_session, args=(driver,))

    pool.close()
    pool.join()


if __name__ == '__main__':
    main()
