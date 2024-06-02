"""
Linkdln scrapping

https://www.linkedin.com/jobs/search?keywords=&location=karachi%20division&f_TPR=r86400&distance=75&position=1&pageNum=0


https://www.linkedin.com/jobs/search?keywords=&location=   {CITY_NAME}   &f_TPR=r86400&distance=   {distance}  &position=1&pageNum=0

distance = 25 or 50 or 75 for miles

In city name
%20 for space (' ')
%2C for coma  (',')



API ENDPOINT
post_job
post_job
post_job
"""

import time, json, random, requests
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from unidecode import unidecode
from decouple import config


base_url = str(config("base_url"))
# base_url= "http://0.0.0.0:9001"


def get_random_headers():
    ua = UserAgent()
    headers = {"User-Agent": ua.random, "Accept-Language": "en-US, en;q=0.5"}
    return headers


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
    target_ul = soup.find("ul", class_="jobs-search__results-list")
    all_li_tags = target_ul.find_all("li") if target_ul else ""
    linklist = [
        litag.find("a", href=True)["href"]
        for litag in all_li_tags
        if litag.find("a", href=True)
    ]
    return linklist


def scrap_data(html):
    data = {
        "listing_platform": "LinkedIn",
        "links": "",
        "job_title": "",
        "company_name": "",
        "company_url": "",
        "company_location": "",
        "job_days": "",
        "applicants": "",
        "job_function": "",
        "employment_type": "",
        "seniority_level": "",
        "industries": "",
        "job_description": "",
    }

    soup = BeautifulSoup(html, "html.parser")
    target_h1 = soup.find("h1", {"class": "top-card-layout__title"})
    data["job_title"] = target_h1.getText(strip=True) if target_h1 else ""
    print("\n\nJob Title is : _____  ", data["job_title"])

    target_h4 = soup.find("h4", {"class": "top-card-layout__second-subline"})
    target_divs = (
        target_h4.find_all("div", {"class": "topcard__flavor-row"}) if target_h4 else []
    )
    for index, div in enumerate(target_divs, start=1):
        if index == 1:
            all_span = div.find_all("span", {"class": "topcard__flavor"})
            for index, span in enumerate(all_span, start=1):
                if index == 1:
                    company_url = span.find("a", href=True)
                    data["company_url"] = (
                        company_url["href"]
                        if company_url and company_url["href"]
                        else ""
                    )
                    data["company_name"] = (
                        company_url.getText(strip=True) if company_url else ""
                    )

                if index == 2:
                    city = span.getText(strip=True)
                    data["company_location"] = unidecode(city)

        if index == 2:
            span = div.find(
                "span", class_="posted-time-ago__text topcard__flavor--metadata"
            )
            data["job_days"] = span.getText(strip=True) if span else ""

            figure = div.find("figcaption", class_="num-applicants__caption")
            if figure:
                caption = figure.text.strip()
                data["applicants"] = caption
            else:
                span = div.find("span", class_="num-applicants__caption")
                caption = span.text.strip() if span else ""
                data["applicants"] = caption

    
    # for job description  description__text description__text--rich
    descrip_div= soup.find('div', {'class': 'description__text'})
    data["job_description"]= str(descrip_div.find('div', class_='show-more-less-html__markup')) if descrip_div else ""

    # for key value
    main_ul_tag = soup.find("ul", {"class": "description__job-criteria-list"})
    li_tags = main_ul_tag.find_all("li") if main_ul_tag else []

    for li in li_tags:
        h3_tag = li.find("h3", class_="description__job-criteria-subheader")
        span_tag = li.find("span", class_="description__job-criteria-text")
        key = h3_tag.getText(strip=True) if h3_tag else None
        value = span_tag.getText(strip=True) if span_tag else None

        if key == "Job function":
            data["job_function"] = value
        if key == "Employment type":
            data["employment_type"] = value
        if key == "Seniority level":
            data["seniority_level"] = value
        if key == "Industries":
            data["industries"] = value

    return data



# check results/jobs available or not at the city
def check_results(html, city_name, key_word):
    city_name= city_name.replace("%20", " ").replace("%2C", ",")
    key_word= key_word.replace("%20", " ").replace("%2C", ",")
    soup= BeautifulSoup(html, 'html.parser')
    main_h1= soup.find('h1', {'class':'core-section-container__main-title main-title'})
    if main_h1:
        main_h1_text= main_h1.text.strip()
        if main_h1_text.startswith("We couldn’t find"):
            print(f"\n\t****** We couldn't find any jobs in {city_name} with {key_word} search ..... ********\n\n")
            return False
    
    return True




