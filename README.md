# mkdocs-toc-md

mkdocs-toc-md generates a table of contents page.


## Options

* pickup_description_meta: bool  
Renders description after h1.

* pickup_description_class: bool  
Renders description after h1.


```md
# in md file
<div class="toc-md-description">
Description of this file. 
</div>
```

* output_path: str  
Path to save rendered toc md file.

* output_log: bool  
Output to console toc md contents.

* ignore_page_pattern: str  
Regular expression pattern of md filenames to be excluded from toc md files.

* remove_navigation_page_pattern: str  
Regular expression pattern of md filenames to remove navigation items.
