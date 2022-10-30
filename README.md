# mkdocs-toc-md

mkdocs-toc-md generates a table of contents page.

[Sample](https://github.com/try0/mkdocs-toc-md/blob/main/sample/docs/index.md?plain=1)

## Options

* page_title: str  
h1 text in toc md.

* pickup_description_meta: bool  
Renders description after h2 in toc md.

* pickup_description_class: bool  
Renders description after h2 in toc md.


  ```md
  # mkdocs-toc-md

  <div class="toc-md-description">
  mkdocs-toc-md generates a table of contents page.
  </div>
  ```
  
  [sample](https://github.com/try0/mkdocs-toc-md/blob/main/sample/docs/index.md?plain=1#L9)

* output_path: str  
Path to save rendered toc md file.

* output_log: bool  
Output toc md contents to console.

* ignore_page_pattern: str  
Regular expression pattern of md filenames to be excluded from toc md files.  
To prevent the table of contents page from listing itself, set the same value as the output file name (output_path).

* remove_navigation_page_pattern: str  
Regular expression pattern of md filenames to remove navigation items.  
To hide the navigation on the table of contents page, set the same value as the output file name (output_path).

