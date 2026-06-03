# mkdocs-toc-md

[English](./README.md) | [日本語](./README.ja.md)

[mkdocs-toc-md](https://pypi.org/project/mkdocs-toc-md/) は、MkDocs の `nav` と各ページの見出しから、目次用の Markdown ファイルを生成する MkDocs プラグインです。

生成された Markdown を HTML として表示するには、`mkdocs build` の前に Markdown ファイルが生成されている必要があります。ローカル開発では、`mkdocs serve` を一度実行すると生成・更新されます。

![](https://user-images.githubusercontent.com/17096601/199638378-892ddec9-b7af-4eb8-8ca8-a57c02980f53.png)

## サンプル

- [生成された Markdown](https://github.com/try0/mkdocs-toc-md/blob/main/sample/docs/index.ja.md?plain=1)
- [サンプルサイト](https://try0.github.io/mkdocs-toc-md/sample/site/)

## インストール

```bash
pip install mkdocs-toc-md
```

## 基本的な使い方

`mkdocs.yml` にプラグインを追加します。

```yaml
plugins:
  - toc-md
```

その後、次を実行します。

```bash
mkdocs serve
```

デフォルトでは `docs/index.md` が生成されます。

## 説明文を追加する

ページ見出しの下に説明文を表示したい場合は、ページの front matter に `toc_md_description` を追加します。

```markdown
---
toc_md_description: 生成された目次に表示する説明文
---
```

`pickup_description_meta` または `pickup_description_class` を有効にすると、HTMLメタデータや `toc-md-description` クラスの要素から説明文を取得できます。

```html
<meta name="description" content="生成された目次に表示する説明文" />
```

```markdown
<div class="toc-md-description">
生成された目次に表示する説明文
</div>
```

## サブディレクトリの index 生成

`subdir_index_depth` を設定すると、`nav` に含まれるページの親ディレクトリに `index.md` を生成できます。

```yaml
plugins:
  - toc-md:
      subdir_index_depth: 1
      overwrite: generated
```

たとえば次の `nav` がある場合:

```yaml
nav:
  - Guide:
      - Intro: guide/intro.md
      - Config: guide/advanced/config.md
```

`subdir_index_depth: 1` では次が生成されます。

```text
docs/guide/index.md
```

生成された `guide/index.md` には、`guide/` 配下にあり、かつ `nav` に含まれるページだけが出力されます。リンクは `guide/index.md` から見た相対パスになります。

ルートの `index.md` を生成せず、サブディレクトリだけ生成したい場合は次のようにします。

```yaml
plugins:
  - toc-md:
      output_root_index: false
      subdir_index_depth: 1
```

## テンプレート

デフォルトテンプレートは `toc.md.j2` です。

カスタムテンプレートディレクトリを使う場合:

```yaml
plugins:
  - toc-md:
      template_dir_path: custom_template
```

サブディレクトリ用 `index.md` のテンプレートは、次の順で選択されます。

1. `toc.subdir.<親ディレクトリ名>.md.j2`
2. `toc.subdir.md.j2`
3. `toc.md.j2`

たとえば `docs/admin/index.md` では、最初に `toc.subdir.admin.md.j2` を探します。

サブディレクトリ用テンプレートには、追加で次の値が渡されます。

```text
data.is_subdir_index
data.directory_name
data.directory_path
data.directory_depth
```

## 設定例

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

## オプション

### `toc_page_title`: `str`

生成される目次 Markdown の H1 テキストです。

デフォルト: `Contents`

### `toc_page_description`: `str`

H1 タイトルの下に表示される説明文です。

デフォルト: `None`

### `header_level`: `int`

収集する見出しの深さです。`1` は `h1`、`2` は `h1` から `h2`、という形で収集します。

デフォルト: `3`

### `pickup_description_meta`: `bool`

`<meta name="description" content="..." />` から説明文を取得します。

デフォルト: `False`

### `pickup_description_class`: `bool`

`toc-md-description` クラスを持つ要素から説明文を取得します。

デフォルト: `False`

### `output_path`: `str`

ルートの生成 Markdown ファイルの保存先です。`docs_dir` からの相対パスで指定します。

デフォルト: `index.md`

### `output_root_index`: `bool`

`output_path` で指定したルートの目次 Markdown を生成するかどうかを指定します。サブディレクトリ用の目次だけを生成したい場合は `false` にします。

デフォルト: `True`

### `subdir_index_depth`: `int`

`nav` に含まれるページの親ディレクトリに、目次 Markdown を生成します。

- `0`: サブディレクトリ用の目次を生成しない
- `1`: docs ルート直下のディレクトリを対象にする
- `2`: その子ディレクトリも対象にする

ファイルシステム上に存在するだけのディレクトリや、`nav` に含まれないページは対象外です。

デフォルト: `0`

### `overwrite`: `str`

既存ファイルの扱いを指定します。

- `always`: 既存ファイルを常に上書きする
- `generated`: mkdocs-toc-md の生成マーカーがある場合だけ上書きする
- `never`: 既存ファイルを上書きしない

デフォルト: `always`

`generated` を使う場合は、`output_comment` を有効にするか、カスタムテンプレートに生成マーカーを含めてください。

### `output_log`: `bool`

生成された Markdown をコンソールに出力します。

デフォルト: `False`

### `ignore_page_pattern`: `str`

生成される目次から除外する Markdown ソースパスの正規表現です。目次ページ自身を載せたくない場合は、`output_path` に一致するパターンを指定します。

デフォルト: `''`

### `remove_navigation_page_pattern`: `str`

レンダリング済みHTMLから、セカンダリナビゲーションを削除する Markdown ソースパスの正規表現です。生成された目次ページのナビゲーションを隠したい場合は、`output_path` に一致するパターンを指定します。

デフォルト: `''`

### `template_dir_path`: `str`

`toc.md.j2` を置いたテンプレートディレクトリのパスです。

サブディレクトリ用の `index.md` も、このディレクトリ内のテンプレートから解決されます。解決順は次の通りです。

1. `toc.subdir.<親ディレクトリ名>.md.j2`
2. `toc.subdir.md.j2`
3. `toc.md.j2`

たとえば `docs/admin/index.md` では、最初に `toc.subdir.admin.md.j2` を探します。

デフォルト: `''`

### `beautiful_soup_parser`: `str`

BeautifulSoup で使用するパーサーです。`html5lib` や `lxml` を使う場合は、追加の依存関係を別途インストールしてください。

デフォルト: `html.parser`

### `integrate_mkdocs_static_i18n`: `bool`

[mkdocs-static-i18n](https://github.com/ultrabug/mkdocs-static-i18n) と連携します。

デフォルト: `False`

### `languages`: `dict`

`integrate_mkdocs_static_i18n` と一緒に使う、言語ごとの設定です。

```yaml
languages:
  en:
    toc_page_title: Contents
    toc_page_description: Usage mkdocs-toc-md
  ja:
    toc_page_title: 目次
    toc_page_description: mkdocs-toc-md プラグインの使い方
```

デフォルト: `dict()`

### `shift_header`: `str`

index ページ周辺の見出しレベル調整を指定します。

- `after_index`: ディレクトリ内の index ファイル以外の見出しレベルを `+1` する
- `after_h1_of_index`: index ファイル内の H1 より後、かつディレクトリ内の index ファイル以外の見出しレベルを `+1` する
- `none`: 見出しレベルを調整しない

デフォルト: `none`

### `extend_module`: `bool`

MkDocs の作業ディレクトリに `toc_extend_module.py` を配置すると、処理を拡張できます。

```text
docs/
mkdocs.yml
toc_extend_module.py
```

[sample/toc_extend_module.py](./sample/toc_extend_module.py) も参照してください。

利用できるフック:

- `find_src_elements(bs_page_soup, page, toc_config) -> list[bs4.element.Tag]`
- `create_toc_items(page, page_description, src_elements, toc_config) -> list[mkdocs_toc_md.objects.TocItem]`
- `on_create_toc_item(toc_item, src_element, page, toc_config)`
- `on_before_output(nav, toc_items, toc_config)`

デフォルト: `False`

### `output_comment`: `str`

生成マーカーコメントの形式を指定します。

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

`none`: マーカーコメントを出力しません。

デフォルト: `html`
