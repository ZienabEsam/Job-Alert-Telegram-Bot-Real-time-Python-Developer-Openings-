from seleniumbase import SB
import time
import telebot

# Using Indeed.com as the job board
JOB_URL = "https://www.indeed.com/jobs"
SEARCH_KEYWORD = "Python Developer"
TELEGRAM_BOT_TOKEN = "telegram token for your channed/ account i removed mine"
TELEGRAM_CHAT_ID = "@ZD_esam"

extracted_job_postings = []
sent_job_urls = set()

def initialize_web_browser():
    return SB(uc=True, disable_csp=True, headless=True)

def perform_job_search(browser_instance, keyword):
    print(f"Navigating to {JOB_URL} and searching for '{keyword}'...")
    browser_instance.open(JOB_URL)
    # Wait for the search input field for keywords 
    browser_instance.wait_for_element("input#text-input-what", timeout=10)
    browser_instance.type("input#text-input-what", keyword)
    

 

    browser_instance.click("button[type='submit']", timeout=5) 
    # delay to wait for search
    browser_instance.sleep(5) 
    print("Job search initiated.")

def extract_job_listings(browser_instance):
    print("Extracting job listings...")
    current_page_listings = []
    try:
        job_elements = browser_instance.find_elements("div.jobsearch-SerpJobCard")
        print(f"Found {len(job_elements)} job elements on the page.")

        for job_element in job_elements:
            try:
                # Job title
                job_title_element = job_element.find_element("h2.jobsearch-SerpJobCard-title a")
                job_title = job_title_element.text
                job_url = job_title_element.get_attribute("href") 
                
                # Company name 
                company_name = job_element.find_element("span.company").text
                
                # Location 
                job_location = job_element.find_element("div.location").text
                
                # Job summary 
                job_snippet = job_element.find_element("div.summary ul li").text 

                current_page_listings.append({
                    "title": job_title,
                    "company": company_name,
                    "location": job_location,
                    "url": job_url,
                    "snippet": job_snippet
                })
            except Exception as e:
                print(f"Could not extract all details for a job element. Skipping. Error: {e}")
                continue
    except Exception as e:
        print(f"No job listing cards found or error during extraction: {e}")

    global extracted_job_postings
    for job in current_page_listings:
        if job["url"] not in sent_job_urls:
            extracted_job_postings.append(job)
            sent_job_urls.add(job["url"])

def send_telegram_job_alerts():
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
    alert_message = f"New '{SEARCH_KEYWORD}' Job Alerts!\n\n"
    new_alerts_count = 0

    global extracted_job_postings

    if not extracted_job_postings:
        print("No new job postings to send.")
        return

    for job in list(extracted_job_postings):
        alert_message += (
            f"{job['title']}\n"
            f"Company: {job['company']}\n"
            f"Location: {job['location']}\n"
            f"Link: {job['url']}\n\n"
        )
        new_alerts_count += 1
        if new_alerts_count % 5 == 0:
            try:
                bot.send_message(TELEGRAM_CHAT_ID, alert_message, parse_mode="Markdown")
                print(f"Sent {new_alerts_count} job alerts to Telegram.")
                alert_message = f"New '{SEARCH_KEYWORD}' Job Alerts! (Continued)\n\n"
            except Exception as e:
                print(f"Failed to send Telegram message: {e}")
                break

    if new_alerts_count > 0 and alert_message != f"New '{SEARCH_KEYWORD}' Job Alerts! (Continued)\n\n":
        try:
            bot.send_message(TELEGRAM_CHAT_ID, alert_message, parse_mode="Markdown")
            print(f"Sent remaining {new_alerts_count} job alerts to Telegram.")
        except Exception as e:
            print(f"Failed to send final Telegram message: {e}")

    extracted_job_postings.clear()

# --- Main ---
if __name__ == "__main__":
    with initialize_web_browser() as browser_instance:
        while True:
            try:
                perform_job_search(browser_instance, SEARCH_KEYWORD)
                extract_job_listings(browser_instance)
                send_telegram_job_alerts()

                print(f"Cycle complete. Waiting 5 minutes for next check.")
                time.sleep(300)
            except Exception as main_loop_error:
                print(f"An error occurred in the main loop: {main_loop_error}")
                print("Retrying in 1 minute.")
                time.sleep(60)
