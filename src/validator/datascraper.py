#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import sqlite3
import json
from html import unescape
import re


def find_jobs(url: str, con: sqlite3.connect, cur: sqlite3.connect().cursor):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        job_urls = soup.find_all('a',
                                 {"class": "card-alias-after-overlay hover-underline link-visited-color text-break"})
        for job_url in job_urls:
            link = "https://www.builtin.com" + job_url.get('href')
            linkResponse = requests.get(link)
            linkResponse.raise_for_status()
            linkSoup = BeautifulSoup(linkResponse.content, 'html.parser')
            job_title = linkSoup.title.string.strip()

            script_tag = linkSoup.find('script', type='application/ld+json')
            if script_tag:
                try:
                    json_content = json.loads(script_tag.string)
                    job_description = json_content.get("@graph", [{}])[0].get("description", "")
                    description = unescape(job_description)
                    description_text = BeautifulSoup(description, 'html.parser').get_text(separator=' ')
                    description_clean = re.sub(r'\s+', ' ', description_text).strip()

                    # Insert job data into the database
                    cur.execute("INSERT INTO jobs (job, description) VALUES (?, ?)", (job_title, description_clean))
                    con.commit()
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
            else:
                print("No JSON script tag found")
    except requests.RequestException as e:
        print(f"Request failed: {e}")


if __name__ == "__main__":
    with sqlite3.connect("jobs.db") as con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS jobs(job TEXT, description TEXT)")
        for i in range(31, 1034):
            url = f"https://www.builtin.com/jobs?page={i}"
            find_jobs(url, con, cur)
        print("Successfully created database of jobs")
