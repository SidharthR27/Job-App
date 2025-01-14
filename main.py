import requests
import smtplib
from datetime import datetime,  timedelta
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import markdown
from email.utils import formataddr

today = datetime.now()
print(today)
yesterday = today - timedelta(days=1)
formatted_date = yesterday.strftime("%Y-%m-%d")
new_jobs = False

header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"
          }

response1 = requests.get(url="https://technopark.org/api/paginated-jobs?page=1&search=&type=", headers=header)
response2 = requests.get(url="https://technopark.org/api/paginated-jobs?page=2&search=&type=", headers=header)
all_jobs = response1.json()["data"] + response2.json()["data"]
url = "https://www.geeksforgeeks.org/python-datetime-timedelta-function/"

markdown_message = f"# Here are all the jobs posted on Technopark Trivandrum yesterday ({yesterday.strftime('%d-%m-%Y')}) 💁‍♀️: \n"
for job in all_jobs:
    if job["posted_date"] == formatted_date:
        new_jobs = True
        markdown_message += f'-  **{job["job_title"].title()}** by {job["company"]["company"].title()} &nbsp;&nbsp;&nbsp; [Know More](https://technopark.org/job-details/{job["id"]})\n\n\n\n\n\n'

html_content = markdown.markdown(markdown_message)

if new_jobs:
    my_email = "sidr272002@gmail.com"
    my_password = os.environ["my_password"]
    sender_name = "Sid's Assistant"

    # Create email
    message = MIMEMultipart("alternative")
    message["Subject"] = "Your Job Alert! 👨‍💻"
    message["From"] = formataddr((sender_name, my_email))
    message["To"] = "sidharthr333@gmail.com"

    # Attach parts
    message.attach(MIMEText(markdown_message, "plain"))  # Plain text fallback
    message.attach(MIMEText(html_content, "html"))       # HTML version

# Send email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(user=my_email, password=my_password)
            connection.sendmail(from_addr=my_email, to_addrs="sidharthr333@gmail.com", msg=message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

