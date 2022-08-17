# Sreality scraping application

### How to start

* Please select docker-compose file based on your architecture. I was able to test it on arm64 architecture (M1 Silicon)
  .
* Follow this steps to run the application:

```commandline
git clone https://github.com/petrcezner/sreality-scraper.git
cd sreality-scraper
docker-compose up --build
```

or

```commandline
docker-compose -f docker-compose.aarch64.yml up --build
```

Wait a few seconds till the images are build. Then in your browser open [localhost:8080](http://localhost:8080) and the
application will open.
In the left sidebar you can find the controlling buttons. If you use fresh build, press `Scrape Web` first. Then go to
make yourself a cup of coffee. It will take some time to scrape the website and don't be kick out. After that, the
results will appears. Use slider to select which ad to show (by its number, 500 is max). If you select large range, the
application may stuck. If this happened, reload the page.
If you use the application after several scraping process, you can use `Show Database` right after application start. 