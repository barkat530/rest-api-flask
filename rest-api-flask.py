import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import datetime
import base64
import time
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import random
from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
import gspread
import gspread_dataframe as gd

# options = webdriver.ChromeOptions()
# options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
# options.add_argument("--headless")
# options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--no-sandbox")
# # driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)
# driver = webdriver.Chrome(service=Service(os.environ.get("CHROMEDRIVER_PATH")), options=options)

options = uc.ChromeOptions()
options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
# driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)
driver = uc.Chrome(service=Service(os.environ.get("CHROMEDRIVER_PATH")), options=options)

url = 'https://www.amazon.de/dp/B09HKXTNH5/ref=syn_sd_onsite_desktop_15?ie=UTF8&pd_rd_plhdr=t&th=1&psc=1'
# driver.get(url)
# time.sleep(5)

baseurl = re.search(r'http.*?\/\/.*?[^\/]+', url, flags=re.IGNORECASE).group(0)
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'}

try:
    asin1 = re.search(r'/[dg]p/([^/]+)', url, flags=re.IGNORECASE).group(1)
    allrev = baseurl + '/product-reviews/' + asin1 + '/?reviewerType=all_reviews'

    driver.get(allrev)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    
    revnumall = soup.find('div', {'data-hook' : 'total-review-count'}).text.strip()
    revnum = re.search(r'(\d+)', revnumall).group(1).replace(',', '')
    count = int(int(revnum)/10) + 2
    if count > 501:
        count = 501
    else:
        count = count

except:
    count = 2

total_list = []

for i in range(1, count):
    
    try:
        revpage = allrev + '&pageNumber=' + f'{i}'

        driver.get(revpage)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'lxml')

        rev = soup.find_all('div', {'data-hook' : 'review'})

        for review in rev:
            
            #Name
            try:
                var1 = review.find('span', {'class' : 'a-profile-name'}).text.strip().replace('\n', '')
            except:
                var1 = ''

            #Title
            try:
                var2 = review.find(class_ = 'review-title').find('span').text.strip().replace('\n', '')
            except:
                var2 = ''

            #Rating
            try:
                rte = review.find('span', class_ = 'a-icon-alt').text.strip()
                var3 = re.search(r'\d[^\s]+', rte).group(0)
            except:
                var3 = ''

            #Date
            try:
                dte = review.find('span', {'data-hook' : 'review-date'}).text.strip().replace('\n', '')
                # var4 = re.search(r'\s(\d+.*)', dte).group(1)
                var4 = re.search(r'(([A-Z][^\s]+\s)?\d+.*)', dte).group(1)
            except:
                var4 = ''

            #Text
            try:
                var5 = review.find('span', {'data-hook' : 'review-body'}).text.strip()
            except:
                var5 = ''

            #Review Page
            var6 = revpage


            total = {
            'Name': var1,
            'Title': var2,
            'Rating': var3,
            'Date': var4,
            'Text': var5,
            'Review Page': var6,

            }
            total_list.append(total)

        print(revpage)

    except:
        pass

df = pd.DataFrame(total_list)
df.to_csv('0.amazon-reviews.csv', index=False, encoding='utf-8-sig')


