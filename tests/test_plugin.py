import logging
import re
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from jinja2 import Environment, FileSystemLoader

from mkdocs_toc_md.objects import TocItem
from mkdocs_toc_md.objects import TocConfig
from mkdocs_toc_md.plugin import TocMdPlugin


class DisabledHook:
    def can_call(self, name):
        return False


class RecordingHook:
    def __init__(self, methods):
        self.methods = set(methods)
        self.calls = []

    def can_call(self, name):
        return name in self.methods

    def find_src_elements(self, soup, page):
        self.calls.append(("find_src_elements", page.file.src_path))
        return soup.find_all("strong")

    def create_toc_items(self, page, description, elements):
        self.calls.append(
            ("create_toc_items", description, [element.text for element in elements])
        )
        item = TocItem()
        item.text = elements[0].text
        item.url = page.file.src_path + "#custom"
        return [item]

    def on_create_toc_item(self, item, element, page):
        self.calls.append(("on_create_toc_item", element.text))
        item.text = "Hooked " + item.text

    def on_before_output(self, nav, toc_headers):
        self.calls.append(("on_before_output", len(toc_headers)))


def make_page(src_path, content="", meta=None):
    return SimpleNamespace(
        is_link=False,
        is_page=True,
        is_section=False,
        file=SimpleNamespace(src_path=src_path),
        content=content,
        meta={} if meta is None else meta,
    )


def make_section(*children):
    return SimpleNamespace(
        is_link=False,
        is_page=False,
        is_section=True,
        children=list(children),
    )


def make_link():
    return SimpleNamespace(
        is_link=True,
        is_page=False,
        is_section=False,
    )


def make_config(**overrides):
    config = {
        "pickup_description_meta": False,
        "pickup_description_class": False,
        "output_path": "index.md",
        "output_root_index": True,
        "subdir_index_depth": 0,
        "overwrite": "always",
        "output_log": False,
        "ignore_page_pattern": "",
        "remove_navigation_page_pattern": "",
        "toc_page_title": "Contents",
        "toc_page_description": None,
        "header_level": 3,
        "template_dir_path": None,
        "beautiful_soup_parser": "html.parser",
        "languages": {},
        "integrate_mkdocs_static_i18n": False,
        "extend_module": False,
        "shift_header": "none",
        "output_comment": "html",
    }
    config.update(overrides)
    return config


def make_plugin(**config_overrides):
    plugin = TocMdPlugin()
    plugin.config = make_config(**config_overrides)
    plugin.ignore_re = None
    plugin.hook = DisabledHook()
    plugin.toc_output_comment = TocConfig(
        {}, plugin.config
    ).get_output_comment()
    return plugin


class HeaderSelectionTests(unittest.TestCase):
    def test_get_header_names_uses_global_and_page_specific_levels(self):
        # パラメーター: 全体の見出し階層を3、ページ個別の見出し階層を2に設定する。
        plugin = make_plugin(header_level=3)
        page = make_page("guide.md", meta={"toc_md_header_level": "2"})

        # チェック内容: 通常はh1～h3、ページ指定時はh1～h2が対象になる。
        self.assertEqual(["h1", "h2", "h3"], plugin.get_header_names())
        self.assertEqual(["h1", "h2"], plugin.get_header_names(page))

    def test_invalid_page_header_level_falls_back_to_global_value(self):
        # パラメーター: 全体の見出し階層を2、ページ個別の値を不正な文字列にする。
        plugin = make_plugin(header_level=2)
        page = make_page(
            "guide.md", meta={"toc_md_header_level": "invalid"}
        )

        with self.assertLogs("mkdocs.toc-md", logging.WARNING) as logs:
            header_names = plugin.get_header_names(page)

        # チェック内容: 全体設定へフォールバックし、対象ページを含む警告を出力する。
        self.assertEqual(["h1", "h2"], header_names)
        self.assertIn("guide.md", "\n".join(logs.output))


