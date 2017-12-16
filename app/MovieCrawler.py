#!/usr/bin/python35

# -*- coding: utf-8 -*-

import os
import re
import urllib.request
import urllib.response
from bs4 import BeautifulSoup
import unittest


class MovieCrawler:

    def __init__(self, url, output_dir):
        self.BASE_URL = url
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        self.categories = []

    def download_page(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
        }
        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(request)
        return response.read()

    def get_category_idx_links(self):
        '''
        get detail page link
        :param page:
        :return:
        '''
        home_html = MovieCrawler.download_page(self.BASE_URL)
        home_dom = BeautifulSoup(home_html, 'html.parser', from_encoding='gbk')
        categories = home_dom.select('.bd3rl .co_area2 .title_all')
        for category in categories[0:4]:
            category_name = category.find('strong').text
            category_idx = category.find('a')['href']
            self.categories.append(
                (category_name, self.BASE_URL + category_idx if category_idx.startswith('/') else category_idx))

    def process_detail_page(self, task):
        '''
        :param task: link item
        '''
        links = []
        link, name = task
        detail_soup = BeautifulSoup(MovieCrawler.download_page(link), 'html.parser', from_encoding='gbk')
        zoom = detail_soup.find('div', attrs={'id': 'Zoom'})
        for item in zoom.find_all(name=['img', 'a']):
            if item.name == 'img':
                img_src = item['src']
                with open(self.output_dir + img_src.split("/")[-1], 'wb') as img_w:
                    img_w.write(MovieCrawler.download_page(img_src))

            if item.name == 'a':
                links.append((item.text + "," + item['href'] + "\n"))

        with open(self.output_dir + re.sub('[/\\,!@#$%^&*()+]', '_', name) + '_links.txt', 'w',
                  encoding="utf-8") as link_file:
            link_file.writelines(links)

    def execute(self):
        self.get_category_idx_links()
        movie_links_on_categories = []
        for category in self.categories:
            category_name, category_idx_link = category
            movie_links_on_categories += self.get_detail_links_from_category_page(category_idx_link)

        for idx in range(len(movie_links_on_categories)):
            movie_link = movie_links_on_categories[idx]
            print("[{current_idx}/{total}]: {name}".format(current_idx=idx + 1, total=len(movie_links_on_categories),
                                                           name=movie_link[1]))
            self.process_detail_page(movie_link)

    def get_detail_links_from_category_page(self, category_url):
        soup_category_page = MovieCrawler.download_page(category_url)
        category_html = BeautifulSoup(soup_category_page, 'html.parser', from_encoding='gbk')
        movie_a_list = category_html.select('.co_content8 table tr td b a.ulink')
        return [(self.BASE_URL + a['href'], a.text) for a in movie_a_list]



if __name__ == '__main__':
    url = "http://www.dytt8.net"
    output_dir = os.getcwd() + "/crawler_output/"
    movie_crawler = MovieCrawler(url, output_dir)
    movie_crawler.execute()
