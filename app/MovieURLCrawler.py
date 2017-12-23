#!/usr/bin/python35

# -*- coding: utf-8 -*-

import os
import re
import urllib.request
import urllib.response
from bs4 import BeautifulSoup
from queue import Queue
import threading
import datetime
import pprint
from pymongo import MongoClient


class CrawlerUtils(object):

    def download_page(url, encoding=None):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
        }
        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request)
        return response.read.decode(encoding) if encoding else response.read()


class MovieURLCrawler:

    def __init__(self, url):
        self.BASE_URL = url
        self.categories = []

    def get_category_idx_urls(self):
        '''
        get detail page link
        :param page:
        :return:
        '''
        home_html = CrawlerUtils.download_page(self.BASE_URL)
        home_dom = BeautifulSoup(home_html, 'html.parser', from_encoding='gbk')
        categories = home_dom.select('.bd3rl .co_area2 .title_all')
        for category in categories[0:3]:
            category_name = category.find('strong').text
            category_idx = category.find('a')['href']
            self.categories.append(
                (category_name, self.BASE_URL + category_idx if category_idx.startswith('/') else category_idx))

    def get_all_page_urls_for_category(category_idx_url):
        soup_idx = BeautifulSoup(CrawlerUtils.download_page(category_idx_url), 'html.parser',
                                 from_encoding='gbk')
        page_list = soup_idx.select('select[name="sldd"] option')
        url_base = category_idx_url[:category_idx_url.rfind('/') + 1]
        return [url_base + page_url['value'] for page_url in page_list]

    def get_movie_page_urls_on_page(self, category_url):
        soup_category_page = CrawlerUtils.download_page(category_url)
        category_html = BeautifulSoup(soup_category_page, 'html.parser', from_encoding='gbk')
        movie_a_list = category_html.select('.co_content8 table tr td b a.ulink')
        return [{'name': a.text, 'href': self.BASE_URL + a['href']} for a in movie_a_list]

    def get_all_movie_urls(self):
        self.get_category_idx_urls();
        category_page_urls = []
        for category_url in self.categories:
            category_name, category_address = category_url
            print("Get page urls for category %s" % category_name)
            category_page_urls += MovieURLCrawler.get_all_page_urls_for_category(category_address)

        all_idx_page_urls_on_category = []
        for category_page_url in category_page_urls:
            all_idx_page_urls_on_category += self.get_movie_page_urls_on_page(category_page_url)
        return all_idx_page_urls_on_category


class MovieQueue(threading.Thread):

    def __init__(self, queue, output_dir, mongo_collection):
        threading.Thread.__init__(self)
        self.queue = queue
        self.output_dir = output_dir
        self.mongo_collection = mongo_collection
        self.total = queue.qsize()

    def run(self):
        while True:
            task = self.queue.get()
            print(str(threading.current_thread()) + ": [{remaining}/{total}] -> {name}".format(
                remaining=self.queue.qsize(), total=self.total, name=task['name']))
            self.process_detail_page(task)
            self.mongo_collection.update({'_id': task['_id']}, {"$set": {"saved": True}})
            self.queue.task_done()

    def process_detail_page(self, task):
        '''
        :param task: link item
        '''
        links = []
        detail_soup = BeautifulSoup(CrawlerUtils.download_page(task['href']), 'html.parser', from_encoding='gbk')
        zoom = detail_soup.find('div', attrs={'id': 'Zoom'})
        for item in zoom.find_all(name=['img', 'a']):
            if item.name == 'img':
                img_src = item['src']
                with open(self.output_dir + img_src.split("/")[-1], 'wb') as img_w:
                    img_w.write(CrawlerUtils.download_page(img_src))

            if item.name == 'a':
                links.append((item.text + "," + item['href'] + "\n"))

        with open(self.output_dir + re.sub('[/\\,!@#$%^&*()+]', '_', task['name']) + '_links.txt', 'w',
                  encoding="utf-8") as link_file:
            link_file.writelines(links)


def crawler_main(output_dir, mongo_collection):
    all_movie_urls = list(movie_collection.find({'saved': {'$exists': False}}))
    if not all_movie_urls: return
    print("Total movies: %s" % len(all_movie_urls))
    queue = Queue()
    for task in all_movie_urls:
        queue.put(task)

    for i in range(5):
        t = MovieQueue(queue, output_dir, mongo_collection)
        # t.setDaemon(True)
        t.setName("Crawler " + str(i))
        t.start()
    queue.join()


def save_movie_links(movies):
    [movie_collection.save(movie) for movie in movies]


if __name__ == '__main__':
    url = "http://www.dytt8.net"
    output_dir = os.getcwd() + "/crawler_output/"
    conn = MongoClient('localhost', 27017)
    movie_db = conn.movie_db
    movie_collection = movie_db.movie_collection
    crawler_main(output_dir, movie_collection)