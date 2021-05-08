#!coding: utf-8
from lxml import html
import rss_reader
def main(url, forras_szoveg):
    html_tartalom=rss_reader.read(url, forras_szoveg)
    html.open_in_browser(html.document_fromstring(html_tartalom), encoding='utf-8')