class TocItemCreationTests(unittest.TestCase):
    def test_create_toc_items_extracts_headings_urls_and_descriptions(self):
        # パラメーター: meta要素、専用クラス、front matterからの説明文取得を有効にする。
        plugin = make_plugin(
            pickup_description_meta=True,
            pickup_description_class=True,
        )
        page = make_page(
            "guide/page.md",
            content=(
                '<meta name="description" content="Meta.">'
                '<p class="toc-md-description">Class.</p>'
                '<h1 id="intro">Introduction'
                '<a class="headerlink">¶</a></h1>'
                '<h2 id="details">Details</h2>'
            ),
            meta={"toc_md_description": "Front matter."},
        )
        toc_items = []

        plugin.create_toc_items(
            toc_items, page, {}, "", nav_item_depth=1
        )

        # チェック内容: 見出し名、URL、階層、結合された説明文が正しく生成される。
        self.assertEqual(2, len(toc_items))
        self.assertEqual("Introduction", toc_items[0].text)
        self.assertEqual("guide/page.md#intro", toc_items[0].url)
        self.assertEqual(1, toc_items[0].src_level)
        self.assertEqual(2, toc_items[0].level)
        self.assertEqual(
            "Meta.Class.Front matter.", toc_items[0].description
        )
        self.assertEqual("Details", toc_items[1].text)
        self.assertEqual(3, toc_items[1].level)
        self.assertIsNone(toc_items[1].description)

    def test_page_specific_header_level_limits_collected_headings(self):
        # パラメーター: 全体ではh3まで、対象ページだけh1まで収集するよう設定する。
        plugin = make_plugin(header_level=3)
        page = make_page(
            "guide.md",
            content='<h1 id="one">One</h1><h2 id="two">Two</h2>',
            meta={"toc_md_header_level": 1},
        )
        toc_items = []

        plugin.create_toc_items(
            toc_items, page, {}, "", nav_item_depth=1
        )

        # チェック内容: ページ個別設定が優先され、h1だけが目次に追加される。
        self.assertEqual(["One"], [item.text for item in toc_items])

    def test_ignored_pages_links_and_output_page_are_skipped(self):
        # パラメーター: 除外正規表現、toc_md_ignore、出力先index.mdをそれぞれ指定する。
        plugin = make_plugin()
        plugin.ignore_re = re.compile(r"ignored/")
        toc_items = []

        pages = [
            make_link(),
            make_page(
                "front-matter.md",
                '<h1 id="ignored">Ignored</h1>',
                {"toc_md_ignore": True},
            ),
            make_page("ignored/page.md", '<h1 id="ignored">Ignored</h1>'),
            make_page("index.md", '<h1 id="self">Self</h1>'),
        ]
        for page in pages:
            plugin.create_toc_items(
                toc_items,
                page,
                {},
                "",
                nav_item_depth=1,
                output_src_path="index.md",
            )

        # チェック内容: 外部リンクと各条件に該当するページがすべて除外される。
        self.assertEqual([], toc_items)

    def test_section_depth_and_index_header_shift_are_applied(self):
        # パラメーター: セクション内のindex.mdにshift_header=after_h1を適用する。
        plugin = make_plugin(shift_header="after_h1")
        page = make_page(
            "guide/index.md",
            '<h1 id="guide">Guide</h1><h2 id="start">Start</h2>',
        )
        toc_items = []

        plugin.create_toc_items(
            toc_items,
            make_section(page),
            {},
            "",
            nav_item_depth=1,
        )

        # チェック内容: セクション階層の加算後、indexページ分が1段戻される。
        self.assertEqual([2, 3], [item.level for item in toc_items])

    def test_target_directory_filters_pages_and_makes_urls_relative(self):
        # パラメーター: 出力対象ディレクトリをguideに限定し、内外のページを渡す。
        plugin = make_plugin()
        toc_items = []
        pages = [
            make_page("guide/page.md", '<h1 id="inside">Inside</h1>'),
            make_page("other/page.md", '<h1 id="outside">Outside</h1>'),
        ]

        for page in pages:
            plugin.create_toc_items(
                toc_items,
                page,
                {},
                "",
                nav_item_depth=1,
                target_dir="guide",
            )

        # チェック内容: guide配下だけが残り、URLがguideからの相対パスになる。
        self.assertEqual(["Inside"], [item.text for item in toc_items])
        self.assertEqual("page.md#inside", toc_items[0].url)

    def test_headings_without_ids_and_all_supported_levels_are_handled(self):
        # パラメーター: h1～h6を収集し、h3だけidなし、shift_headerをindexのh1限定にする。
        plugin = make_plugin(
            header_level=6,
            shift_header="after_h1_of_index",
        )
        page = make_page(
            "guide/index.md",
            "".join(
                "<h{level}{id_attribute}>H{level}</h{level}>".format(
                    level=level,
                    id_attribute=(
                        "" if level == 3 else f' id="h{level}"'
                    ),
                )
                for level in range(1, 7)
            ),
        )
        toc_items = []

        with self.assertLogs("mkdocs.toc-md", logging.WARNING) as logs:
            plugin.create_toc_items(
                toc_items, page, {}, "", nav_item_depth=1
            )

        # チェック内容: 全階層が設定され、h1だけシフトし、idなし見出しはページURLになる。
        self.assertEqual([1, 2, 3, 4, 5, 6], [item.src_level for item in toc_items])
        self.assertEqual([1, 3, 4, 5, 6, 7], [item.level for item in toc_items])
        self.assertEqual("guide/index.md", toc_items[2].url)
        self.assertIn("no id attribute", "\n".join(logs.output))

    def test_extend_module_can_replace_elements_and_created_items(self):
        # パラメーター: 要素検索と目次項目生成を拡張フックへ委譲する。
        plugin = make_plugin(extend_module=True)
        plugin.hook = RecordingHook(
            {"find_src_elements", "create_toc_items"}
        )
        page = make_page(
            "guide/page.md",
            "<h1>Default</h1><strong>Custom</strong>",
            {"toc_md_description": "Description"},
        )
        toc_items = []

        plugin.create_toc_items(
            toc_items,
            page,
            {},
            "",
            nav_item_depth=1,
            target_dir="guide",
        )

        # チェック内容: フックが選んだ要素と項目だけが使われ、URLも相対化される。
        self.assertEqual(["Custom"], [item.text for item in toc_items])
        self.assertEqual("page.md#custom", toc_items[0].url)
        self.assertEqual(
            [
                ("find_src_elements", "guide/page.md"),
                ("create_toc_items", "Description", ["Custom"]),
            ],
            plugin.hook.calls,
        )

    def test_extend_module_can_modify_each_default_toc_item(self):
        # パラメーター: 標準生成を維持し、項目生成後のフックだけを有効にする。
        plugin = make_plugin(extend_module=True)
        plugin.hook = RecordingHook({"on_create_toc_item"})
        page = make_page("guide.md", '<h1 id="guide">Guide</h1>')
        toc_items = []

        plugin.create_toc_items(
            toc_items, page, {}, "", nav_item_depth=1
        )

        # チェック内容: 標準項目に対してフックによる変更が反映される。
        self.assertEqual("Hooked Guide", toc_items[0].text)
        self.assertEqual(
            [("on_create_toc_item", "Guide")], plugin.hook.calls
        )


