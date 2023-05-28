
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
    metadata = dict()



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
