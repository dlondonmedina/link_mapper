from mapper import mapper 

m = mapper.Mapper(True)

urls = set()
excludeed_domains = set()

print("Welcome to LinkMapper!")
print("This application produces a link map to illustrate how sites are connected.")
print("Thanks for visiting...")
print("Let's start by getting a list of URLs you'd like me to crawl.")
print("I recommend selecting a few that you know might be interesting")

while True: 
    tmp = input("Please give me a URL. OR enter \"d\" when finished. ")
    if tmp.lower() == "d":
        break
    urls.add(tmp)

print("Thanks!")
print("Now there are some URLs you might ignore because the crawl will ")
print("take to long. For instance, if you know the site you start at links ")
print("to Wikipedia, you might exclude wikipedia.org to avoid crawling all ")
print("of Wikipedia.")

while True: 
    tmp = input("Please give me a URL to exclude. OR enter \"d\" when finished. ")
    if tmp.lower() == "d":
        break
    excludeed_domains.add(tmp)

print("Thanks! ")
print("Finally, tell me how many hops you want me to crawl. ")
print("If you choose 1 hop, then I will only visit the links on the start url. ")
print("If you choose 3 hops, I will crawl all of the pages within 3 ")
print("links of the start url. Keep in mind, the more hops, the longer your crawl ")
print("will take for me to finish.")

depth = int(input("How many hops (1-10)"))

m.crawl(urls, depth, excluded_domains=excludeed_domains)

m.print_graph()
