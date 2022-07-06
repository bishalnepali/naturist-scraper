#naturist-scraper




## HOW TO INSTALL THE DEPENDENCIES


    pip install - requirements.txt



## HOW TO RUN THE SCRIPT


    scrapy crawl naturitas


Above is the command to run the scraper which will create the csv file with name naturitas_scraper.csv.

If you want to have the result in the json file, you can use the command below:

    scrapy crawl naturitas -o naturitas_scraper.json




## HOW TO ADD MORE URLS?
In naturitas_scraper/spiders/naturitas_spider.py file you can add more urls to scrape.
In line  11 add the string of your you want to scrape.


    start_urls = ['https://www.naturitas.com/en/products/', 'your url']
