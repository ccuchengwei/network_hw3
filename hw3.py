from bs4 import BeautifulSoup
import requests
import requests.exceptions
from urllib.parse import urlsplit
from collections import deque
import re
import argparse


# a set of urls that we have already crawled
processed_urls = set()
 
# a set of crawled emails
emails = set()
def craweremail(starturl):
    icount = 0
    # a queue of urls to be crawled
    new_urls = deque([starturl])
    # process urls one by one until we exhaust the queue
    while len(new_urls):
        icount += 1
        # move next url from the queue to the set of processed urls
        url = new_urls.popleft()
        processed_urls.add(url)
     
        # extract base url to resolve relative links
        parts = urlsplit(url)
        base_url = "{0.scheme}://{0.netloc}".format(parts)
        if '/' in parts.path:
            path = url[:url.rfind('/')+1]   
        else:
            path = url
        # get url's content
        print("Processing %s" % url)
        try:
            response = requests.get(url)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            # ignore pages with errors
            continue
     
        # extract all email addresses and add them into the resulting set
        new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
        emails.update(new_emails)
     
        # create a beutiful soup for the html document
        soup = BeautifulSoup(response.text)
     
        # find and process all the anchors in the document
        for anchor in soup.find_all("a"):
            # extract link url from the anchor
            link = anchor.attrs["href"] if "href" in anchor.attrs else ''
            # resolve relative links
            if link.startswith('/'):
                link = base_url + link
            elif not link.startswith('http'):
                link = path + link
            # add the new url to the queue if it was not enqueued nor processed yet
            if not link in new_urls and not link in processed_urls:
                new_urls.append(link)
        for email in new_urls:
            print (new_emails)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Crawler email")
    parser.add_argument('url', help='begine URL')
    
    start_url = parser.parse_args().url
   
    starting_netloc = urlsplit(start_url).netloc
    if starting_netloc == '':
        print("Please enter a valid URL such as https://www.google.com.tw")
    else:
        craweremail(start_url)