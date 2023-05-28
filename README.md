
# mkdocs-toc-md

[mkdocs-toc-md](https://pypi.org/project/mkdocs-toc-md/) is a plugin for mkdocs that generates a table of contents in markdown format. To render the table of contents as HTML, the markdown file must be generated before running `mkdocs build`.

![](https://user-images.githubusercontent.com/17096601/199638378-892ddec9-b7af-4eb8-8ca8-a57c02980f53.png)



## Sample

[File](https://github.com/try0/mkdocs-toc-md/blob/main/sample/docs/index.en.md?plain=1)  
[Site](https://try0.github.io/mkdocs-toc-md/sample/site/)




## Usage

### Generates toc markdown file.

1. Install plugin. 
    ```
    pip install mkdocs-toc-md
    ```
1. Add plugin config to mkdocs.yml.

    ```yml
    plugins:
      - toc-md
    ```

1. Run `mkdocs serve` to output the toc md file.

1. Check docs/index.md.


### Adds description.
If you use metadata (front matter), set the value with toc_md_description as a key.
```
---
toc_md_description: pickup target value
---
```

or use options `pickup_description_meta` `pickup_description_class`.



## Options

Minimum
```yml
plugins:
  - toc-md:
```

Full
```yml
plugins:
  - toc-md:
      toc_page_title: Contents
      toc_page_description: Usage mkdocs-toc-md
      header_level: 3
      pickup_description_meta: false
      pickup_description_class: false
      output_path: index.md
      output_log: false
      ignore_page_pattern: index.*.md$
      remove_navigation_page_pattern: index.*.md$
      template_dir_path: custom_template
      integrate_mkdocs_static_i18n: true
      languages:
        en:
          toc_page_title: Contents
          toc_page_description: Usage mkdocs-toc-md
        ja:
          toc_page_title: 目次
          toc_page_description: mkdocs-toc-mdプラグインの使い方
      shift_header: after_h1_of_index
      extend_module: true
      output_comment: html
```

### toc_page_title: str  
h1 text in the table of contents markdown file.

default: Contents

### toc_page_description: str
The description will be rendered below the h1 tag in the table of contents.

default: None

### header_level: int  
Header level (depth) to render.  
h1→1, h2→2, ...

default: 3

### pickup_description_meta: bool  
The plugin renders the description after the h2 header in the table of contents markdown file. If you use metadata (front matter), there is no need to set this option.
```html
<mata name="description" content="pickup target value" />
```

default: False

### pickup_description_class: bool  
The plugin renders the description after the h2 header in the table of contents markdown file. If you use metadata (front matter), there is no need to set this option.

```md
# mkdocs-toc-md

<div class="toc-md-description">
pickup target value
</div>
```
default: False

### output_path: str  
Path to save rendered toc md file.  
index.md → docs/index.md

default: index.md

### output_log: bool  
Output contents of markdown file to console.

default: False

### ignore_page_pattern: str  
Regular expression pattern of markdown file names to be excluded from toc markdown file.  
To prevent the table of contents page from listing itself, set the same value as the output file name (output_path).

default: ''

### remove_navigation_page_pattern: str  
Regular expression pattern of markdown file names to remove navigation items.  
To hide the navigation on the table of contents page, set the same value as the output file name (output_path).

default: ''

### template_dir_path: str
Path of template dir.
Put `toc.md.j2` in your custom template dir.

default: ''

### beautiful_soup_parser: str
Parser used in BeautifulSoup. Default is html.parser.  
If using html5lib or lxml, you need to install additional dependencies.

default: html.parser

### integrate_mkdocs_static_i18n: bool
With [mkdocs-static-i18n](https://github.com/ultrabug/mkdocs-static-i18n)

default: False

### languages: dict
Use with integrate_mkdocs_static_i18n option.
Set toc_page_title, toc_page_description for each language.

```yml
languages:
    en:
        toc_page_title: Contents
        toc_page_description: Usage mkdocs-toc-md
    ja:
        toc_page_title: 目次
        toc_page_description: mkdocs-toc-mdプラグインの使い方
```

default: dict()

### shift_header: str (after_index, after_h1_of_index, none)
`after_index`  
    Shifts the header level(+1) except for the index file in the directory.

`after_h1_of_index`  
    Shifts the header level(+1) after h1 in index file and except for the index file in the directory.

`none` (default)

### extend_module: bool
Some processes can be extended by placing the toc_extend_module.py file in the docs folder.

```
├─ docs
│  ├─ mkdocs.yml
│  ├─ toc_extend_module.py
```

[Sample/toc_extend_module.py](./sample/toc_extend_module.py)


`find_src_elements` -> list[bs4.element.Tag]  
args

1. `bs_page_soup`: bs4.BeautifulSoup
1. `page`: mkdocs.structure.pages.Page
1. `toc_config`: mkdocs_toc_md.objects.TocConfig

`create_toc_items` -> list[mkdocs_toc_md.objects.TocItem]  
args

1. `page`: mkdocs.structure.pages.Page
1. `page_description`: str
1. `src_elements`: list[bs4.element.Tag]
1. `toc_config`: mkdocs_toc_md.objects.TocConfig

`on_create_toc_item`  
args

1. `toc_item`: mkdocs_toc_md.objects.TocItem
1. `src_element`: bs4.element.Tag
1. `page`: mkdocs.structure.pages.Page
1. `toc_config`: mkdocs_toc_md.objects.TocConfig

`on_before_output`  
args

1. `nav`: mkdocs.structure.nav.Navigation
1. `toc_items`: list[mkdocs_toc_md.objects.TocItem]
1. `toc_config`: mkdocs_toc_md.objects.TocConfig

### output_comment: str (html, metadata, none)

`html` (default)
```html
<!-- ====================== TOC ====================== -->
<!-- Generated by mkdocs-toc-md plugin -->
<!-- ================================================= -->
```

`metadata`
```
---
toc_output_comment: Generated by mkdocs-toc-md plugin
---
```
 
`none`