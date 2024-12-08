from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import requests
import json
import sqlite3
import os

site_url = "https://chitai-gorod.ru"
api_url = "https://web-gate.chitai-gorod.ru"
api_path = "api/v2/products"
params = {
    'filters[onlyAvailableForSale]': 1,
    'filters[tags]': 13,
    'filters[onlyWithImage]': 1,
    'products[page]': 1,
    'products[per-page]': 342,
    'sortPreset': 'relevance',
    'include': 'productTexts,isbns,publisher,publisherBrand,publisherSeries,dates,literatureWorkCycle,rating,tags'
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0 (Edition Yx GX)',
    'Accept': 'application/json, text/plain, */*',
    'Authorization': 'Bearer',
    'Cookie': '' # add to make it work
}

res_folder = "data"

def main() -> None:
    if not os.path.exists(res_folder):
        os.makedirs(res_folder)
    
    cur_time = datetime.now().strftime("%Y.%m.%d-%H.%M.%S")
    
    conn = sqlite3.connect(os.path.join(res_folder, cur_time + ".db"))
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS book (
    id INTEGER PRIMARY KEY,
    title VARCHAR(128) NOT NULL,
    author VARCHAR(128),
    description TEXT,
    category VARCHAR(128),
    publisher VARCHAR(128),
    year_published INTEGER,
    isbn VARCHAR(32) NOT NULL
    );
    ''')

    resp = requests.get(urljoin(api_url, api_path), params=params, headers=headers)
    books_data = (resp.json())["data"]
    # print(json.dumps(books_data, indent=4, ensure_ascii=False))
    i = 0
    for book in books_data:
        # print(json.dumps(book, indent=4, ensure_ascii=False))
        
        title = book["attributes"]["title"]
        author_full_name = ""
        try:
            author_first_name = book["attributes"]["authors"][0]["firstName"]
            author_middle_name = book["attributes"]["authors"][0]["middleName"]
            author_last_name = book["attributes"]["authors"][0]["lastName"]
            author_full_name = " ".join([author_last_name, author_first_name, author_middle_name])
        except IndexError:  
            pass
        description = book["attributes"]["description"]
        category = book["attributes"]["category"]["title"]
        publisher = ""
        try:
            publisher = book["attributes"]["publisher"]["title"]
        except KeyError:
            pass
        year = book["attributes"]["yearPublishing"]
        
        book_url = urljoin(site_url, book["attributes"]["url"])
        book_page = requests.get(book_url)
        soup = BeautifulSoup(book_page.content, "lxml")
        isbn_el = soup.find(attrs={"itemprop": "isbn"})
        isbn = isbn_el.text.strip()
        
        cur.execute("INSERT INTO book (title, author, description, category, publisher, year_published, isbn) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (title, author_full_name, description, category, publisher, year, isbn))
        
        i += 1
        print(f"#{i}/342")
        
        # if i == 1:
        #     break
        
    print("FINISHED")
    
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
    
