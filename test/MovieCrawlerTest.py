#!/usr/bin/python35

# -*- coding: utf-8 -*-

from mockito import mock, verify
import os
from app.MovieCrawler import MovieCrawler

import unittest


class MovieCrawlerTest(unittest.TestCase):
    def setUp(self):
        url = "http://www.dytt8.net"
        output_dir = os.getcwd() + "/crawler_output/"
        self.movie_crawler = MovieCrawler(url, output_dir)

    def tearDown(self):
        pass

    def test_blala(self):
        self.assertIn("todo", ['todo', 'haha'])
        # self.assertIn("todo1", ['todo','haha'], 'todo1')
        pass

    def test_get_detail_links_from_category_page(self):
        movie_links = self.movie_crawler.get_movie_page_urls_on_page(
            "http://www.ygdy8.net/html/gndy/china/index.html");
        print(movie_links)


if __name__ == '__main__':
    unittest.main()
