import requests 
import re
import matplotlib.pyplot as plt
import networkx as nx
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

        Args:
            url (str): a url with the protocol.

        Returns:
            output (set): a set of external urls without the protocol.
        """
        output = set()

        if not url or not isinstance(url, str):
            return output 

        if root_url == None:
            root_url = url

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
            if tmp == None or "javascript:" in tmp or "mailto:" in tmp or "#" in tmp: # javascript button, same page link
                pass
            elif tmp[:2] == "//": # add protocol
                tmp = "https:" + tmp 
                output.add(tmp)     
            elif re.search("https?://*", tmp) is not None: # external link
                output.add(tmp)
            else:
                tmp = tmp.strip("./")
                
                tmp = root_url.strip("/") + "/" + tmp
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
        self.g.add_node(url)
        self.g.add_nodes_from(ex_links)
        self.g.add_edges_from([(url, l) for l in ex_links])


    def print_graph(self, labels: bool = True):
        """
        Generates a png file of the instances graph.

        Args: 
            labels (bool): True if the graph should be labelled.
        """

        if labels:
            nx.draw_networkx(self.g)
        else:
            nx.draw(self.g)
        plt.savefig("map.png")


    def crawl(self, urls: set, depth: int = 2):
        """
        Main crawl method that crawls the input list of urls.

        Args:
            urls (set): A set of urls to visit as a starting point. 
            depth (int): Number of jumps from starting urls the crawl should go.
        """

        if depth <= 0:
            return

        for url in urls:
            ex_links = self.get_links(url)
            self.build_graph(url, ex_links)
            self.crawl(ex_links, depth - 1)
        

    

