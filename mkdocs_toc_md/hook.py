import logging
import os
import sys
import importlib

from logging import Logger
from bs4 import BeautifulSoup
from bs4.element import Tag
from mkdocs.structure.pages import Page
from mkdocs.structure.nav import Navigation
from mkdocs.config.base import Config
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mkdocs_toc_md.objects import TocItem



class TocExtendModule(object):

    module_name = 'toc_extend_module'

    @classmethod
    def watch_file(cls, server, builder):
        module_file = cls.module_name + '.py'
        if os.path.exists(module_file):
            server.watch(module_file, builder)

    def __init__(self):
        self.logger = logging.getLogger(
            'mkdocs.toc-md').getChild('extend-module')
        self.delegate_module = self.load_module()

    def load_module(self):
        cwd = os.getcwd()
        if cwd not in sys.path:
            sys.path.append(cwd)

        try:
            module = __import__(self.__class__.module_name)
            importlib.reload(module)
            self.logger.info('toc-md: load module')
        except ModuleNotFoundError:
            module = None

        return module

    def can_call(self, method_name: str) -> bool:
        return self.delegate_module and hasattr(self.delegate_module, method_name)

    def find_src_elements(self, bf_page_soup: BeautifulSoup, page: Page) -> list[Tag]:
        if self.can_call('find_src_elements'):
            return self.delegate_module.find_src_elements(bf_page_soup, page, self.logger)
        else:
            return []

    def create_toc_items(self, page: Page, toc_description: str, header_elements: list[Tag]) -> list['TocItem']:
        if self.can_call('create_toc_items'):
            return self.delegate_module.create_toc_items(page, toc_description, header_elements, self.logger)
        else:
            return []

    def on_create_toc_item(self, toc_item: 'TocItem', src_element: Tag, page: Page):
        if self.can_call('on_create_toc_item'):
            self.delegate_module.on_create_toc_item(
                toc_item, src_element, page, self.logger)

    def on_before_output(self, nav: Navigation, toc_headers: list['TocItem']):
        if self.can_call('on_before_output'):
            self.delegate_module.on_before_output(
                nav, toc_headers, self.logger)
