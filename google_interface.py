from googlesearch import search
import requests
from bs4 import BeautifulSoup

def get_page_text(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return ' '.join([p.text for p in soup.find_all('p')])
        else:
            print(f"Failed to fetch page: {url}, status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching page: {url}, error: {e}")
        return None

def search_internet(query, num_results=1):
    try:
        search_results = []
        for url in search(query, num_results=num_results):
            page_text = get_page_text(url)
            if page_text:
                search_results.append({"url": url, "text": page_text})

        return search_results
    except Exception as e:
        print(e)
        return None
    
result = search_internet("Weather today")
print(result)