sheeturl = 'https://docs.google.com/spreadsheets/d/1IAPJK6eWsEx4C5JW6irn8yi_AVFgs8L1fbGjzfKEiUw/edit#gid=0'
credentials = {
  "type": "service_account",
  "project_id": "dev-airlock-333102",
  "private_key_id": "2180a5cd683ba7cedc0f9801849e988b13925286",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCqazFtaY9AGBKT\n3cm1/MSrZu3cxfDReAP9qm8VjdoVRHSLdxiYBXKGnoP4Y+9Qgtp+AS3j5NBNE0Ux\nUF/fwqXfFX7N8qoERs2kM2H5LA0RwqMoWAjvelBwsTcswcqNXEoaiX7kkER3OVd/\n4Fb8d2QemQP35/T7kSLo5hTeyQJJwa0HKcA6spmwU1qZJXTuOvyohHKsISQ1KRlO\n0zeIwsl+dPtfPJZBYkKSNuF9InwJweIgua+bFZJGpgzYG2zr+8mzfSkUSODjeY4C\nrshdTQLjvFIo8dL1A4yhIiFu/g5Iy5D7LF+66qkY4wOgjT3ZU6H0EZAZNzCmz8tV\nyv0wxSKXAgMBAAECggEAE9ncrhQHvb2QHG1PW8WP2y9oMblU7fF+9YNu4SHe729D\n7CL5WGv6BThdwwdRDx3O+bKFd/BlWzUNcEsef+AaljvYw4Cq0Ui2F5Rsqyu4cgMs\nIjzu/YZP7HCYLrx8La88ao7tmw47C3BAgwLM3yfBH9dPIQeB//PODzcN402i2Jhn\nwFhO8IADJLZ4yw0x7r/eJG4T/T86JxKarty4BhSfr+8IuH6MjCJsA2iQjpSyTthi\nP3LgsdfdfEZNXjAko7P9+T1fNGDwJ8oh8gpiaV+dRukZxe3s4XboaikOoa8+J5Wa\n+bEYgPSPUt5td4vQ7l7XccvMa950VKyiSEwgNzvUAQKBgQDv6k6IpERBApk8FUu5\n9IC6FsTaE2ynDKF34dALcBcLvOgCnjuWNei0ljR3oUctE1JcXbdiz2Q+u+MqzKHC\nF79FfeSCJT8vosgh+OcicBcia8thVYAaQpmxKhlBeJCoo8PViiez3/54z1/Mesco\n/Q5j+zBzlmmRhZK+QBiv0oGhlwKBgQC12Bv2TZAYABmS9jPWV1yaSOefMRxUtL6R\nWOl0kgr8ckBsuyBabhmTJ4R1010wqcDW/LeUvGHfcSX0eOFTx4oO7roas76f/eIf\nX4yc4WfSKlSU1zXNX9wC/98y5rzPuBXukjb3Ti1v0fAfilVS00p6yCVhMzsSDBRg\nJrfaCDanAQKBgQCY3MSvIWLvvRUfiD4YvKXsa6d/f5LiGRUkijeBoii87N8zE9jJ\ni426yl2hv5vXJ5F5kqjPB29K3XIPihSi03imcWFQXyUUV/aGVs4GTj8fSmlqmgym\nLrs4e6dd5NDe8oFLpNxJKrY8CX1zjuMoxZwOrjSf4T1gYCgwmixgkpLP/wKBgQCi\n3YjFw9g/tq8xEfOBkMMuqAdTa//s2ekoctK9BiRyz71l5P9oHt4nDyizAvifIhrG\nMpgVzdd28XdGC5H8oGXFVAk46y3bS99frAtbYwLCmAkjOdFFPQrnYNY+V6xZ+o0i\nHLDANLO7R/NhvFsJEJbPez0HXoQUeN8y8tqNm/efAQKBgBe7e8NkK7yssfXmWpOU\n55O6odWwJD1HFElwEZob5Et23UykZzXIM5gTZcO/+Bn0DCHHg+n5pDaiY0A4Fsw0\n/B+ckViQSSq7feZkITB50+bL2uGwXVCjjfoPt+pTVKeTbydxtgPTEncc8rbXNnoI\nGxwYs5DzIC2s7ebybJ7MY+ED\n-----END PRIVATE KEY-----\n",
  "client_email": "fulker@dev-airlock-333102.iam.gserviceaccount.com",
  "client_id": "116643256588791743728",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/fulker%40dev-airlock-333102.iam.gserviceaccount.com"
}

def togsheet(indx):
    gc = gspread.service_account_from_dict(credentials)
    sht1 = gc.open_by_url(sheeturl).get_worksheet(indx)
    sht1.clear()
    df = pd.DataFrame(total_list)
    gd.set_with_dataframe(sht1, df)

togsheet(0)