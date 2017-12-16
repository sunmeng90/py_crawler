#!/usr/bin/python35

# -*- coding: utf-8 -*-

import os
import re
import urllib.request
import urllib.response
from bs4 import BeautifulSoup


class MovieCrawler:

    def __init__(self, url, output_dir):
        self.BASE_URL = url
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

    def download_page(url):
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        return response.read()

    def get_links(self, page):
        '''
        get detail page link
        :param page:
        :return:
        '''
        links = []
        dom = BeautifulSoup(page, 'html.parser', from_encoding='gbk')
        sections = dom.select('.bd3rl .co_area2')
        for section in sections[0:4]:
            title = section.find(attrs={'class': 'title_all'}).p.strong.text
            for row in section.select('tr'):
                a = row.select('td:nth-of-type(1) a:nth-of-type(2)')
                link, name = self.BASE_URL + a[0]['href'], a[0].text
                links.append((link, name))
        return links

    def do_task(self, task):
        '''
        :param task: link item
        '''
        links = []
        link, name = task
        detail_soup = BeautifulSoup(self.download_page(link), 'html.parser', from_encoding='gbk')
        zoom = detail_soup.find('div', attrs={'id': 'Zoom'})
        for item in zoom.find_all(name=['img', 'a']):
            if item.name == 'img':
                img_src = item['src']
                with open(self.output_dir + img_src.split("/")[-1], 'wb') as img_w:
                    img_w.write(self.download_page(img_src))

            if item.name == 'a':
                links.append((item.text + "," + item['href'] + "\n"))

        with open(self.output_dir + re.sub('[/\\,!@#$%^&*()+]', '_', name) + '_links.txt', 'w',
                  encoding="utf-8") as link_file:
            link_file.writelines(links)

    def execute(self):
        homepage = self.download_page(self.BASE_URL)
        links = self.get_links(homepage)
        for idx in range(len(links)):
            task = links[idx]
            print("[{current_idx}/{total}]: {name}".format(current_idx=idx + 1, total=len(links), name=task[1]))
            self.do_task(task)


if __name__ == '__main__':
    url = "http://www.dytt8.net"
    output_dir = os.getcwd() + "/crawler_output/"
    movie_crawler = MovieCrawler(url, output_dir)
    movie_crawler.execute()
