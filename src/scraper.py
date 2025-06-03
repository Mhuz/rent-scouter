from urllib.parse import urlparse, urlencode, urlunparse
import requests
import argparse
from bs4 import BeautifulSoup
import json
import argparse
from parsers import subito

SOURCES_FILE_PATH = 'sources.json'

def load_sources():
    try:
        with open(SOURCES_FILE_PATH) as sources_file:
            sources = json.load(sources_file)
        return sources
    except FileNotFoundError:
        print(f"File {SOURCES_FILE_PATH} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Could not parse file '{SOURCES_FILE_PATH}'.")
        return None

SOURCES_PARAMS = load_sources()

def start_search(realestateportal, url, minprice, maxprice):
    if not SOURCES_PARAMS:
        print("Sources params aren't loaded")
        return

    config = SOURCES_PARAMS[realestateportal]
    params_map = config['params']
    headers = {
        "Accept": '"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"',
        "Accept-Encoding": '"gzip, deflate"',
        "Accept-Language": '"en-US,en;q=0.5"',
        "Connection": '"keep-alive"',
        "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Brave";v="128"',
        "Sec-Ch-Ua-Mobile": '"?0"',
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": '"document"',
        "Sec-Fetch-Mode": '"navigate"',
        "Sec-Fetch-Site": '"none"',
        "Sec-Fetch-User": '"?1"',
        "Sec-Gpc": '"1"',
        "Upgrade-Insecure-Requests": '"1"',
        "User-Agent": '"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"'
    }

    query_params = {}
    if minprice:
        query_params[params_map['minPrice']] = minprice
    if maxprice:
        query_params[params_map['maxPrice']] = maxprice

    url_parts = list(urlparse(url))
    if query_params:
        encoded_params = urlencode(query_params)
        if url_parts[4]:
            url_parts[4] += '&' + encoded_params
        else:
            url_parts[4] += '?' + encoded_params

    complete_url = urlunparse(url_parts)

    try:
        page = requests.get(complete_url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')

        if realestateportal  == "subito":
            subito.parse_subito(soup)
    except requests.exceptions.RequestException as e:
        print(e)
        return




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("realEstatePortal", help="real estate portal on which to search (subito, idealista, immobiliare)")
    parser.add_argument("url", help="url for rent search query")
    parser.add_argument("--minPrice", "-m", help="minimum price for the query")
    parser.add_argument("--maxPrice", "-M", help="maximum price for the query")
    args = parser.parse_args()

    if args.realEstatePortal is not None and args.url is not None:
        start_search(args.realEstatePortal.lower(), args.url, args.minPrice if args.minPrice is not None else "null",
                     args.maxPrice if args.maxPrice is not None else "null")
