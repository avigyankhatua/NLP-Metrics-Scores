import os
import scrapy
import pandas as pd

class ArticlespiderSpider(scrapy.Spider):
    name = 'articlespider'
    allowed_domains = ['insights.blackcoffer.com']
    data = pd.read_excel('Input.xlsx')
    start_urls = list(data['URL'])
    

    def parse(self, response):
        # Extract all <p> elements within the article
        heading = response.xpath('//header[@class="td-post-title"]/h1[@class="entry-title"]/text()').get()
        paragraphs = response.xpath('//div[@class="td-post-content tagdiv-type"]/p')

        # Initialize an empty string to store the extracted text
        extracted_text = ""
        
        # Loop through each <p> element and extract its text, including text within <strong> tags
        for paragraph in paragraphs:
            # Extract text within the current <p> element, including text within <strong> tags
            paragraph_text = " ".join(paragraph.xpath('.//text()').extract())
            paragraph_text = paragraph_text.replace("\n", " ").strip()
            # Append the extracted text to the overall text
            extracted_text += paragraph_text.strip() + " "


        yield{
            'Index': self.data['URL_ID'][self.start_urls.index(response.url)],
            'Title' : heading,
            'Body' : extracted_text
        }        
        
        
