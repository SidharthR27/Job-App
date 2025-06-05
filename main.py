import requests
import smtplib
from datetime import datetime
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import markdown
from email.utils import formataddr
import time
from bs4 import BeautifulSoup
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
import json

today = datetime.now()
# print(today)
formatted_date = today.strftime("%Y-%m-%d")
new_jobs = False


# get latest jobs from Technopark api
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"}

page1_jobs = requests.get(url="https://technopark.org/api/paginated-jobs?page=1&search=&type=", headers=header)
page2_jobs = requests.get(url="https://technopark.org/api/paginated-jobs?page=2&search=&type=", headers=header)
all_jobs = page1_jobs.json()["data"] + page2_jobs.json()["data"]

job_titles = []
job_urls = []
job_companies = []

# add the job details to array and also add the markdown message for the mail
markdown_message = f"# Here are all the jobs posted on Technopark Trivandrum Today ({today.strftime('%d-%m-%Y')}) 💁‍♀️: \n"
for job in all_jobs:
    if job["posted_date"] == formatted_date:
        new_jobs = True
        job_titles.append(job["job_title"])
        job_companies.append(job["company"]["company"].title())
        job_urls.append(f'https://technopark.org/job-details/{job["id"]}')
        markdown_message += f'-  **{job["job_title"]}** by {job["company"]["company"].title()} &nbsp;&nbsp;&nbsp; [Know More](https://technopark.org/job-details/{job["id"]})\n\n\n\n\n\n'



# AI Suggestions
markdown_message += "<div> <br><br> </div>"
markdown_message += f"# AI suggestions personalised for you :\n\n"
job_descriptions = []

# get job details from each urls and scraping to find the necessary details to feed to AI
for job_url in job_urls:
    response = requests.get(url=job_url, headers=header)
    soup = BeautifulSoup(response.content, "html.parser")
    job_div = soup.select_one("#app > div.relative.min-h-screen.w-full.pt-20 > div > div.mb-10.flex.flex-col.bg-white.shadow-2xl")
    job_desc = job_div.getText()
    relevant_parts = " ".join(job_desc.split()[:400]) 
    job_descriptions.append(relevant_parts)

# print(job_descriptions)


genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create the model

ai_suggest = False

# going through all the job descriptions and getting AI response for each.
for i in  range(len(job_descriptions)):
        
    generation_config = {
  "temperature": .2,
  "top_p": 0.2,
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
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
    system_instruction="I hold a B.Tech from NIT Calicut and have strong skills in Python, Django, React, JavaScript, SQL, cybersecurity, and machine learning. I’ve worked on projects like medical ML models, Amazon price tracking, antimicrobial peptide prediction, and Django web applications with PostgreSQL. Evaluate the following job description against my skills and experience. Provide a response with only True or False. I don't have any professional experience so only recommend jobs that don't need any experience. Only match jobs that strictly need python",
    )
    chat_session = model.start_chat(
    history=[
    ]
    )


    response = chat_session.send_message(job_descriptions[i])
    # print(json.loads(response.text)["response"])
    if bool(json.loads(response.text)["response"]):
        ai_suggest = True
        markdown_message += f'-  **{job_titles[i]}** by {job_companies[i]} &nbsp;&nbsp;&nbsp; [Know More]({job_urls[i]})\n\n\n\n\n\n'
    time.sleep(10)

if not ai_suggest:
    markdown_message += f'*There are no AI picked jobs for you today*'


# convert the markdown message to HTML
html_content = markdown.markdown(markdown_message)

# send mails if there are new jobs today
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
        print(f"An error occurred when sending mail: {e}")

else:
    print("No new jobs today, exiting...")