class NavigationAndPathTests(unittest.TestCase):
    def test_collect_subdir_index_dirs_respects_order_and_depth(self):
        # パラメーター: 最大深度2で、Markdown・画像・リンクを含むナビを渡す。
        plugin = make_plugin()
        nav = SimpleNamespace(
            items=[
                make_section(
                    make_page("guide/start.md"),
                    make_page("guide/deep/topic.md"),
                ),
                make_page("api/reference.md"),
                make_page("assets/logo.png"),
                make_link(),
            ]
        )

        # チェック内容: Markdownページの親だけが、登場順かつ深度2まで収集される。
        self.assertEqual(
            ["guide", "guide/deep", "api"],
            plugin.collect_subdir_index_dirs(nav, max_depth=2),
        )

    def test_path_helpers_normalize_join_and_relativize(self):
        # パラメーター: Windows区切り、前後の区切り、フラグメント付きURLを渡す。
        plugin = make_plugin()

        # チェック内容: 正規化、結合、配下判定、相対化、深度計算が正しく行われる。
        self.assertEqual(
            "guide/page.md", plugin.normalize_src_path(r"\guide\page.md")
        )
        self.assertEqual(
            "guide/deep/index.md",
            plugin.join_src_path("/guide/", r"\deep", "index.md"),
        )
        self.assertTrue(
            plugin.is_under_directory("guide/deep/page.md", "guide")
        )
        self.assertFalse(
            plugin.is_under_directory("guidebook/page.md", "guide")
        )
        self.assertEqual(
            "../api/page.md#method",
            plugin.to_relative_url("api/page.md#method", "guide"),
        )
        self.assertEqual(2, plugin.get_directory_depth("guide/deep"))

    def test_subdirectory_template_candidates_prefer_specific_templates(self):
        # パラメーター: サブディレクトリdocs/guideとルートの両方を指定する。
        plugin = make_plugin()

        # チェック内容: 専用、サブディレクトリ共通、標準の順で候補が並ぶ。
        self.assertEqual(
            [
                "toc.subdir.guide.md.j2",
                "toc.subdir.md.j2",
                "toc.md.j2",
            ],
            plugin.get_template_name_candidates("docs/guide"),
        )
        self.assertEqual(
            ["toc.md.j2"], plugin.get_template_name_candidates()
        )


