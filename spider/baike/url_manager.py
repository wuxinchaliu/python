#!/usr/local/bin/python

# coding:utf8

class UrlManager(object):
    def __init__(self):
        self.urls = set()
        self.visited = set()
    def add_new_url(self, url):
        if url is None:
            return
        if url not in self.visited:
            self.urls.add(url)
    def add_new_urls(self, urls):
        if urls is None:
            return
        for url in urls:
            self.add_new_url(url)
    def has_new_url(self):
        return len(self.urls) !=0
    def get_new_url(self):
        new_url = self.urls.pop()
        self.visited.add(new_url)
        return new_url

