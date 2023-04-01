
# mkdocs-toc-md

[mkdocs-toc-md](https://pypi.org/project/mkdocs-toc-md/) is a plugin for mkdocs that generates a table of contents in markdown format. To render the table of contents as HTML, the markdown file must be generated before running `mkdocs build`.

![](https://user-images.githubusercontent.com/17096601/199638378-892ddec9-b7af-4eb8-8ca8-a57c02980f53.png)



## Sample

[File](https://github.com/try0/mkdocs-toc-md/blob/main/sample/docs/index.md?plain=1)  
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

```yml
plugins:
    - toc-md:
        toc_page_title: Contents
        toc_page_description: Usage mkdocs-toc-md
        header_level: 3
        pickup_description_meta: false
        pickup_description_class: false
        output_path: index.md
        output_log: true
        ignore_page_pattern: index.md
        remove_navigation_page_pattern: index.md
        template_dir_path: custom_template
```

### toc_page_title: str  
h1 text in the table of contents markdown file.

### toc_page_description: str
The description will be rendered below the h1 tag in the table of contents.

### header_level: int  
Header level (depth) to render.  
h1→1, h2→2, ...

### pickup_description_meta: bool  
The plugin renders the description after the h2 header in the table of contents markdown file. If you use metadata (front matter), there is no need to set this option.
```html
<mata name="description" content="pickup target value" />
```

### pickup_description_class: bool  
The plugin renders the description after the h2 header in the table of contents markdown file. If you use metadata (front matter), there is no need to set this option.

```md
# mkdocs-toc-md

<div class="toc-md-description">
pickup target value
</div>
```

### output_path: str  
Path to save rendered toc md file.  
index.md → docs/index.md

### output_log: bool  
Output contents of markdown file to console.

### ignore_page_pattern: str  
Regular expression pattern of markdown file names to be excluded from toc markdown file.  
To prevent the table of contents page from listing itself, set the same value as the output file name (output_path).

### remove_navigation_page_pattern: str  
Regular expression pattern of markdown file names to remove navigation items.  
To hide the navigation on the table of contents page, set the same value as the output file name (output_path).

### template_dir_path: str
Path of template dir.
Put `toc.md.j2` in your custom template dir.

### beautiful_soup_parser: str
Parser used in BeautifulSoup. Default is html.parser.  
If using html5lib or lxml, you need to install additional dependencies.
