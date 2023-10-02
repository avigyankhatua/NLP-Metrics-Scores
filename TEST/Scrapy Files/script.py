import scrapy
from scrapy.crawler import CrawlerProcess
import article_data
import pandas as pd

# Create a CrawlerProcess instance
process = CrawlerProcess()

# Add your spider to the process
process.crawl(articlespider)

# Start the crawling process
process.start()