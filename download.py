import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

# URL to fetch HTML from
url = "https://the-eye.eu/public/Games/eXo/eXoDOS_v5/eXo/eXoDOS/?fbclid=IwAR2XrmI6O-iG9rUBuHIP7o5-lkZOtnWp3BOOWcHFlI33jvlLi7v0bZ5occA"

# Fetch HTML from URL
response = requests.get(url)

# Parse HTML using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find all <a> tags with href containing .zip
links = soup.find_all('a', href=re.compile('\.zip$'))

# Download each zip file
for link in links:
    href = link['href']
    filename = urllib.parse.unquote(href.split('/')[-1])
    download_url = url + '/' + href
    response = requests.get(download_url)
    with open(filename, 'wb') as f:
        f.write(response.content)
        print(f"Downloaded {filename}")
