import scrapy
import logging
import os
import sys
from datetime import datetime, timedelta

class TP_Spider(scrapy.Spider):
    name = "TPGrabReviews"
    start_urls = [
        'https://uk.trustpilot.com/review/cinch.co.uk?sort=recency',
        'https://uk.trustpilot.com/review/cazoo.co.uk?sort=recency',
        'https://uk.trustpilot.com/review/carwow.co.uk?sort=recency',
        'https://uk.trustpilot.com/review/motorway.co.uk',
    ]
    custom_settings = {
        'FEEDS': {'TrustPilot.json': {'format':'json', 'overwrite': True}}
    }

    def parse(self,response):
        for reviews in response.css('div.styles_reviewCardInner__EwDq2'):
            try:
                posted_date_time = reviews.css('div.typography_body-m__xgxZ_.typography_appearance-subtle__8_H2l.styles_datesWrapper__RCEKH > *:last-child').attrib['datetime']
            except:
                posted_date_time = reviews.css('div.typography_body-m__xgxZ_.typography_appearance-subtle__8_H2l.styles_datesWrapper__RCEKH > span > time').attrib['datetime']
            posted_date_time = datetime.strptime(posted_date_time, "%Y-%m-%dT%H:%M:%S.%fZ")   # Convert to datetime object
            if posted_date_time < datetime.now() - timedelta(days=180):  # If the review is older than 6 months stop the spider
                return   
            try:
                yield {
                    'url':response.url,
                    'From':  reviews.css('div.typography_body-m__xgxZ_.typography_appearance-subtle__8_H2l.styles_detailsIcon__Fo_ua > *:last-child::text').get(),
                    'Num_Of_Reviews': reviews.css('span.typography_body-m__xgxZ_.typography_appearance-subtle__8_H2l::text').get(),
                    'Experience_Date': reviews.css('p.typography_body-m__xgxZ_.typography_appearance-default__AAY17::text')[1].get(),
                    'Posted_DateTime': reviews.css('div.typography_body-m__xgxZ_.typography_appearance-subtle__8_H2l.styles_datesWrapper__RCEKH > *:last-child').attrib['datetime'],
                    'Review_Stars': reviews.css('div.styles_reviewHeader__iU9Px').attrib['data-service-review-rating'],
                    'Review_Type': reviews.css('div.typography_body-m__xgxZ_.typography_appearance-subtle__8_H2l.styles_detailsIcon__yqwWi > *:last-child::text').get(),
                    'Review_Title': reviews.css('h2.typography_heading-s__f7029.typography_appearance-default__AAY17::text').get(),
                    'Review_Text': reviews.css('p.typography_body-l__KUYFJ.typography_appearance-default__AAY17.typography_color-black__5LYEn::text').get(),
                }
            except:
                yield {
                    'url':response.url,
                    'From':  reviews.css('div.typography_body-m__xgxZ_.typography_appearance-subtle__8_H2l.styles_detailsIcon__Fo_ua > *:last-child::text').get(),
                    'Num_Of_Reviews': reviews.css('span.typography_body-m__xgxZ_.typography_appearance-subtle__8_H2l::text').get(),
                    'Experience_Date': reviews.css('p.typography_body-m__xgxZ_.typography_appearance-default__AAY17::text')[1].get(),
                    'Posted_DateTime': reviews.css('div.typography_body-m__xgxZ_.typography_appearance-subtle__8_H2l.styles_datesWrapper__RCEKH > span > time').attrib['datetime'],
                    'Review_Stars': reviews.css('div.styles_reviewHeader__iU9Px').attrib['data-service-review-rating'],
                    'Review_Type': reviews.css('div.typography_body-m__xgxZ_.typography_appearance-subtle__8_H2l.styles_detailsIcon__yqwWi > *:last-child::text').get(),
                    'Review_Title': reviews.css('h2.typography_heading-s__f7029.typography_appearance-default__AAY17::text').get(),
                    'Review_Text': reviews.css('p.typography_body-l__KUYFJ.typography_appearance-default__AAY17.typography_color-black__5LYEn::text').get(),
                }
        try:
            next_page = response.css('a.link_internal__7XN06.button_button__T34Lr.button_m__lq0nA.button_appearance-outline__vYcdF.button_squared__21GoE.link_button___108l.pagination-link_next__SDNU4.pagination-link_rel__VElFy').attrib['href']
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)
        except KeyError:
            pass

#process = CrawlerProcess({
#   'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
# })

#Next bit stops crawler falling over on re-runs by deleting existing jl/json file and installed reactor
#def delfile(filename):
#   try:
#       os.remove(filename)
#   except OSError:
#       pass
#delfile('TrustPilot.jl')
#delfile('TrustPilot.json')

if "twisted.internet.reactor" in sys.modules:
    del sys.modules["twisted.internet.reactor"]