def sysInit(city_name, key_word):

    # display = Display(visible=0, size=(800, 600))
    # display.start()
    try:

        myretry= True
        while myretry:
            try:
                print("Starting........")
                print("key_word-----------", key_word)
                options = get_chromedrvier_options()
                driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
                driver.maximize_window()
                my_city_name = city_name.replace(" ", "%20").replace(",", "%2C")
                # city_url = f"https://www.linkedin.com/jobs/search?keywords=&location={my_city_name}&f_TPR=r86400&distance=75&position=1&pageNum=0"
                key_word= key_word.replace(" ", "%20").replace(",", "%2C")
                # 1 day
                # city_url = f"https://www.linkedin.com/jobs/search?keywords={key_word}&location={my_city_name}&f_TPR=r86400&distance=75&position=1&pageNum=0"
                # 1 month 
                # city_url = f"https://www.linkedin.com/jobs/search?keywords={key_word}&location={my_city_name}&f_TPR=r2592000&distance=75&position=1&pageNum=0"
                # any time 
                city_url = f"https://www.linkedin.com/jobs/search?keywords={key_word}&location={my_city_name}&f_TPR=&distance=75&position=1&pageNum=0"
                driver.get(city_url)
                time.sleep(2)

                print(f"\n\n\t******  City {city_name} LinkedIn Jobs Scrapping Start . . .\n")
                print(f"\n\n\t******  City LinkdIn Jobs URL is . . .\n\n{city_url} \n\n")

                # check results available or not
                html = driver.page_source
                result = check_results(html, city_name, key_word)
                if not result:
                    return 
                
                is_links = False
                counter = 0
                while not is_links and counter < 10:
                    time.sleep(2)
                    html = driver.page_source
                    fetch_links = get_links(html)
                    if len(fetch_links) > 0:
                        is_links = True
                    
                    if not fetch_links:
                        driver.get(city_url)
                        counter += 1
                        # check results available or not
                        html = driver.page_source
                        result = check_results(html, city_name, key_word)
                        if not result:
                            return 
                        time.sleep(3)
                        print(
                            f"Please wait, linkedIn is rendering on the sigup page, {counter} try"
                        )
                        if counter >= 10:
                            print(
                                "Sorry LinkedIn is not allow for scrapping, Bot try 10 times .... Try again"
                            )

                time.sleep(7)

                # For infinite scroll
                # Define the initial scroll height
                last_height = driver.execute_script("return document.body.scrollHeight")
                counter = 0
                while True:
                    if counter == 50:
                        print("\n\n ********* Congrats 50 times Clicked ***********\n")
                        break
                    # Scroll down to the bottom of the page
                    driver.execute_script("window.scrollBy(0, 400);")
                    time.sleep(1)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    driver.execute_script("window.scrollBy(0, -500);")
                    time.sleep(1)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    driver.execute_script("window.scrollBy(0, -1000);")
                    time.sleep(1)

                    # Wait for some time to let the content load
                    time.sleep(3)
                    try:
                        btn = driver.find_element(
                            By.XPATH, "//button[contains(@aria-label, 'See more jobs')]"
                        )
                        btn.click()
                        print(f"\n {counter} CLICK ON => See more JOBS Button Successfully . . .\n")
                        counter += 1
                        time.sleep(2)
                    except:
                        print("See more Button Not found . . .")
                        time.sleep(2)
                        pass

                    # Calculate the new scroll height and compare with the last scroll height
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    # if new_height == last_height:
                        # If the scroll height hasn't changed, we have reached the bottom of the page
                        # break
                    # last_height = new_height
                    html= driver.page_source
                    soup= BeautifulSoup(html, 'html.parser')
                    main_div= soup.find('div', {'class': 'px-1.5 flex inline-notification text-color-signal-positive see-more-jobs__viewed-all'})
                    if main_div:
                        p_tag= soup.find('p', {'class':'inline-notification__text text-sm leading-regular'})
                        if p_tag:
                            text= p_tag.text.strip()
                            if text== "You've viewed all jobs for this search":
                                break
                html = driver.page_source
                links = get_links(html)
                len_of_links = len(links)
                myretry= False
                print(
                    f"\n\n\n\t****** Total __________ {len_of_links} _______ Jobs on LinkdIn were found On Today Filter ... city {city_name} \n\n\n"
                )
                
            
            except:
                print(f"\n\n********** EXCEPTION IN MAIN **********")
                myretry= True
            finally:
                print("QUIT WEB DRIVER ______________")
                if driver:
                    driver.quit()

        for index, link in enumerate(links, start=1):
            is_data = False
            counter = 1
            while not is_data and counter < 15:
                try: 
                    print(
                        f"\n\nJOb No.{index} of total {len_of_links} starts ______ \n\n {link}"
                    )
                    options = get_chromedrvier_options()
                    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
                    driver.get(link)
                    time.sleep(2)
                    driver.execute_script("window.scrollBy(0, 200);")
                    time.sleep(1)
                    driver.execute_script("window.scrollBy(0, 400);")
                    time.sleep(3)

                    html = driver.page_source
                    data = scrap_data(html)
                    if data["job_title"]:
                        data["links"] = link
                        data['city'] = city_name
                        print("\n\n", json.dumps(data, indent=2))
                        time.sleep(2)
                        # integrate POST api to save LinkedIn job in DB
                        save_in_db(data)
                        is_data = True
                    counter +=1
                except:
                    counter= 1
                    print(f"\n\n********** EXCEPTION IN link {index} ------- COUNTER IS : {counter} **********")
                    time.sleep(5)
                    is_data= False
                finally:
                    print("QUIT WEB DRIVER ______________")
                    if driver:
                        driver.quit()


        time.sleep(5)

    except Exception as e:
        print(e)


def ScrapLinkdin(city_name, key_word):
    sysInit(city_name, key_word)


# ScrapLinkdin("New York")
