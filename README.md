# sayari_task
Web scraping and entity resolution task solution.

System requirements: Python 3.7 or later, GraphViz, Scrapy, Networkx, Matplotlib

The ouptut in this repo can be produced by running the following from the command line :

$ scrapy runspider nd_spider.py -a query=<query_starts_with> -s FEED_URI=<path_to_scrape_result.jl>
$ python3 business_network.py -i <path_to_scrape_result.jl> -o <path_to_network_visualization.pdf>
