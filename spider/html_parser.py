#!/usr/local/bin/python

# coding:utf8
from bs4 import BeautifulSoup
import re
import urlparse
import urllib2
class HtmlParser(object):

    def _get_new_url(self, page_url, soup):
        new_urls = set()
        links = soup.find_all("a", href=re.compile(r"/view/\d+\.htm"))
        for link in links:
            new_full_url = urlparse.urljoin(page_url, link['href'])
            new_urls.add(new_full_url)
        return new_urls


    def _get_new_data(self, page_url, soup):
        res_data = {}
        res_data['url'] = page_url

        title_node = soup.find("dd",class_="lemmaWgt-lemmaTitle-title").find("h1")
        res_data['title'] = title_node.get_text()
        summary_node = soup.find("div",class_="lemma-summary")
        res_data['summary'] = summary_node.get_text()

        return res_data


    def parser(self, page_url, html_cnt):
        if page_url is None or html_cnt is None:
            return None
        soup = BeautifulSoup(html_cnt, "html.parser", from_encoding="utf-8")
        new_url = self._get_new_url(page_url, soup)
        new_data = self._get_new_data(page_url, soup)

        return new_url, new_data


if __name__ == "__main__":
    parser = HtmlParser()
    page_url = "http://baike.baidu.com/view/21087.htm"
    response = urllib2.urlopen(page_url)
    content = response.read()
    new_url, new_data = parser.parser(page_url, content)
