from pathlib import Path
import sys
import logging
import os
import re
from typing import TYPE_CHECKING, Any, Iterator, List, Mapping, Optional, Type, TypeVar, Union
from mkdocs import plugins
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs.structure.pages import Page
from mkdocs.structure.nav import Navigation, Section, Link
from mkdocs_toc_md.objects import TocConfig, TocItem, TocPageData
from mkdocs_toc_md.hook import TocExtendModule
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
try:
    from mkdocs.plugins import event_priority
except ImportError:
    def event_priority(priority): return lambda f: f  # No-op fallback


logging.getLogger(__name__)


class TocMdPlugin(BasePlugin):

    config_scheme = (
        ('pickup_description_meta', config_options.Type(bool, default=False)),
        ('pickup_description_class', config_options.Type(bool, default=False)),
        ('output_path', config_options.Type(str, default='index.md')),
        ('output_log', config_options.Type(bool, default=False)),
        ('ignore_page_pattern', config_options.Type(str, default='')),
        ('remove_navigation_page_pattern', config_options.Type(str, default='')),
        ('toc_page_title', config_options.Type(str, default='Contents')),
        ('toc_page_description', config_options.Type(str, default=None)),
        ('header_level', config_options.Type(int, default=3)),
        ('template_dir_path', config_options.Type(str, default=None)),
        ('beautiful_soup_parser', config_options.Type(str, default='html.parser')),
        ('languages', config_options.Type(dict, default=dict())),
        ('integrate_mkdocs_static_i18n', config_options.Type(bool, default=False)),
        ('extend_module', config_options.Type(bool, default=False)),
        ('shift_header', config_options.Type(str, default='none')),
        ('output_comment', config_options.Type(str, default='html')),
    )

    def __init__(self):
        self.logger = logging.getLogger('mkdocs.toc-md')
        self.logger.setLevel(logging.INFO)

        self.toc_description_class = 'toc-md-description'
        self.is_build_command = 'build' in sys.argv

    def on_pre_build(self, config):
        self.logger.info("Enabled toc-md plugin")

        self.toc_config = TocConfig(config, self.config)

        self.toc_output_comment = self.toc_config.get_output_comment()

        # mkdocs-static-i18n
        self.i18n_plugin = None
        if self.config['integrate_mkdocs_static_i18n'] and 'i18n' in config['plugins']:
            self.i18n_plugin = config['plugins']['i18n']

        self.hook = TocExtendModule(self.toc_config)

    def on_serve(self, server, config, builder):
        # for dev
        try:
            TocExtendModule.watch_file(server, builder)

            if 'output_path' in self.config:
                output_path = self.config['output_path']
                if self.i18n_plugin:
                    for lang in self.i18n_plugin.i18n_navs:
                        output_path_i18n = re.sub('md$', lang + '.md', output_path)
                        if os.path.exists(output_path_i18n):
                            server.watch(output_path_i18n, builder)
                else:
                    if os.path.exists(output_path):
                        server.watch(output_path, builder)
        except Exception as e:
            self.logger.error('toc-md: Failed watch files', e)

    def on_nav(self, nav: Navigation, config, files):
        # keep navigations
        self.nav = nav


    def on_post_page(self, output_content, page, config):
        # remove navigation items
        pattern = self.config['remove_navigation_page_pattern']
        if pattern:
            remove_navigation_page_re = re.compile(pattern)
            if remove_navigation_page_re.match(page.file.src_path):
                self.logger.info("toc-md: Remove toc")

                soup = BeautifulSoup(
                    output_content, self.config['beautiful_soup_parser'])
                for nav_elm in soup.find_all("nav", {"class": "md-nav md-nav--secondary"}):
                    nav_elm.decompose()

                souped_html = soup.prettify(soup.original_encoding)
                return souped_html

        return output_content

    @plugins.event_priority(-100)
    def on_post_build(self, config):

        ignore_file_pattern = self.config['ignore_page_pattern']
        self.ignore_re = None
        if ignore_file_pattern:
            self.ignore_re = re.compile(ignore_file_pattern)

        self.header_names = []
        for level in range(self.config['header_level']):
            self.header_names.append('h' + str(level + 1))

        self.logger.info('toc-md: Lookup ' + ', '.join(self.header_names))

        if self.i18n_plugin:
            # mkdocs-static-i18n
            # https://github.com/ultrabug/mkdocs-static-i18n

            for lang in self.i18n_plugin.i18n_navs:
                use_folder = 'folder' == self.i18n_plugin.config['docs_structure']
                nav = self.i18n_plugin.i18n_navs[lang]
                if use_folder:
                    self.output(config, nav, "", lang)
                else:
                    self.output(config, nav, lang, "")

        else:
            # default

            self.output(config, self.nav, "", "")

    def create_toc_items(self, toc_items, nav_item: Union[Page, Section, Link], config, lang, nav_item_depth):

        if nav_item.is_link and not nav_item.is_page:
            # no page file
            return
        
        if nav_item.is_section and not nav_item.is_page:
            # no page file
            if self.config['shift_header'] and not self.config['shift_header'] == 'none':
                # consider nav hierarchy
                nav_item_depth += 1

            for child_item in nav_item.children:
                self.create_toc_items(toc_items, child_item, config, lang, nav_item_depth)
            return

        # page file

        page = nav_item
        if 'output_path' in self.config:
            output_path = self.config['output_path']
            if page.file.src_path == output_path:
                return

        ignore = self.ignore_re and self.ignore_re.match(
            page.file.src_path)
        if ignore:
            return

        soup = BeautifulSoup(
            page.content, self.config['beautiful_soup_parser'])

        # extract page description
        toc_description = ''
        if 'pickup_description_meta' in self.config:
            if self.config['pickup_description_meta']:
                description_elm = soup.find(
                    'meta', attrs={'name': 'description'})
                if description_elm is not None:
                    toc_description += description_elm['content']

        if 'pickup_description_class' in self.config:
            if self.config['pickup_description_class']:
                description_elm = soup.find(
                    True, class_=self.toc_description_class)
                if description_elm is not None:
                    toc_description += description_elm.text

        if 'toc_md_description' in page.meta:
            toc_description += page.meta['toc_md_description']

        # create TocItem
        src_elements = []
        if self.use_extend_module('find_src_elements'):
            # user impl
            src_elements = self.hook.find_src_elements(soup, page)
        else:
            # default
            src_elements = soup.find_all(self.header_names)

        if self.use_extend_module('create_toc_items'):
            # user impl
            items = self.hook.create_toc_items(
                page, toc_description, src_elements)
            toc_items.extend(items)
        else:
            # default
            for elm in src_elements:

                toc_header = TocItem()
                if elm.find('a', attrs={'class', 'headerlink'}):
                    elm.a.extract()

                toc_header.text = elm.text

                if elm.has_attr("id"):
                    toc_header.url = page.file.src_path + '#' + elm.get('id')
                else:
                    toc_header.url = page.file.src_path
                    self.logger.warning(
                        'toc-md: Cannot generate URL with hash property because the target element has no id attribute.')
                    
                if elm.name == 'h1':
                    toc_header.src_level = 1
                    if toc_description:
                        toc_header.description = toc_description
                elif elm.name == 'h2':
                    toc_header.src_level = 2
                elif elm.name == 'h3':
                    toc_header.src_level = 3
                elif elm.name == 'h4':
                    toc_header.src_level = 4
                elif elm.name == 'h5':
                    toc_header.src_level = 5
                elif elm.name == 'h6':
                    toc_header.src_level = 6

                toc_header.level = (toc_header.src_level + nav_item_depth)

                if self.config['shift_header'] and not self.config['shift_header'] == 'none':
                    index_re = re.compile('.*(index.' + lang + '.md$|index.md$)')
                    if self.config['shift_header'] == 'after_h1':
                        if index_re.match(page.file.src_path):
                            toc_header.level -= 1
                    elif self.config['shift_header'] == 'after_h1_of_index':
                        if index_re.match(page.file.src_path) and toc_header.src_level == 1:
                            toc_header.level -= 1

                if self.use_extend_module('on_create_toc_item'):
                    # user hook
                    self.hook.on_create_toc_item(toc_header, elm, page)
                toc_items.append(toc_header)

    def output(self, config, nav, lang, folder):

        # Pickup headers
        toc_headers = []
        nav_item_depth = 1
        for nav_item in nav.items:
            self.create_toc_items(toc_headers, nav_item, config, lang, nav_item_depth)

        if self.use_extend_module('on_before_output'):
            # user hook
            self.hook.on_before_output(nav, toc_headers)

        # create template arg
        template_param = TocPageData()
        template_param.page_title = self.config['toc_page_title']
        if lang in self.config['languages']:
            if 'toc_page_title' in self.config['languages'][lang]:
                template_param.page_title = self.config['languages'][lang]['toc_page_title']

        template_param.page_description = self.config['toc_page_description']
        if lang in self.config['languages']:
            if 'toc_page_description' in self.config['languages'][lang]:
                template_param.page_description = self.config['languages'][lang]['toc_page_description']

        template_param.toc_headers = toc_headers
        template_param.toc_output_comment = self.toc_output_comment

        self.output_md_file(config, template_param, lang, folder)

    def output_md_file(self, config, template_param, file_suffix, append_folder):
        """ Outputs markdown file. """

        base_path = os.path.abspath(os.path.dirname(__file__))
        template_path = [os.path.join(base_path, 'template')]

        # using custom template
        if 'template_dir_path' in self.config:
            if self.config['template_dir_path'] and os.path.exists(self.config['template_dir_path']):
                template_path = self.config['template_dir_path']
                self.logger.info("toc-md: Use custom template")

        # render contents
        jinja_env = Environment(
            loader=FileSystemLoader(template_path),
            trim_blocks=True
        )
        template = jinja_env.get_template('toc.md.j2')
        toc_output = template.render(data=template_param)

        # print to console
        if 'output_log' in self.config:
            if self.config['output_log']:
                print(toc_output)

        # save file
        if 'output_path' in self.config:
            output_path = self.config['output_path']
            if file_suffix:
                output_path = re.sub('md$', file_suffix + '.md', output_path)

            if output_path:
                abs_md_path = os.path.join(
                    config['docs_dir'], append_folder, output_path)
                os.makedirs(os.path.dirname(abs_md_path), exist_ok=True)

                # avoid infinite loop
                if os.path.isfile(abs_md_path):
                    with open(abs_md_path, 'r', encoding='utf-8') as file:
                        old_content = file.read()
                        if old_content == toc_output:
                            self.logger.info(f'toc-md: No changes')
                            return

                mode = 'x'
                if os.path.isfile(abs_md_path):
                    mode = 'w'

                with open(abs_md_path, mode, encoding='utf-8') as file:
                    file.write(toc_output)

                self.logger.info(
                    f'toc-md: Output a toc markdown file to "{abs_md_path}".')

                if self.is_build_command:
                    self.logger.warning(
                        'toc-md: Command line contains [build]. You may need to build again to render toc md as html.')

    def use_extend_module(self, name) -> bool:
        return 'extend_module' in self.config and self.config['extend_module'] and self.hook.can_call(name)


