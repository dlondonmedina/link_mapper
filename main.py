from mapper import mapper 

m = mapper.Mapper(True)

urls = set()

tmp = ""

while tmp.lower() != "q": 
    tmp = input("Please give me a URL. OR enter \"q\" when finished. ")
    urls.add(tmp)


m.crawl(urls, 2)

m.print_graph()
