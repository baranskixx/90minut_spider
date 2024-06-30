BOT_NAME = "minut90_spider"
SPIDER_MODULES = ["minut90_finder.spiders"]
NEWSPIDER_MODULE = "minut90_finder.spiders"
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
CONCURRENT_REQUESTS = 256
CONCURRENT_REQUESTS_PER_DOMAIN = 256
LOG_LEVEL = 'INFO'
PARSE_IMGS = False

ITEM_PIPELINES = {
    "minut90_finder.pipelines.BirthDatePipeline": 100,
    "minut90_finder.pipelines.LeagueStatsPipeline": 150,
    "minut90_finder.pipelines.ClubsPipeline": 200,
    "minut90_finder.pipelines.PlayerNamePipeline": 250,
    "minut90_finder.pipelines.ItemExportPipeline": 300
}
