import requests
from lxml import html
import csv

def scrape_page(url):
    response = requests.get(url)
    tree = html.fromstring(response.content)
    verse_number = tree.xpath('//*[@id="pageContent"]/div/section[2]/div/h1/text()')[0].strip()
    sanskrit_text_elements = tree.xpath('//*[@id="scontent"]/div/p/text()')[0:2]
    sanskrit_text = ''.join(sanskrit_text_elements)
    english_text = tree.xpath('//*[@id="pageContent"]/div/div[2]/blockquote/p[2]/text()')[0].strip()

    return verse_number, sanskrit_text, english_text
base_url = 'https://www.wisdomlib.org/hinduism/book/mahabharata-sanskrit/d/doc'
initial_page = 965160
data = []
for i in range(100):
    current_url = f"{base_url}{initial_page + i}.html"
    extracted_data = scrape_page(current_url)
    data.append(extracted_data)
with open('verses.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Verse Number', 'Sanskrit Text', 'English Translation'])
    writer.writerows(data)

print("Data scraping completed and saved to verses.csv.")
