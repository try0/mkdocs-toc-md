import logging
import os
from pathlib import Path
from logging import Logger
import re
from bs4 import BeautifulSoup
from bs4.element import Tag
from mkdocs.structure.pages import Page
from mkdocs.structure.nav import Navigation
from mkdocs.config.base import Config
from mkdocs_toc_md.objects import TocConfig, TocItem

logger = logging.getLogger('mkdocs.toc-md')

# def find_src_elements(bs_page_soup: BeautifulSoup, page: Page, toc_config: TocConfig) -> list[Tag]:
#     toc_module_logger.info('extend find_src_elements')

#     elements = bs_page_soup.find_all(['h1', 'h2', 'h3'])
#     return elements


# def create_toc_items(page: Page, page_description: str, src_elements: list[Tag], toc_config: TocConfig) -> list[TocItem]:
#     toc_module_logger.info('extend create_toc_items')

#     toc_items = []
#     for elm in src_elements:

#         toc_item = TocItem()
#         toc_item.metadata['page.file.abs_dest_path'] = page.file.abs_dest_path
#         # extract anchor link text
#         if elm.find('a', attrs={'class', 'headerlink'}):
#             elm.a.extract()

#         toc_item.text = elm.text
#         toc_item.url = page.file.src_path + '#' + elm.get('id')

#         if elm.name == 'h1':
#             toc_item.src_level = 1
#             if page_description:
#                 toc_item.description = page_description
#         elif elm.name == 'h2':
#             toc_item.src_level = 2
#         elif elm.name == 'h3':
#             toc_item.src_level = 3
#         elif elm.name == 'h4':
#             toc_item.src_level = 4
#         elif elm.name == 'h5':
#             toc_item.src_level = 5
#         elif elm.name == 'h6':
#             toc_item.src_level = 6

#         on_create_toc_item(toc_item, elm, page, toc_config)
#         toc_items.append(toc_item)

#     return toc_items

# index_pattern = re.compile('.*(index.*.md$|index.md$)')
# def on_create_toc_item(toc_item: TocItem, src_element: Tag,  page: Page, toc_config: TocConfig):
#     logger.info("hook on_create_toc_item")

#     if index_pattern.match(page.file.src_path):
#         if toc_item.src_level > 1:
#             toc_item.src_level += 1

#     if toc_item.src_level > 6:
#         toc_item.src_level = 6


# def on_before_output(nav: Navigation, toc_items: list[TocItem], toc_config: TocConfig):
#     toc_module_logger.info("hook on_before_output")

#     toc_item = TocItem()
#     toc_item.src_level = 1
#     toc_item.text = "External Link"
#     toc_item.description = "Added on on_before_output event"
#     toc_item.url = "https://github.com/try0/mkdocs-toc-md"

#     toc_items.append(toc_item)
