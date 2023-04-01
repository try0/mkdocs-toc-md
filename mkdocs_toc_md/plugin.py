import sys
import logging
import os
import re
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader

logging.getLogger(__name__)


class TocPageData:
    """ Page params """
    toc_output_comment = None
    page_title = None
    page_description = None
    toc_headers = []

class TocItem:
    """ headers """
    src_level = 1
    text  = None
    description = None
    url = None
    parent = None
    children = []


    def get_md_header_prefix(self) -> str:
        """ Gets level as markdown header. """

        prefix = '#'
        for num in range(self.src_level):
            prefix += '#'
        return prefix


    def get_text_as_md_header(self) -> str:
        """ Gets text as markdown header. """

        prefix = self.get_md_header_prefix()

        if self.url:
            return prefix + ' [' + self.text + '](' + self.url + ')'

        return prefix + ' ' + self.text
        

    def get_text_as_md_ul_item(self) -> str:
        """ Gets text as markdown list item. """

        if self.url:
            return '* [' + self.text + '](' + self.url + ')'
        
        return '* ' + self.text


    def get_text_as_md_ol_item(self) -> str:
        """ Gets text as markdown ordered list item. """

        if self.url:
            return '1. [' + self.text + '](' + self.url + ')'
        
        return '1. ' + self.text

    def has_description(self) -> bool:
        return self.description is not None 



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
    )


    def __init__(self):
        self.logger = logging.getLogger('mkdocs.toc-md')
        self.logger.setLevel(logging.INFO)
        
        self.toc_description_class = 'toc-md-description'

        self.toc_output_comment = ''
        self.toc_output_comment += '<!-- ====================== TOC ====================== -->\n'
        self.toc_output_comment += '<!-- Generated by mkdocs-toc-md plugin -->\n'
        self.toc_output_comment += '<!-- ================================================= -->\n'
        self.toc_output_comment += '\n'

        self.is_build_command = 'build' in sys.argv


    def on_pre_build(self, config):
        self.logger.info("Enabled toc-md plugin")


    def on_nav(self, nav, config, files):
        # keep navigations
        self.nav = nav


    def on_post_page(self, output_content, page, config):
        
        # remove navigation items
        pattern = self.config['remove_navigation_page_pattern']
        if pattern:
            remove_navigation_page_re = re.compile(pattern)
            if remove_navigation_page_re.match(page.file.src_path):
                self.logger.info("toc-md: Remove toc")

                soup = BeautifulSoup(output_content, self.config['beautiful_soup_parser'])
                for nav_elm in soup.find_all("nav", {"class": "md-nav md-nav--secondary"}):
                    nav_elm.decompose()
        
                souped_html = soup.prettify(soup.original_encoding)
                return souped_html 

        return output_content
        

    def on_post_build(self, config):

        ignore_file_pattern = self.config['ignore_page_pattern']
        ignore_re = None
        if ignore_file_pattern:
            ignore_re = re.compile(ignore_file_pattern)

        header_names = []
        for level in range(self.config['header_level']):
            header_names.append('h' + str(level + 1))

        self.logger.info('toc-md: Lookup ' + ', '.join(header_names))

        # Pickup headers
        toc_headers = []
        for page in self.nav.pages:

            if 'output_path' in self.config:
                output_path = self.config['output_path']
                if page.file.src_path == output_path:
                    continue

            ignore = ignore_re and ignore_re.match(page.file.src_path)
            if ignore:
                continue

            soup = BeautifulSoup(page.content, self.config['beautiful_soup_parser'])

            # extract page description
            toc_description = ''
            if 'pickup_description_meta' in self.config:
                if self.config['pickup_description_meta']:
                    description_elm = soup.find('meta', attrs={'name':'description'})
                    if description_elm is not None:
                        toc_description += description_elm['content']

            if 'pickup_description_class' in self.config:
                if self.config['pickup_description_class']:
                    description_elm = soup.find(True, class_=self.toc_description_class)
                    if description_elm is not None:
                        toc_description += description_elm.text

            if 'toc_md_description' in page.meta:
                toc_description += page.meta['toc_md_description']

            # create TocItem
            article_headers = soup.find_all(header_names)
            for h in article_headers:

                toc_header = TocItem()
                if h.find('a', attrs={'class', 'headerlink'}):
                     h.a.extract()

                toc_header.text = h.text
                toc_header.url = page.file.src_path + '#' + h.get('id')

                if h.name == 'h1':
                    toc_header.src_level = 1
                    if toc_description:
                        toc_header.description = toc_description
                elif h.name == 'h2':
                    toc_header.src_level = 2
                elif h.name == 'h3' :
                    toc_header.src_level = 3
                elif h.name == 'h4' :
                    toc_header.src_level = 4
                elif h.name == 'h5' :
                    toc_header.src_level = 5
                elif h.name == 'h6' :
                    toc_header.src_level = 6

                toc_headers.append(toc_header)



        base_path = os.path.abspath(os.path.dirname(__file__))
        template_path = [os.path.join(base_path, 'template')]

        # using custom template
        if 'template_dir_path' in self.config:
            if self.config['template_dir_path'] and os.path.exists(self.config['template_dir_path']):
                template_path = self.config['template_dir_path']
                self.logger.info("toc-md: Use custom template")


        # create template arg
        template_param = TocPageData()
        template_param.page_title = self.config['toc_page_title']
        template_param.page_description = self.config['toc_page_description']
        template_param.toc_headers = toc_headers
        template_param.toc_output_comment = self.toc_output_comment

        # render contents
        jinja_env = Environment(
            loader = FileSystemLoader(template_path),
            trim_blocks = True
        )
        template = jinja_env.get_template('toc.md.j2')
        toc_output = template.render(data = template_param)

        # print to console
        if 'output_log' in self.config:
            if self.config['output_log']:
                print(toc_output)

        # save file
        if 'output_path' in self.config:
            output_path = self.config['output_path']
            if output_path:
                abs_md_path = os.path.join(config['docs_dir'], output_path)
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
                
                self.logger.info(f'toc-md: Output a toc markdown file to "{abs_md_path}".')

                if self.is_build_command:
                    self.logger.warning('toc-md: Command line contains [build]. You may need to build again to render toc md as html.')