class OutputTests(unittest.TestCase):
    def test_can_overwrite_honors_each_policy(self):
        # パラメーター: overwriteをalways、never、generatedへ順に切り替える。
        plugin = make_plugin(overwrite="always")

        # チェック内容: alwaysは許可、neverは拒否、generatedは生成印の有無で判定する。
        self.assertTrue(plugin.can_overwrite("manual", "index.md"))

        plugin.config["overwrite"] = "never"
        self.assertFalse(plugin.can_overwrite("generated", "index.md"))

        plugin.config["overwrite"] = "generated"
        self.assertFalse(plugin.can_overwrite("manual", "index.md"))
        self.assertTrue(
            plugin.can_overwrite(
                "<!-- Generated by mkdocs-toc-md plugin -->", "index.md"
            )
        )

    def test_output_generates_root_and_subdirectory_indexes(self):
        # パラメーター: subdir_index_depth=1でルート、guide配下、ルート直下のページを渡す。
        plugin = make_plugin(subdir_index_depth=1)
        nav = SimpleNamespace(
            items=[
                make_page(
                    "guide/index.md", '<h1 id="guide">Guide</h1>'
                ),
                make_page(
                    "guide/setup.md", '<h1 id="setup">Setup</h1>'
                ),
                make_page("about.md", '<h1 id="about">About</h1>'),
            ]
        )

        with tempfile.TemporaryDirectory() as docs_dir:
            plugin.output({"docs_dir": docs_dir}, nav, "", "")

            root_output = Path(docs_dir, "index.md").read_text(
                encoding="utf-8"
            )
            subdir_output = Path(docs_dir, "guide", "index.md").read_text(
                encoding="utf-8"
            )

        # チェック内容: ルートとguideに目次が生成され、リンク範囲と相対URLが正しい。
        self.assertIn("# Contents", root_output)
        self.assertIn("[Guide](guide/index.md#guide)", root_output)
        self.assertIn("[Setup](guide/setup.md#setup)", root_output)
        self.assertIn("# guide", subdir_output)
        self.assertNotIn("[Guide]", subdir_output)
        self.assertIn("[Setup](setup.md#setup)", subdir_output)
        self.assertNotIn("[About]", subdir_output)

    def test_post_page_removes_only_matching_secondary_navigation(self):
        # パラメーター: hidden.mdだけに一致するナビゲーション除外パターンを指定する。
        plugin = make_plugin(
            remove_navigation_page_pattern=r"hidden\.md"
        )
        html = (
            '<nav class="md-nav md-nav--secondary">TOC</nav>'
            '<nav class="md-nav">Main</nav>'
        )

        result = plugin.on_post_page(
            html, make_page("hidden.md"), {}
        )

        # チェック内容: 対象ページの副ナビだけを削除し、通常ナビと非対象ページは維持する。
        self.assertNotIn("TOC", result)
        self.assertIn("Main", result)
        self.assertEqual(
            html, plugin.on_post_page(html, make_page("visible.md"), {})
        )

    def test_existing_file_is_preserved_or_replaced_according_to_policy(self):
        # パラメーター: 既存ファイルに対しneverとgeneratedの上書き方針を適用する。
        plugin = make_plugin(overwrite="never")
        nav = SimpleNamespace(
            items=[make_page("guide.md", '<h1 id="guide">Guide</h1>')]
        )

        with tempfile.TemporaryDirectory() as docs_dir:
            output_path = Path(docs_dir, "index.md")
            output_path.write_text("Manual content", encoding="utf-8")

            plugin.output({"docs_dir": docs_dir}, nav, "", "")
            preserved_content = output_path.read_text(encoding="utf-8")

            plugin.config["overwrite"] = "generated"
            output_path.write_text(
                "<!-- Generated by mkdocs-toc-md plugin -->\nOld content",
                encoding="utf-8",
            )
            plugin.output({"docs_dir": docs_dir}, nav, "", "")
            replaced_content = output_path.read_text(encoding="utf-8")

        # チェック内容: neverでは手書きを維持し、generatedでは生成印付き内容を更新する。
        self.assertEqual("Manual content", preserved_content)
        self.assertIn("[Guide](guide.md#guide)", replaced_content)
        self.assertNotIn("Old content", replaced_content)

    def test_unchanged_existing_file_is_not_rewritten(self):
        # パラメーター: 一度生成した目次へ、同じ入力でもう一度出力する。
        plugin = make_plugin()
        nav = SimpleNamespace(
            items=[make_page("guide.md", '<h1 id="guide">Guide</h1>')]
        )

        with tempfile.TemporaryDirectory() as docs_dir:
            plugin.output({"docs_dir": docs_dir}, nav, "", "")
            output_path = Path(docs_dir, "index.md")
            before_stat = output_path.stat()

            with self.assertLogs("mkdocs.toc-md", logging.INFO) as logs:
                plugin.output({"docs_dir": docs_dir}, nav, "", "")
            after_stat = output_path.stat()

        # チェック内容: 内容が同じ場合は書き直さず、変更なしのログを出力する。
        self.assertEqual(before_stat.st_mtime_ns, after_stat.st_mtime_ns)
        self.assertIn("No changes", "\n".join(logs.output))

    def test_custom_template_and_language_specific_text_are_used(self):
        # パラメーター: カスタムテンプレートと言語別タイトル・説明文を指定する。
        with tempfile.TemporaryDirectory() as template_dir:
            Path(template_dir, "toc.md.j2").write_text(
                "{{ data.page_title }}|{{ data.page_description }}",
                encoding="utf-8",
            )
            plugin = make_plugin(
                template_dir_path=template_dir,
                languages={
                    "ja": {
                        "toc_page_title": "目次",
                        "toc_page_description": "日本語の説明",
                    }
                },
            )
            nav = SimpleNamespace(items=[])

            with tempfile.TemporaryDirectory() as docs_dir:
                plugin.output({"docs_dir": docs_dir}, nav, "ja", "")
                output = Path(docs_dir, "index.ja.md").read_text(
                    encoding="utf-8"
                )

        # チェック内容: 標準テンプレートではなく、言語別文言を渡した独自テンプレートを使う。
        self.assertEqual("目次|日本語の説明", output)

    def test_subdirectory_template_falls_back_to_default_template(self):
        # パラメーター: サブディレクトリ専用テンプレートが存在しない環境を作る。
        plugin = make_plugin()
        environment = Environment(
            loader=FileSystemLoader(plugin.get_template_paths())
        )

        template = plugin.get_template(environment, "guide")

        # チェック内容: サブディレクトリ用候補がない場合は標準テンプレートを取得する。
        self.assertEqual(
            plugin.TEMPLATE_NAME,
            template.name,
        )


