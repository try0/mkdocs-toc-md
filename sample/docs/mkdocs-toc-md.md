# mkdocs-toc-md

<div class="toc-md-description">
mkdocs-toc-md generates a table of contents page.
</div>

## Options



### toc_page_title: str  
h1 text in toc md.

### toc_page_description: str
Renders description after h1.

### pickup_description_meta: bool  
Renders description after h2.

### pickup_description_class: bool  
Renders description after h2.


```md
# mkdocs-toc-md

<div class="toc-md-description">
mkdocs-toc-md generates a table of contents page.
</div>
```



### output_path: str  
Path to save rendered toc md file.

### output_log: bool  
Output toc md contents to console.

### ignore_page_pattern: str  
Regular expression pattern of md filenames to be excluded from toc md files.  
To prevent the table of contents page from listing itself, set the same value as the output file name (output_path).

### remove_navigation_page_pattern: str  
Regular expression pattern of md filenames to remove navigation items.  
To hide the navigation on the table of contents page, set the same value as the output file name (output_path).

### template_dir_path: str
Path of template dir.
Put `toc.md.j2` in your custom template dir.

## Sample 

### mkdocs.yml

```yml
plugins:
  - toc-md:
      page_title: Contents
      page_description: Usage mkdocs-toc-md
      pickup_description_meta: true
      pickup_description_class: true
      output_path: index.md
      output_log: true
      ignore_page_pattern: index.md
      remove_navigation_page_pattern: index.md
      template_dir_path: custom_template
```


