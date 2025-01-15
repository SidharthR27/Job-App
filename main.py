import requests
import smtplib
from datetime import datetime
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import markdown
from email.utils import formataddr

from bs4 import BeautifulSoup

today = datetime.now()
print(today)
formatted_date = today.strftime("%Y-%m-%d")
new_jobs = False

header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"
          }

response1 = requests.get(url="https://technopark.org/api/paginated-jobs?page=1&search=&type=", headers=header)
response2 = requests.get(url="https://technopark.org/api/paginated-jobs?page=2&search=&type=", headers=header)
all_jobs = response1.json()["data"] + response2.json()["data"]

job_titles = []
job_urls = []
job_companies = []


markdown_message = f"# Here are all the jobs posted on Technopark Trivandrum Today ({today.strftime('%d-%m-%Y')}) 💁‍♀️: \n"
for job in all_jobs:
    if job["posted_date"] == formatted_date:
        new_jobs = True
        job_titles.append(job["job_title"])
        job_companies.append(job["company"]["company"].title())
        job_urls.append(f'https://technopark.org/job-details/{job["id"]}')
        markdown_message += f'-  **{job["job_title"]}** by {job["company"]["company"].title()} &nbsp;&nbsp;&nbsp; [Know More](https://technopark.org/job-details/{job["id"]})\n\n\n\n\n\n'



# AI Suggestions
markdown_message += "<div> <br><br><br> </div>"
markdown_message += f"# AI suggestions personalised for you 👾:\n\n"
job_descriptions = []

for job_url in job_urls:
    response = requests.get(url=job_url, headers=header)
    soup = BeautifulSoup(response.content, "html.parser")
    job_div = soup.select_one("#app > div.relative.min-h-screen.w-full.pt-20 > div > div.mb-10.flex.flex-col.bg-white.shadow-2xl")
    job_desc = job_div.getText()
    job_descriptions.append(job_desc)

# print(job_descriptions)

import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
import json

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_schema": content.Schema(
    type = content.Type.OBJECT,
    enum = [],
    required = ["response"],
    properties = {
      "response": content.Schema(
        type = content.Type.BOOLEAN,
      ),
    },
  ),
  "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash-8b",
  generation_config=generation_config,
  system_instruction="I hold a B.Tech from NIT Calicut and have strong skills in Python, Django, React, JavaScript, SQL, cybersecurity, and machine learning. I’ve worked on projects like medical ML models, Amazon price tracking, antimicrobial peptide prediction, and Django web applications with PostgreSQL. Evaluate the following job description against my skills and experience. Provide a response with only True or False. I don't have any professional experience so only recommend jobs that don't need any experience more than 1 year.",
)

chat_session = model.start_chat(
  history=[
  ]
)

ai_suggest = False

for i in  range(len(job_descriptions)):
    response = chat_session.send_message(job_descriptions[i])
    if bool(json.loads(response.text)["response"]):
        ai_suggest = True
        markdown_message += f'-  **{job_titles[i]}** by {job_companies[i]} &nbsp;&nbsp;&nbsp; [Know More]({job_urls[i]})\n\n\n\n\n\n'

if not ai_suggest:
    markdown_message += f'*There are no AI picked jobs for you today*'




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

if not new_jobs:
    print("No new jobs..")