class EventLifecycleTests(unittest.TestCase):
    def test_pre_build_and_nav_initialize_runtime_state(self):
        # パラメーター: i18n連携を有効にし、pluginsにi18nプラグインを渡す。
        plugin = TocMdPlugin()
        plugin.config = make_config(integrate_mkdocs_static_i18n=True)
        i18n_plugin = SimpleNamespace()
        config = {"plugins": {"i18n": i18n_plugin}}
        nav = SimpleNamespace(items=[])

        with patch(
            "mkdocs_toc_md.plugin.TocExtendModule"
        ) as extend_module:
            plugin.on_pre_build(config)
            plugin.on_nav(nav, config, [])

        # チェック内容: 設定、出力コメント、i18n、拡張フック、ナビが保持される。
        self.assertIs(config, plugin.toc_config.mkdocs_config)
        self.assertIn(
            TocMdPlugin.GENERATED_MARKER_TEXT,
            plugin.toc_output_comment,
        )
        self.assertIs(i18n_plugin, plugin.i18n_plugin)
        extend_module.assert_called_once_with(plugin.toc_config)
        self.assertIs(nav, plugin.nav)

    def test_post_build_outputs_default_and_both_i18n_layouts(self):
        # パラメーター: 通常ナビ、folder型i18n、suffix型i18nを順に設定する。
        plugin = make_plugin(ignore_page_pattern=r"draft/")
        plugin.nav = SimpleNamespace(items=[])
        plugin.i18n_plugin = None
        plugin.output = Mock()

        plugin.on_post_build({"docs_dir": "docs"})

        folder_nav = SimpleNamespace(items=[])
        suffix_nav = SimpleNamespace(items=[])
        plugin.i18n_plugin = SimpleNamespace(
            i18n_navs={"ja": folder_nav},
            config={"docs_structure": "folder"},
        )
        plugin.on_post_build({"docs_dir": "docs"})
        plugin.i18n_plugin = SimpleNamespace(
            i18n_navs={"en": suffix_nav},
            config={"docs_structure": "suffix"},
        )
        plugin.on_post_build({"docs_dir": "docs"})

        # チェック内容: 除外正規表現を準備し、各レイアウトに正しい言語・フォルダを渡す。
        self.assertIsNotNone(plugin.ignore_re.match("draft/page.md"))
        self.assertEqual(
            [
                unittest.mock.call(
                    {"docs_dir": "docs"}, plugin.nav, "", ""
                ),
                unittest.mock.call(
                    {"docs_dir": "docs"}, folder_nav, "", "ja"
                ),
                unittest.mock.call(
                    {"docs_dir": "docs"}, suffix_nav, "en", ""
                ),
            ],
            plugin.output.call_args_list,
        )

    def test_before_output_hook_receives_generated_headers(self):
        # パラメーター: on_before_outputフックと言語別設定を有効にする。
        plugin = make_plugin(
            extend_module=True,
            languages={"ja": {"toc_page_title": "目次"}},
        )
        plugin.hook = RecordingHook({"on_before_output"})
        plugin.output_md_file = Mock()
        nav = SimpleNamespace(items=[])
        headers = [TocItem()]

        plugin.output_toc_md_file(
            {"docs_dir": "docs"},
            nav,
            headers,
            "ja",
            "",
            None,
        )

        # チェック内容: 出力直前フックが呼ばれ、言語別タイトルを持つデータが出力処理へ渡る。
        self.assertEqual(
            [("on_before_output", 1)], plugin.hook.calls
        )
        template_data = plugin.output_md_file.call_args.args[1]
        self.assertEqual("目次", template_data.page_title)
        self.assertIs(headers, template_data.toc_headers)

    def test_serve_registers_runtime_watch_targets(self):
        # パラメーター: 通常出力ファイルが存在する状態で開発サーバーを起動する。
        plugin = make_plugin()
        plugin.i18n_plugin = None
        server = Mock()
        builder = Mock()

        with patch(
            "mkdocs_toc_md.plugin.TocExtendModule.watch_file"
        ) as watch_file, patch(
            "mkdocs_toc_md.plugin.os.path.exists", return_value=True
        ):
            plugin.on_serve(server, {}, builder)

        # チェック内容: 拡張ファイルと出力Markdownが監視対象へ登録される。
        watch_file.assert_called_once_with(server, builder)
        server.watch.assert_called_once_with("index.md", builder)


if __name__ == "__main__":
    unittest.main()
