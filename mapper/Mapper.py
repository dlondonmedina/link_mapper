import requests 
import re
from time import sleep
from random import randint
from bs4 import BeautifulSoup

class Mapper:

    def __init__(self, start_urls: set, depth: int = 3, backlinks: bool = False):
        """
        Class constructor establishes start url, search depth, and backlink requirement.
        
        Args:
            start_urls (set): Set of unique addresses to begin the mapping.
            depth (int): The number of hops that the spider should crawl from start URL
            backlinks (bool): If True, links are only saved if they link back to previous link.
        
        """
        self.start_urls = start_urls
        self.depth = depth
        self.backlinks = backlinks 

        # Initialize headers for scraping 

        self.headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }

        
    
    def get_links(self, url: str, visited: set = None) -> set:
        """
        Gets external links from all pages on a domain. 

        Args:
            url (str): a url with the protocol.

        Returns:
            output (set): a set of external urls without the protocol.
        """
        output = set()

        if not url or not isinstance(url, str):
            return output 
        
        if visited == None:
            visited = set()

        m = re.search("https?://([A-Za-z_0-9.-]+).*", url)
        base_url = m.group(1)

        output  = set()

        try:
            print("Visiting {}!".format(url))
            req = requests.get(url, self.headers)
        except requests.exceptions.ConnectionError:
            print("Connection Error on: {} Returning empty output.".format(url))
            return output
        except requests.exceptions.Timeout:
            print("Timeout Error on: {} Returning empty output.".format(url))
            return output 
        except requests.exceptions.TooManyRedirects:
            print("Redirect Error on: {} Returning empty output.".format(url))
            return output
        except requests.exceptions.RequestException as e:
            print("Unknown Error {} on: {} Returning empty output.".format(e, url))
            return output

        soup = BeautifulSoup(req.content, 'html.parser')

        for l in soup.find_all('a'):
            tmp = l.get('href')
            if tmp == None or "javascript:" in tmp or "#" in tmp: # javascript button, same page link
                pass
            elif tmp[:2] == "//": # add protocol
                tmp = "https:" + tmp 
                output.add(tmp)     
            elif re.search("https?://*", tmp) is not None: # external link
                output.add(tmp)
            elif tmp not in visited:
                visited.add(tmp)
                if tmp[0] != "/":
                    tmp = "/" + tmp 
                tmp = "https://" + base_url + tmp
                print("Found internal link...friendly spiders wait")
                for i in range(randint(0,5)):
                    print("...")
                    sleep(1)
                output.update(self.get_links(tmp, visited))

        return output 



    

