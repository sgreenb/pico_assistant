from googlesearch import search
import requests
from bs4 import BeautifulSoup
import openai
from document_embedding import split_text_lists, create_embeddings, search_embeddings, retrieve_answer, query_agent

openai.api_key = open("openai_key.txt", "r").read().strip("\n")  # get api key from text file

def get_page_text(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return ' '.join([p.text for p in soup.find_all('p')])
        else:
            print(f"Failed to fetch page: {url}, status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching page: {url}, error: {e}")
        return None

def search_internet(query, num_results=2):
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

def get_urls(query, num_results=1):
    try:
        urls = []
        for url in search(query, num_results=num_results):
            urls.append(url)
        return urls
    except Exception as e:
        print(e)
        return None

   



#print(google_agent("What is the current price of one share of Apple stock?"))

def search_and_scrape(query):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        url = f"https://www.google.com/search?q={query}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            cleaned_text = ' '.join(text.split())
            return cleaned_text
        else:
            print(f"Failed to fetch search results for query: {query}, status code: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error fetching search results for query: {query}, error: {e}")
        return None


def fetch_google_search_results(query, num_results=10, language="en", user_agent=None):
    url = f"https://www.google.com/search?q={query}&num={num_results}&hl={language}"

    headers = {
        "User-Agent": user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch search results: {response.status_code}")
    
def parse_organic_results(html_content):
    soup = BeautifulSoup(html_content, "lxml")

    search_results = []

    for result in soup.select(".tF2Cxc"):
        title = result.select_one(".LC20lb.DKV0Md").text
        url = result.select_one(".yuRUbf a")["href"]
        snippet = result.select_one(".VwiC3b.MUxGbd").text if result.select_one(".VwiC3b.MUxGbd") else None

        search_results.append({
            "title": title,
            "url": url,
            "snippet": snippet
        })

    return search_results

def trim_text(text, start_string="results", length=1000):
    start_index = text.find(start_string)
    if start_index == -1:
        return "Error: Start string not found"
    start_index += len(start_string)
    return text[start_index:start_index + length]


def google_agent(prompt, cutoff=7):
    completion = openai.ChatCompletion.create(
    model = "gpt-4",
            temperature = 0,
            messages=[
                    {"role":"system", "content": "You analyze a user's input to a large language model with \
                     training data that cuts off at September 2021. The current year is 2023. You decide how \
                     likely it is that a user's request will benefit from a Google search to help address the\
                      question. Respond with a number in the range 1-10, where 1 is very unlikely that a \
                     Google search would be beneficial, and 10 meaning a Google search is highly necessary."},
                    {"role":"user", "content": prompt},
                    ] 
        )
    google_probability = int(completion.choices[0].message.content)
    if google_probability >= cutoff:
        search_results = trim_text(search_and_scrape(prompt))
        query_with_context = prompt + str(search_results)
        response = query_agent(query_with_context)
        return [{"role":"user", "content": query_with_context}, {"role":"assistant", "content": response}]
    else:
        return False



print(google_agent("What is the current price of one share of Apple stock?"))
