from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup as bs
import time
import pandas as pd

o = {}
k = []

# Credentials
username = "username"
password = "password"

service = Service('path/to/chromedriver.exe')

browser = webdriver.Chrome(service=service)

# login
browser.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')

elementID = browser.find_element(By.ID, "username")
elementID.send_keys(username)

elementID = browser.find_element(By.ID, "password")
elementID.send_keys(password)

elementID.submit()

time.sleep(1)

search_terms=[
    "Fairness",
    "Bias",
    "Ethics",
    "Responsible",
    "Fair",
    "AI Integrity",
    "Morality"
]

search_query = "%20AND%20".join(search_terms)

posts = []

# searching itens
for item in search_terms:
    browser.get(f'https://www.linkedin.com/search/results/content/?keywords={item}%20AND%20Software&origin=CLUSTER_EXPANSION')

    print(f'https://www.linkedin.com/search/results/content/?keywords={item}%20AND%20Software&origin=CLUSTER_EXPANSION')
    time.sleep(1)
    count = 0
    soup = bs(browser.page_source, 'html.parser')

    # scrolling
    while True:
        height = browser.execute_script("return document.body.scrollHeight")
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)  
        count += len(soup.find_all('div', class_='feed-shared-update-v2'))
        print(count)
        if count > 220:
            break
        try:
            show_more_button = WebDriverWait(browser, 3).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "artdeco-button"))
            )
            show_more_button.click()
            time.sleep(1)
        except:
            pass
        
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == height:
            break
    
    # Extract post details
    print(len(soup.find_all('div', class_='feed-shared-update-v2')))

    for post in soup.find_all('div', class_='feed-shared-update-v2'):  
        include_post = True
        try:
            o["Text"] = post.find('div', class_='feed-shared-update-v2__description-wrapper').get_text(strip=True) 
        except:
            o["Text"] = None
        try:
            o["author"] = post.find('span', class_='update-components-actor__name').get_text(strip=True)
        except:
            o["author"] = None

        try:
            posted_date_str = post.find('span', class_='update-components-actor__sub-description').get_text(strip=True).split()[0]
            print(posted_date_str)
            if "mo" in posted_date_str:
                months = int(posted_date_str.split()[0])
                if months > 6:
                    include_post = False
            elif "yr" in posted_date_str:
                include_post = False

            o["posted_date"] = posted_date_str
        except:
            o["posted_date"] = None

        if include_post and any(value is not None for value in o.values()):
            try:
                o["Search item"] = item
            except:
                o["Search item"] = None

            k.append(o)

        o = {}

df = pd.DataFrame(k)
print(k)

# saving data
df.to_csv('LinkedinPosts.csv', index=False, encoding='utf-8')

browser.quit()