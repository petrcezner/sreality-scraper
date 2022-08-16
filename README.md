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
In the left sidebar you can find the controlling buttons. If you use fresh build, press `Scrape Web` first. Then wait a
few minutes, till the first 500 advertisements. After that, the results will appears.
If you use the application after several scraping process, you can use `Show Database` right after application start.