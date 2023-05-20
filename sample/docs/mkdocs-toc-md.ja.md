---
toc_md_description: mkdocs-toc-md プラグインの使い方を説明します。
---

# mkdocs-toc-md

mkdocs-toc-md は、目次マークダウンを生成するプラグインです。
HTMLとして出力するためには、`mkdocs build`コマンド実行前に`mkdocs serve`等で出力しておいてください。

[PyPI](https://pypi.org/project/mkdocs-toc-md/)

## サンプル


[File](https://github.com/try0/mkdocs-toc-md/blob/main/sample/docs/index.md?plain=1)  
[Site](https://try0.github.io/mkdocs-toc-md/sample/site/)




## 使い方


### 目次マークダウンを出力する


1. プラグインをインストールしてください。 
    ```
    pip install mkdocs-toc-md
    ```
1. mkdocs.yml.へ設定を追加してください。

    ```yml
    plugins:
        - toc-md:
            toc_page_title: Contents
            toc_page_description: Usage mkdocs-toc-md
            header_level: 6
            pickup_description_meta: true
            pickup_description_class: true
            output_path: index.md
            output_log: false
            ignore_page_pattern: index.*.md
            remove_navigation_page_pattern: index.*.md
            template_dir_path: custom_template
            integrate_mkdocs_static_i18n: true
            languages:
                en:
                    toc_page_title: Contents
                    toc_page_description: Usage mkdocs-toc-md
                ja:
                    toc_page_title: 目次
                    toc_page_description: mkdocs-toc-mdプラグインの使い方
    ```

1. `mkdocs serve`を実行して、マークダウンファイルを出力してください。


### 概要説明を追加する

メタデータを使用して概要説明テキストが指定できます。`toc_md_description`をキーとして、指定してください。

```
---
toc_md_description: このプラグインについて説明します。
---
```

また、次のオプションでも指定可能です。 `pickup_description_meta` `pickup_description_class`



## オプション


### toc_page_title: str  
目次マークダウンのタイトルです。  
h1

### toc_page_description: str
概要説明です。タイトルの次に出力されます。  

### header_level: int  
目次へ出力する、各ページの項目ヘッダーレベルです。  
h1→1, h2→2, ...

### pickup_description_meta: bool  
メタタグで指定された概要説明を目次へ出力します。  
マークダウンのメタデータで指定する場合、falseにしてください。
```html
<mata name="description" content="pickup target value" />
```

### pickup_description_class: bool  
クラス属性で指定された概要説明を目次へ出力します。  
マークダウンのメタデータで指定する場合、falseにしてください。

```md
# mkdocs-toc-md

<div class="toc-md-description">
pickup target value
</div>
```

### output_path: str  
ファイル名。docs配下へ出力されます。  
index.md → docs/index.md

### output_log: bool  
目次要素をログへ出力します。

### ignore_page_pattern: str  
目次から除外するファイルの正規表現です。  
出力した目次ファイル自身が目次の要素として出力されないようにするためには、同一のファイル名を指定します。

### remove_navigation_page_pattern: str  
ナビゲーションメニューを削除するファイルの正規表現です。  
出力した目次ファイルからナビゲーションメニューを削除するには、同一のファイル名を指定します。

### template_dir_path: str
テンプレートフォルダーパス。  
`toc.md.j2`を指定したフォルダーに配置してください。

### beautiful_soup_parser: str
BeautifulSoupのパーサーを指定します。デフォルトは、`html.parser`です。
html5lib lxmlを使用する場合、個別にインストールが必要です。

### integrate_mkdocs_static_i18n: bool
[mkdocs-static-i18n](https://github.com/ultrabug/mkdocs-static-i18n)に対応します。

### languages: dict
integrate_mkdocs_static_i18n オプションと一緒に使用します。  
toc_page_title, toc_page_descriptionを各言語ごとに指定できます。

```yml
languages:
    en:
        toc_page_title: Contents
        toc_page_description: Usage mkdocs-toc-md
    ja:
        toc_page_title: 目次
        toc_page_description: mkdocs-toc-mdプラグインの使い方
```