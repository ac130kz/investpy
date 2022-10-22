import argparse
import datetime
import os

# Get's list of url's with proxies
import random
import re
import sys
import time
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

import data
import requests
from bs4 import BeautifulSoup

user_agent_list = [
    # Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
    # Firefox
    "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)",
    "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)",
]

headers = {"User-Agent": random.choice(user_agent_list)}

date = datetime.datetime.today().strftime("%Y-%m-%d")
filename = "{} ProxyList.txt".format(date)
threads = []
url = "https://www.google.com"
timeout = 8
hits = 0
num_threads = 30
max = 800
######################################################################


def get_links():
    links = []
    keyword = "server-list"
    index_url = "http://www.proxyserverlist24.top/"
    page = requests.get(index_url)
    soup = BeautifulSoup(page.text, "html.parser")
    temp_links = soup.find_all("a")
    for atag in temp_links:
        link = atag.get("href")
        if atag.get("href") is None:
            pass
        elif keyword in link and "#" not in link and link not in links:
            links.append(link)
    return links


# Scrape most recently uploaded proxies and returns a list of proxies
# according to the maximum amount entered by the user (default 800)


def scrape(links):
    url = links[0]
    page = requests.get(url)
    ip_list = re.findall(r"[0-9]+(?:\.[0-9]+){3}:[0-9]+", page.text)
    return max_proxies(ip_list, data.max)


# Save scraped list into a file


def save_scraped(ip_list):
    if os.path.isfile(data.filename):
        os.remove(data.filename)
    with open(data.filename, "a") as wfile:
        for ip in ip_list:
            wfile.write(ip)
            wfile.write("\n")
    print("[!] {} Proxies were scraped and saved ! ".format(len(ip_list)))


# Maximum amount of proxies to scrape


def max_proxies(ip_list, max):
    ip_list = ip_list.copy()
    return ip_list[0:max]


# Check if proxy is alive and gets a 200 response


def is_good(p):
    proxy = {"https": "{}".format(p)}
    try:
        r = requests.get(data.url, proxies=proxy, headers=data.headers, timeout=data.timeout)
        if r.status_code is 200:
            hits_count(p)
            save_hits(p)
    except (
        requests.exceptions.Timeout,
        requests.exceptions.ProxyError,
        requests.exceptions.SSLError,
        requests.exceptions.ConnectionError,
    ) as e:
        pass


# Save working proxy to a file


def save_hits(p):
    with open("{} Checked ProxyList.txt".format(data.date), "a") as wfile:
        wfile.write(p)
        wfile.write("\n")


# Count hits to display when script finished executing


def hits_count(p):
    data.hits += 1
    print("[+] HIT - {}".format(p))


def hits():
    print("[!] {} Proxies checked and saved !".format(data.hits))


def check_args(args=None):
    parser = argparse.ArgumentParser(description="A script to quickly get alive HTTPS proxies")
    parser.add_argument(
        "-u", "--url", type=str, help="url to check proxy against", required=False, default="https://www.google.com"
    )
    parser.add_argument("-m", "--max", type=int, help="maximum proxies to scrape", required=False, default=800)
    parser.add_argument("-t", "--timeout", type=int, help="set proxy timeout limit", required=False, default=8)
    parser.add_argument(
        "-st", "--set-threads", type=int, help="set number of threads to run", required=False, default=30
    )

    results = parser.parse_args(args)
    return (results.url, results.max, results.timeout, results.set_threads)


# Check multiple proxies at once from a given proxy list


def check(p_list):

    pool = ThreadPool(data.num_threads)
    pool.map(is_good, p_list)
    pool.close()
    pool.join()


def main():

    # Get_links returns a list with links which is passed to scrape() to scrape from
    # which returns a proxy list to save in a file
    save_scraped(scrape(get_links()))

    p_list = open(data.filename).read().splitlines()
    check(p_list)
    hits()


if __name__ == "__main__":
    # Set user input
    data.url, data.max, data.timeout, data.num_threads = check_args(sys.argv[1:])
    main()
