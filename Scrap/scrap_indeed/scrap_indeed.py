import time
import json
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from unidecode import unidecode
from decouple import config

# base_url= "http://0.0.0.0:9001"
base_url = str(config("base_url"))


def get_random_headers():
    ua = UserAgent()
    headers = {"User-Agent": ua.random, "Accept-Language": "en-US, en;q=0.5"}
    return headers


# for translation
prefs = {"translate_whitelists": {"ar": "en"}, "translate": {"enabled": "true"}}


def random_delay():
    time.sleep(random.uniform(1, 3))



def get_chromedrvier_options():
    headers = get_random_headers()
    print(headers)
    # Set Chrome options
    options = Options()
    options.headless = True
    options.add_argument("--enable-logging")
    options.add_argument("--log-level=0")
    # options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
    options.add_argument(f'user-agent={headers["User-Agent"]}')
    options.add_argument("--no-sandbox")
    return options



def save_in_db(data):
    my_retry= True
    while my_retry:
        try:
            print("\n\nSAVING \n")
            print(base_url)
            url = f"{base_url}/jobsScrap/post_job/"

            payload = json.dumps(data)
            headers = {"Content-Type": "application/json"}
            response = requests.request("POST", url, headers=headers, data=payload)
            response_text = json.loads(response.text)

            print("\n\n", response_text, "\n\n")

            if response_text["status"]:
                my_retry= False
                return True
            elif not response_text["status"]:
                my_retry= True
        except:
            time.sleep(20)
            print(f"\n\n ************ EXCEPTION IN SAVING DB **********\n\n\n")
            my_retry= True
    

def get_links(html):
    soup = BeautifulSoup(html, "html.parser")
    target_ul = soup.find("ul", class_="css-zu9cdh eu4oa1w0")
    all_li_tags = target_ul.find_all("li", class_="css-5lfssm eu4oa1w0") if target_ul else []
    base_url = "https://www.indeed.com/"
    linklist = []
    for litag in all_li_tags:
        a_tag = litag.find("a", href=True)
        if a_tag:
            href = a_tag["href"]
            if not href.startswith("https://www.indeed.com"):
                linklist.append(base_url + href)
    return linklist


def scrap_data(html):
    data = {
        "listing_platform": "Indeed",
        "job_title": "",
        "company_name": "",
        "company_location": "",
        "salary": "",
        "employment_type": "",
        "job_description": "",
        "links": "",
    }

    soup = BeautifulSoup(html, "html.parser")
    target_h1 = soup.find("h1", {"data-testid": "jobsearch-JobInfoHeader-title"})
    data["job_title"] = target_h1.getText(strip=True) if target_h1 else ""

    target_div = soup.find("div", {"data-testid": "inlineHeader-companyName"})
    data["company_name"] = target_div.get_text(strip=True) if target_div else ""

    location_div = soup.find("div", {"data-testid": "inlineHeader-companyLocation"})
    city = (
        location_div.find("div").get_text(strip=True)
        if location_div and location_div.find("div")
        else ""
    )
    data["company_location"] = unidecode(city)

    salary_jobtype_ele = soup.find("div", id="salaryInfoAndJobType")
    salary_span = (
        salary_jobtype_ele.find("span", class_="css-19j1a75")
        or salary_jobtype_ele.find("span", class_="css-2iqe2o")
        if salary_jobtype_ele
        else None
    )
    if salary_span:
        salary_text = salary_span.get_text(strip=True)
        data["salary"] = salary_text

    jobtype_ele = (
        salary_jobtype_ele.find("span", class_="css-k5flys")
        if salary_jobtype_ele
        else None
    )
    data["employment_type"] = jobtype_ele.get_text(strip=True) if jobtype_ele else ""

    job_desript_ele = soup.find("div", {"id": "jobDescriptionText"})
    data["job_description"] = str(job_desript_ele)

    return data


def sysInit(city_name, keyword):
    web_driver = None
    try:
        print("Starting........")
        # search_url = "https://indeed.com/jobs?q=&l="
        keyword= keyword.replace(' ', '+').replace(',', '%2C')
        search_url = f"https://indeed.com/jobs?q={keyword}&l="
        city = city_name
        city_name= city_name.replace(' ', '+').replace(',', '%2C')
        # url = f"{search_url}{city_name}&fromage=1"
        url = f"{search_url}{city_name}&radius=35"
        print(url)
        myretry= True
        while myretry:
            try:
                options = get_chromedrvier_options()
                web_driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
                web_driver.maximize_window()
                web_driver.get(url= url)
                time.sleep(5)

                all_links = []
                web_driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(2)
                web_driver.execute_script("window.scrollBy(0, 2500);")
                time.sleep(2)

                links = get_links(web_driver.page_source)
                all_links.extend(links)

                count = 1

                while count < 2:
                    try:
                        print(f"\n\n********** On {count} Paginated page *********** ")
                        new_url= f"{url}&start={count}0"
                        print(new_url)
                        web_driver.get(new_url)
                        time.sleep(2)
                        web_driver.execute_script("window.scrollBy(0, 1000);")
                        time.sleep(2)
                        html = web_driver.page_source
                        web_driver.execute_script("window.scrollBy(0, 2500);")
                        time.sleep(2)
                        html = web_driver.page_source
                        links = get_links(html)
                        print(f"links on {count} paginated pages are {len(links)} _____")
                        all_links.extend(links) if links is not None else None
                        random_delay()
                        count += 1

                    except TimeoutException:
                        time.sleep(20)
                        break
                myretry= False

            except:
                print(f"\n\n********** EXCEPTION IN MAIN **********")
                myretry= True
            finally:
                print("QUIT WEB DRIVER ______________")
                if web_driver:
                    web_driver.quit()

        print("\n\n", json.dumps(all_links), "\n\n")
        len_of_link = len(all_links)

        for index, link in enumerate(all_links):
            myretry= True
            while myretry:
                try:
                    time.sleep(2)
                    print(
                        f"\n\n****** link {index+1} start of {len_of_link} _______ \n  {link} \n\n"
                    )
                    options = get_chromedrvier_options()
                    web_driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
                    web_driver.maximize_window()
                    web_driver.get(link)
                    time.sleep(3)
                    html = web_driver.page_source
                    web_driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(2)
                    html = web_driver.page_source
                    web_driver.execute_script("window.scrollBy(0, 1000);")
                    time.sleep(2)
                    html = web_driver.page_source
                    web_driver.execute_script("window.scrollBy(0, 1);")
                    time.sleep(2)

                    html = web_driver.page_source
                    data = scrap_data(html)
                    if all(value == "" for value in data.values()):
                        print("\n\n********************")
                        print("\nCheck the link I think cloud-flare is come \n", link)
                        continue
                    data["links"] = link
                    data['city'] = city
                    print(json.dumps(data, indent=2))
                    time.sleep(5)
                    # call post api to save indeed job in DB
                    save_in_db(data)
                    myretry= False
                
                except:
                    print(f"\n\n********** EXCEPTION IN MAIN **********")
                    myretry= True
                finally:
                    print("QUIT WEB DRIVER ______________")
                    if web_driver:
                        web_driver.quit()
    except:
        # display.stop()
        if web_driver:
            web_driver.quit()

   


def run_scraping(city_name, keyword):
    sysInit(city_name, keyword)


# run_scraping("New York")
