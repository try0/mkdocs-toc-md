# mkdocs-toc-md

[English](./README.md) | [Japanese](./README.ja.md)

[mkdocs-toc-md](https://pypi.org/project/mkdocs-toc-md/) is a MkDocs plugin that generates a table-of-contents Markdown file from your MkDocs navigation and page headings.

The generated Markdown file must be created before `mkdocs build` renders it as HTML. During local development, run `mkdocs serve` once to generate or update the Markdown output.

![](https://user-images.githubusercontent.com/17096601/199638378-892ddec9-b7af-4eb8-8ca8-a57c02980f53.png)

## Sample

- [Generated Markdown](https://github.com/try0/mkdocs-toc-md/blob/main/sample/docs/index.en.md?plain=1)
- [Sample site](https://try0.github.io/mkdocs-toc-md/sample/site/)

## Installation

```bash
pip install mkdocs-toc-md
```

## Basic Usage

Add the plugin to `mkdocs.yml`.

```yaml
plugins:
  - toc-md
```

Then run:

```bash
mkdocs serve
```

By default, the plugin generates `docs/index.md`.

## Add Descriptions

To show a description under a page heading, add `toc_md_description` to the page front matter.

```markdown
---
toc_md_description: Description shown in the generated TOC.
---
```

You can also extract descriptions from HTML metadata or an element with the `toc-md-description` class by enabling `pickup_description_meta` or `pickup_description_class`.

```html
<meta name="description" content="Description shown in the generated TOC." />
```

```markdown
<div class="toc-md-description">
Description shown in the generated TOC.
</div>
```

## Per-Page Front Matter

Some global options can be overridden per page through the page front matter.

```markdown
---
toc_md_ignore: true
toc_md_header_level: 2
---
```

- `toc_md_ignore`: when truthy, exclude this page from the generated TOC (per-page form of `ignore_page_pattern`).
- `toc_md_header_level`: heading depth to collect for this page only (per-page form of `header_level`). An invalid value falls back to the global `header_level`.

## Subdirectory Indexes

Set `subdir_index_depth` to generate `index.md` files under directories that contain pages listed in `nav`.

```yaml
plugins:
  - toc-md:
      subdir_index_depth: 1
      overwrite: generated
```

With this navigation:

```yaml
nav:
  - Guide:
      - Intro: guide/intro.md
      - Config: guide/advanced/config.md
```

`subdir_index_depth: 1` generates:

```text
docs/guide/index.md
```

The generated `guide/index.md` contains only the nav-backed pages under `guide/`, and links are written relative to `guide/index.md`.

To generate only subdirectory indexes and skip the root output file:

```yaml
plugins:
  - toc-md:
      output_root_index: false
      subdir_index_depth: 1
```

## Templates

The default template is `toc.md.j2`.

To use a custom template directory:

```yaml
plugins:
  - toc-md:
      template_dir_path: custom_template
```

For subdirectory indexes, template selection uses this order:

1. `toc.subdir.<parent-directory>.md.j2`
2. `toc.subdir.md.j2`
3. `toc.md.j2`

For example, `docs/admin/index.md` first looks for `toc.subdir.admin.md.j2`.

Subdirectory templates receive these additional values:

```text
data.is_subdir_index
data.directory_name
data.directory_path
data.directory_depth
```

## Full Configuration Example

```yaml
plugins:
  - toc-md:
      toc_page_title: Contents
      toc_page_description: Usage mkdocs-toc-md
      header_level: 3
      pickup_description_meta: false
      pickup_description_class: false
      output_path: index.md
      output_root_index: true
      subdir_index_depth: 0
      overwrite: always
      output_log: false
      ignore_page_pattern: index.*.md$
      remove_navigation_page_pattern: index.*.md$
      template_dir_path: custom_template
      beautiful_soup_parser: html.parser
      integrate_mkdocs_static_i18n: true
      languages:
        en:
          toc_page_title: Contents
          toc_page_description: Usage mkdocs-toc-md
        ja:
          toc_page_title: 目次
          toc_page_description: mkdocs-toc-md プラグインの使い方
      shift_header: after_h1_of_index
      extend_module: true
      output_comment: html
```

## Options

### `toc_page_title`: `str`

H1 text in the generated table-of-contents Markdown file.

Default: `Contents`

### `toc_page_description`: `str`

Description rendered below the H1 title.

Default: `None`

### `header_level`: `int`

Heading depth to collect. `1` collects `h1`, `2` collects `h1` through `h2`, and so on.

Can be overridden per page with the `toc_md_header_level` front matter key.

Default: `3`

### `pickup_description_meta`: `bool`

Read descriptions from `<meta name="description" content="..." />`.

Default: `False`

### `pickup_description_class`: `bool`

Read descriptions from an element with class `toc-md-description`.

Default: `False`

### `output_path`: `str`

Path to save the root generated Markdown file, relative to `docs_dir`.

Default: `index.md`

### `output_root_index`: `bool`

Generate the root TOC Markdown file configured by `output_path`. Set this to `false` when you only want subdirectory TOC files.

Default: `True`

### `subdir_index_depth`: `int`

Generate TOC Markdown files in subdirectories that contain pages listed in `nav`.

- `0`: disable subdirectory TOC files
- `1`: target directories directly under the docs root
- `2`: also target their child directories

Only directories backed by Markdown pages that appear in `nav` are considered.

Default: `0`

### `overwrite`: `str`

Controls how existing generated files are handled.

- `always`: always overwrite existing files
- `generated`: overwrite only when the existing file contains the mkdocs-toc-md generated marker
- `never`: never overwrite existing files

Default: `always`

When using `generated`, keep `output_comment` enabled or include the generated marker in your custom template.

### `output_log`: `bool`

Print generated Markdown to the console.

Default: `False`

### `ignore_page_pattern`: `str`

Regular expression for Markdown source paths to exclude from the generated TOC. To prevent the TOC page from listing itself, use a pattern that matches `output_path`.

A single page can also be excluded with the `toc_md_ignore: true` front matter key.

Default: `''`

### `remove_navigation_page_pattern`: `str`

Regular expression for Markdown source paths whose secondary page navigation should be removed from rendered HTML. To hide the navigation on the generated TOC page, use a pattern that matches `output_path`.

Default: `''`

### `template_dir_path`: `str`

Path to a directory containing `toc.md.j2`.

Subdirectory indexes also resolve templates from this directory. The lookup order is:

1. `toc.subdir.<parent-directory>.md.j2`
2. `toc.subdir.md.j2`
3. `toc.md.j2`

For example, `docs/admin/index.md` first looks for `toc.subdir.admin.md.j2`.

Default: `''`

### `beautiful_soup_parser`: `str`

Parser used by BeautifulSoup. If you use `html5lib` or `lxml`, install the additional dependency yourself.

Default: `html.parser`

### `integrate_mkdocs_static_i18n`: `bool`

Integrate with [mkdocs-static-i18n](https://github.com/ultrabug/mkdocs-static-i18n).

Default: `False`

### `languages`: `dict`

Per-language settings used with `integrate_mkdocs_static_i18n`.

```yaml
languages:
  en:
    toc_page_title: Contents
    toc_page_description: Usage mkdocs-toc-md
  ja:
    toc_page_title: 目次
    toc_page_description: mkdocs-toc-md プラグインの使い方
```

Default: `dict()`

### `shift_header`: `str`

Controls heading level shifts for index pages.

- `after_index`: shift heading levels by `+1` except for the index file in the directory
- `after_h1_of_index`: shift heading levels by `+1` after H1 in the index file, and for non-index files in the directory
- `none`: do not shift heading levels

Default: `none`

### `extend_module`: `bool`

Enable extension hooks by placing `toc_extend_module.py` in the MkDocs working directory.

```text
docs/
mkdocs.yml
toc_extend_module.py
```

See [sample/toc_extend_module.py](./sample/toc_extend_module.py).

Available hooks:

- `find_src_elements(bs_page_soup, page, toc_config) -> list[bs4.element.Tag]`
- `create_toc_items(page, page_description, src_elements, toc_config) -> list[mkdocs_toc_md.objects.TocItem]`
- `on_create_toc_item(toc_item, src_element, page, toc_config)`
- `on_before_output(nav, toc_items, toc_config)`

Default: `False`

### `output_comment`: `str`

Controls the generated marker comment.

`html`:

```html
<!-- ====================== TOC ====================== -->
<!-- Generated by mkdocs-toc-md plugin -->
<!-- ================================================= -->
```

`metadata`:

```yaml
---
toc_output_comment: Generated by mkdocs-toc-md plugin
---
```

`none`: no marker comment.

Default: `html`
