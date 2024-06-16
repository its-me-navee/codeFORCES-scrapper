import logging
import azure.functions as func
import jinja2
import requests
import datetime
from datetime import date, timedelta
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pytz
import os

os.environ["DISPLAY"] = ":99"

app = func.FunctionApp()


def get_ist_time():
    # Get the current UTC time
    utc_now = datetime.datetime.utcnow()
    # Define the Indian Standard Time (IST) timezone
    ist_timezone = pytz.timezone("Asia/Kolkata")
    # Convert the UTC time to IST
    ist_now = utc_now.replace(tzinfo=pytz.utc).astimezone(ist_timezone)
    return ist_now


@app.function_name(name="mytimer")
@app.schedule(
    schedule="0 */10 * * * *",
    arg_name="mytimer",
    run_on_startup=True,
    timezone="Asia/Kolkata",
)
def timer_trigger_1729(mytimer: func.TimerRequest) -> None:
    logging.info("Python Timer trigger function started")
    ist_timestamp = get_ist_time().isoformat()
    if mytimer.past_due:
        logging.warning("The timer is past due!")
    logging.info("Python timer trigger function ran at %s", ist_timestamp)

    main()


def getDate(tame):
    cnv = {
        "Jan": "01",
        "Feb": "02",
        "Mar": "03",
        "Apr": "04",
        "May": "05",
        "Jun": "06",
        "Jul": "07",
        "Aug": "08",
        "Sep": "09",
        "Oct": "10",
        "Nov": "11",
        "Dec": "12",
    }
    cnt = 0
    mnth, year, day = "", "", ""
    for c in tame:
        if cnt == 3:
            break
        if c == "/" or c == " ":
            cnt += 1
            continue
        if cnt == 0:
            mnth += c
        if cnt == 1:
            day += c
        if cnt == 2:
            year += c
    mnth = cnv[mnth]
    return year + "-" + mnth + "-" + day


def getProblems(driver, handle):
    today = date.today()
    yesterday = today - timedelta(days=1)
    today = str(today)
    yesterday = str(yesterday)

    pages = driver.find_elements(By.CLASS_NAME, "page-index")

    total_pages = 1
    for page in pages:
        total_pages = int(page.text)

    submissionLink, submissionId = [], []
    problemLink, problemId = [], []
    URL = "https://codeforces.com/submissions/" + handle + "/page/"
    for num in range(total_pages + 1):
        end_of_loop = 0
        new_url = URL + str(num)
        driver.get(new_url)
        sleep(1)
        lst1 = driver.find_elements(By.CLASS_NAME, "status-small")
        lst2 = driver.find_elements(By.CLASS_NAME, "id-cell")

        itr, cls = 0, 0
        temp = []
        plink = ""
        for elem in lst1:
            if cls == 0:
                dt = getDate(elem.text)
                if dt == today or dt == yesterday:
                    temp.append(dt)
                else:
                    end_of_loop = 1
                    break
            elif cls == 1:
                ele = driver.find_elements(By.PARTIAL_LINK_TEXT, elem.text)
                plink = ele[0].get_attribute("href")
                temp.append(elem.text)
            elif cls == 2:
                temp.append(elem.text)
                if elem.text == "Accepted" and temp[0] == yesterday:
                    problemLink.append(plink)
                    submissionId.append(str(lst2[itr].text))
                    problemId.append(temp[1])
            cls += 1
            if cls == 3:
                temp.clear()
                itr += 1
                cls = 0
        for ids in submissionId:
            driver.get(new_url)
            solution = driver.find_elements(By.PARTIAL_LINK_TEXT, ids)
            solution[0].click()
            driver.implicitly_wait(10)
            directLink = driver.find_elements(
                By.XPATH, '//*[@id="facebox"]/div/div/div/span/a'
            )
            directLink = directLink[0].get_attribute("href")
            submissionLink.append(directLink)
        if end_of_loop == 1:
            break
    return submissionId, submissionLink, problemId, problemLink


def send_mailgun_message(api_key, domain, from_email, to_emails, subject, html_content):
    url = f"https://api.mailgun.net/v3/{domain}/messages"
    auth = ("api", api_key)
    data = {
        "from": from_email,
        "to": to_emails,
        "subject": subject,
        "html": html_content,
    }

    return requests.post(url, auth=auth, data=data)


def main():
    emailList = [
        "navee4501@gmail.com",
        "ashmia789@gmail.com",
        "navneets20@iitk.ac.in",
        "sameer20@iitk.ac.in",
    ]
    friendsList = [
        "PRO_fessor",
        "sultan__",
        "savita_bhabhi69",
        "Mayank_Pushpjeet",
        "satyam343",
    ]

    logging.basicConfig(
        filename="webdriver_log.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        print("WebDriver started successfully.")
    except Exception as e:
        print(f"Error starting WebDriver: {str(e)}")
        raise

    friends = friendsList

    finalList = [[]]
    finalList.clear()

    for friend in friends:
        profile = "https://codeforces.com/profile/" + friend
        driver.get(profile)
        sleep(1)

        submission = driver.find_elements(By.PARTIAL_LINK_TEXT, "SUBMISSIONS")
        submission[0].click()
        sleep(1)
        submissionId, submissionLink, problemId, problemLink = getProblems(
            driver, friend
        )
        for [elem1, elem2, elem3, elem4] in zip(
            submissionId, submissionLink, problemId, problemLink
        ):
            finalList.append([friend, profile, elem1, elem2, elem3, elem4])

    driver.quit()

    jinja_var = {"items": finalList}

    template_string = """
    <html>
        <head></head>
        <body>
            <table style="width: 100%; border: 1px solid #dddddd; border-collapse: collapse; border-spacing: 0;">
                <tr>
                    <th style="border: 1px solid #dddddd; padding: 5px; text-align: center;">Handle</th>
                    <th style="border: 1px solid #dddddd; padding: 5px; text-align: center;">Submission</th>
                    <th style="border: 1px solid #dddddd; padding: 5px; text-align: center;">Problem</th>
                </tr>
            {% for item in items %}
            <tr>
                <td style="border: 1px solid #dddddd; padding: 5px; text-align: center;" class="c1"><a href="{{ item[1] }}">{{ item[0] }}</a></td>
                <td style="border: 1px solid #dddddd; padding: 5px; text-align: center;" class="c2"><a href="{{ item[3] }}">{{ item[2] }}</a></td>
                <td style="border: 1px solid #dddddd; padding: 5px; text-align: center;" class="c3"><a href="{{ item[5] }}">{{ item[4] }}</a></td>
            </tr>
            {% endfor %}
            </table>
        </body>
    </html>
    """

    template = jinja2.Template(template_string)

    html = template.render(jinja_var)

    today = date.today()
    yesterday = today - timedelta(days=1)
    today = str(today)
    yesterday = str(yesterday)
    # Example usage
    api_key = "API_KEY"
    domain = "mailGunDomain"
    from_email = "mailGunEmail"
    to_emails = emailList
    subject = "Spies Report for " + str(yesterday)
    html_content = html

    response = send_mailgun_message(
        api_key, domain, from_email, to_emails, subject, html_content
    )

    # Check the response
    if response.status_code == 200:
        logging.info("Email sent successfully")
    else:
        logging.info("Email failed to send")


if __name__ == "__main__":
    main()
