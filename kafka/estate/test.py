from crawlers import EstateCrawlerSelenium

crawler = EstateCrawlerSelenium(
        kafka_server="0.0.0.0:9092",
        topic="test",
        save_dir="./data",
        headless=True,
        take_screenshot=False,
    )
crawler.start()
try:
    crawler.crawl_all()
finally:
    crawler.close()