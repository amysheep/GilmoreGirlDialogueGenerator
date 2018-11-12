#! /usr/bin/env python3

import json
import re

import scrapy
import scrapy.linkextractors


TRANSCRIPT_PAGE = r'http://transcripts.foreverdreaming.org/viewforum.php?f=22&sid=5428f0805d65c62659b22808b2713af5'


EPISODE_CAPTION_REGX = re.compile(r'^(?P<season>\d+)x(?P<episode>\d+) - ')
LINE_REGEX = re.compile(r'^(?P<actor>\w+): (?P<line>.+)$')


class ScriptTerm(scrapy.Item):
    actor = scrapy.Field()
    line = scrapy.Field()
    season = scrapy.Field()
    episode = scrapy.Field()


class ScriptSpider(scrapy.spiders.CrawlSpider):

    name = r'GilmoreGirlsSpider'
    allowed_domains = [r'transcripts.foreverdreaming.org']
    start_urls = [r'http://transcripts.foreverdreaming.org/viewforum.php?f=22&sid=5428f0805d65c62659b22808b2713af5']
    rules = [
        scrapy.spiders.Rule(
            scrapy.linkextractors.LinkExtractor(
                allow=r'/viewforum\.php\?f=22\&sid=5428f0805d65c62659b22808b2713af5\&start=\d+'
            ),
            follow=True
        ),
        scrapy.spiders.Rule(
            scrapy.linkextractors.LinkExtractor(
                allow=r'/viewtopic\.php\?f=22\&t=\d+\&sid=5428f0805d65c62659b22808b2713af5'
            ),
            callback='parse_episode'
        )
    ]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
        'DOWNLOAD_DELAY': 1.0,
        'FEED_FORMAT': 'jsonlines',
        'FEED_URI': 'script.jl'
    }

    def parse_keyword(self, response: scrapy.http.response.html.HtmlResponse):
        self.logger.info('Entering {}'.format(response.url))

    def parse_episode(self, response: scrapy.http.response.html.HtmlResponse):
        self.logger.info('Entering {}'.format(response.url))

        selector = scrapy.selector.Selector(response=response)
        title_lines = selector.css('div .t-header').css('div .pull-left').xpath('a/text()').extract()
        title_line = title_lines[0]

        match = EPISODE_CAPTION_REGX.match(title_line)
        if not match:
            return
        match_groupdict = match.groupdict()
        season = match_groupdict['season']
        episode = match_groupdict['episode']

        for line in selector.css('div .postbody').xpath('p/text()').extract():
            match = LINE_REGEX.match(line)
            if not match:
                continue
            actor = match.groupdict()['actor']
            actor_line = re.sub('\[.*?\]', '', match.groupdict()['line'])

            yield ScriptTerm(actor=actor, line=actor_line, season=season, episode=episode)
