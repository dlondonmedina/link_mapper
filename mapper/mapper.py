import requests 
import re
import json
import time
import matplotlib.pyplot as plt
import networkx as nx
from networkx.readwrite import json_graph
from time import sleep
from random import randint
from bs4 import BeautifulSoup

class Mapper:

    def __init__(self, directional: bool = False):
        """
        Class constructor establishes start url, search depth, and backlink requirement.
        
        Args:
            directional (bool): If True, the graph will be directional and allow loops.
        
        """
        # Initialize Graph
        if directional:
            self.g = nx.MultiDiGraph()
        else:
            self.g = nx.Graph()
        
        # Initialize headers for scraping 

        self.headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }

        self.visited = set()
        
    
    def get_links(self, url: str, root_url = None) -> set:
        """
        Gets external links from all pages on a domain. 
        This won't function on sites that require javascript.

        Args:
            url (str): a url with the protocol.

        Returns:
            output (set): a set of external urls without the protocol.
        """
        output = set()

        if not url or not isinstance(url, str):
            return output 

        if root_url == None:
            if url.rfind("/") == -1:
                root_url = url
            else:
                root_url = url[:url.rfind("/") + 1]

        elif re.search("https?://*", root_url) is None:
            return output

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
            filter = [None, "", "/", "./", "../", "#", ".", ".."]

            if tmp in filter:
                continue 
            
            # Remove params
            tmp = tmp[:tmp.find("?")] if tmp.find("?") > -1 else tmp 
            
            # Add protocol
            if tmp[:2] == "//":
                tmp = "https:" + tmp 
            
            # if it's external link, add to external link set.
            if re.search(r"^https?://", tmp) is not None and root_url not in tmp:
                output.add(tmp)

            elif ":" in tmp.strip(r'^https?://') or "#" in tmp: 
                #ignore None or special links or same page links
                continue
            else:
                filters = ["./", "../", "/."]
                for f in filters:
                    tmp = tmp.replace(f, "/")
                
                if root_url not in tmp:
                    if tmp[0] == "/" and root_url[-1] == "/":
                        tmp = root_url.strip("/") + tmp 
                    elif tmp[0] != "/" and root_url[-1] != "/":
                        tmp = root_url + "/" + tmp 
                    else:
                        tmp = root_url + tmp

                if tmp not in self.visited:
                    self.visited.add(tmp)
                    print("Found internal link...friendly spiders wait")
                    for i in range(randint(0,5)):
                        print("...")
                        sleep(1)
                    output.update(self.get_links(tmp, root_url))

        return output 


    def build_graph(self, url: str, ex_links: set):
        """
        Adds to the instance's graph the current url plus outward 
        connections to all ex_links.
        
        Args:
            url (str): The url address of the source site.
            ex_links (set): The set of external links from url.

        """
        domain = self.get_domain(url)

        for l in ex_links:
            link = self.get_domain(l)
            self.g.add_edge(domain, link)


    def print_graph(self, labels: bool = True):
        """
        Generates a png file of the instances graph.

        Args: 
            labels (bool): True if the graph should be labelled.
        """
        # Write to JSON first
        timestamp = int(time.time())
        with open('graph{}.json'.format(timestamp), 'w') as f:
            f.write(json.dumps(json_graph.node_link_data(self.g)))

        if labels:
            nx.draw_networkx(self.g)
        else:
            nx.draw(self.g)
        plt.savefig("map{}.png".format(timestamp))


    def crawl(self, urls: set, depth: int = 2, excluded_domains: set = None):
        """
        Main crawl method that crawls the input list of urls.

        Args:
            urls (set): A set of urls to visit as a starting point. 
            depth (int): Number of jumps from starting urls the crawl should go.
        """

        if depth <= 0:
            return

        for url in urls:
            if any([d in url for d in excluded_domains]):
                continue 

            ex_links = self.get_links(url)
            self.build_graph(url, ex_links)
            self.crawl(ex_links, depth - 1, excluded_domains)
        

    def get_domain(self, url: str) -> str:
    
        d = re.search('https?://([A-Za-z_0-9.-]+).*', url)
        d = d.group(1)
        return d

