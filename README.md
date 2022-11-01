# mkdocs-toc-md

mkdocs-toc-md is a mkdocs plugin that generates a table of contents as markdown. To render as html, the toc md file must be generated before the `mkdocs build`.



## Sample

[File](https://github.com/try0/mkdocs-toc-md/blob/main/sample/docs/index.md?plain=1)  
[Site](https://try0.github.io/mkdocs-toc-md/sample/site/)

## Usage
1. Install plugin.
    ```
    pip install mkdocs-toc-md
    ```
1. Add plugin conifg to mkdocs.yml.

    ```yml
    plugins:
      - toc-md:
          toc_page_title: Contents
          toc_page_description: Usage mkdocs-toc-md
          header_level: 3
          pickup_description_meta: true
          pickup_description_class: true
          output_path: index.md
          output_log: true
          ignore_page_pattern: index.md
          remove_navigation_page_pattern: index.md
          template_dir_path: custom_template
    ```

1. Run `mkdocs serve` to output toc md file.



## Options

* page_title: str  
h1 text in toc md.

* page_description: str  
Renders description after h1.

* header_level: int  
Header level (depth) to render.  
h1→1, h2→2, ...

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
  
  [sample](https://github.com/try0/mkdocs-toc-md/blob/main/sample/docs/index.md?plain=1#L14)

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

* template_dir_path: str  
Path of template dir.
Put `toc.md.j2` in your custom template dir.
