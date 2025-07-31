

import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time


def setup_driver(li_at_cookie):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    driver.get("https://www.linkedin.com/")
    driver.add_cookie({"name": "li_at", "value": li_at_cookie, "domain": ".linkedin.com", "path": "/"})
    driver.get("https://www.linkedin.com/feed/")
    time.sleep(3)
    return driver


def scrape_certifications(driver):
    certifications = []

    try:
        
        driver.get(driver.current_url + "details/certifications/")
        time.sleep(4)

        cert_blocks = driver.find_elements(By.CSS_SELECTOR, 'li.pvs-list__paged-list-item')

        for item in cert_blocks:
            try:
                title = item.find_element(By.CSS_SELECTOR, 'span[aria-hidden="true"]').text.strip()
            except:
                title = ''
            try:
                issuer = item.find_elements(By.CSS_SELECTOR, 'span.t-14.t-normal')[0].text.strip()
            except:
                issuer = ''
            try:
                date = item.find_elements(By.CSS_SELECTOR, 'span.t-14.t-normal')[1].text.strip()
            except:
                date = ''
            try:
                url_elem = item.find_element(By.TAG_NAME, 'a')
                url = url_elem.get_attribute('href') if url_elem else ''
            except:
                url = ''

            certifications.append({
                "Title": title,
                "Issuer": issuer,
                "Issued Date": date,
                "Credential URL": url
            })

    except Exception as e:
        print("Certification scrape error:", e)

    return certifications


def scrape_profile(driver, url):
    driver.get(url)
    time.sleep(5)

    data = {
        "Profile Name": "",
        "Company Name": "",
        "Job Title": "",
        "Certifications": []
    }

    try:
        data["Profile Name"] = driver.find_element(By.TAG_NAME, "h1").text.strip()
    except:
        pass

    try:
        data["Job Title"] = driver.find_element(By.CLASS_NAME, "text-body-medium.break-words").text.strip()
    except:
        pass

    try:
        company_elem = driver.find_elements(By.CSS_SELECTOR, "div.text-body-small")[1]
        data["Company Name"] = company_elem.text.strip()
    except:
        pass

    data["Certifications"] = scrape_certifications(driver)
    return data


st.title("🔍 LinkedIn Profile Scraper with Certifications")

li_at_cookie = st.text_input("Enter LinkedIn `li_at` session cookie", type="password")
profile_url = st.text_input("Paste LinkedIn Profile URL")

if st.button("Scrape Profile"):
    if not li_at_cookie or not profile_url:
        st.warning("Please enter both cookie and profile URL.")
    else:
        with st.spinner("Scraping..."):
            driver = setup_driver(li_at_cookie)
            profile = scrape_profile(driver, profile_url)
            driver.quit()

            st.subheader("👤 Profile Overview")
            st.write(f"**Name:** {profile['Profile Name']}")
            st.write(f"**Job Title:** {profile['Job Title']}")
            st.write(f"**Company:** {profile['Company Name']}")

            st.subheader("🏅 Certifications")
            if profile["Certifications"]:
                cert_df = pd.DataFrame(profile["Certifications"])
                st.dataframe(cert_df)
                csv = cert_df.to_csv(index=False).encode("utf-8")
                st.download_button("Download CSV", csv, "certifications.csv", "text/csv")
            else:
                st.info("No certifications found.")




