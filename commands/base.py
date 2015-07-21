import json
import threading
import sublime
import sublime_plugin
import analytics
import uuid

from elasticsearch import Elasticsearch
from elasticsearch_connections import CustomHeadersConnection
from abc import ABCMeta, abstractmethod

from ..panel import IndexListPanel
from ..panel import DocTypeListPanel
from ..panel import SwitchServerListPanel
from ..panel import AnalyzerListPanel
from ..panel import ScriptListPanel
from ..panel import SearchTemplateListPanel
from ..panel import AliasListPanel
from ..panel import IndexTemplateListPanel
from ..panel import WarmerListPanel
from ..panel import FieldListPanel


ANALYTICS_WRITE_KEY = "phc2hsUe48Dfw1iwsYQs2W7HH9jcwrws"


def track_command(user_id, command_name):
    analytics.write_key = ANALYTICS_WRITE_KEY
    analytics.identify(user_id)
    analytics.track(user_id, "Run Command", {
        "category": "ST3",
        "label": command_name,
    })


class Settings(object):
    SETTINGS_FILE = 'Elasticsearch.sublime-settings'

    def __init__(self):
        self.settings = sublime.load_settings(self.SETTINGS_FILE)

    @property
    def base_url(self):
        return self.settings.get("base_url", "http://localhost:9200")

    @property
    def index(self):
        return self.settings.get("index", "blog-ja")

    @property
    def doc_type(self):
        return self.settings.get("doc_type", "posts")

    @property
    def scroll_size(self):
        return self.settings.get("scroll_size", "1m")

    @property
    def headers(self):
        return self.settings.get("headers", None)

    @property
    def servers(self):
        return self.settings.get("servers", [])

    @property
    def active_server(self):
        return dict(
            base_url=self.base_url,
            index=self.index,
            doc_type=self.doc_type,
            scroll_size=self.scroll_size,
        )

    @property
    def analytics(self):
        return self.settings.get("analytics", True)

    @property
    def user_id(self):
        return self.settings.get("user_id", None)

    def set(self, key, value):
        self.settings.set(key, value)

    def save(self):
        sublime.save_settings(self.SETTINGS_FILE)


class BaseCommand(sublime_plugin.WindowCommand):
    __metaclass__ = ABCMeta
    command_name = None

    def __init__(self, *args, **kwargs):
        self.settings = Settings()
        sublime_plugin.WindowCommand.__init__(self, *args, **kwargs)

    @property
    def view(self):
        return self.window.active_view()

    def is_valid_json(self):
        try:
            json.loads(self.get_text())
        except ValueError:
            return False
        return True

    def is_enabled(self):
        return self.is_valid_json()

    def get_text(self):
        return self.view.substr(sublime.Region(0, self.view.size()))

    def init_client(self):
        self._client = Elasticsearch(
            self.settings.base_url,
            connection_class=CustomHeadersConnection,
            headers=self.settings.headers
        )
        return self._client

    def save_settings(self):
        self.settings.save()
        self.init_client()

    @property
    def client(self):
        return self.init_client()

    def track_command(self):
        if self.settings.analytics:
            user_id = self.settings.user_id
            if not user_id:
                user_id = uuid.uuid4()
                self.settings.set("user_id", str(user_id))
                self.settings.save()
            track_command(user_id, self.command_name)

    def show_input_panel(self, label, default, callback):
        self.window.show_input_panel(label, default, callback, None, None)

    def show_response(self, response, title=""):
        title = title or self.__class__.__name__
        text = json.dumps(response, indent=2, ensure_ascii=False)
        self.window.run_command(
            "show_response", {"title": title, "text": text})

    def show_index_list_panel(self, callback):
        list_panel = IndexListPanel(self.window, self.client)
        list_panel.show(callback)

    def show_doc_type_list_panel(self, callback):
        list_panel = DocTypeListPanel(
            self.window, self.client, self.settings.index)
        list_panel.show(callback)

    def show_analyzer_list_panel(self, callback):
        list_panel = AnalyzerListPanel(
            self.window, self.client, self.settings.index)
        list_panel.show(callback)

    def show_switch_server_list_panel(self, callback):
        list_panel = SwitchServerListPanel(self.window, self.settings.servers)
        list_panel.show(callback)

    def show_script_list_panel(self, callback):
        list_panel = ScriptListPanel(self.window, self.client)
        list_panel.show(callback)

    def show_search_template_list_panel(self, callback):
        list_panel = SearchTemplateListPanel(self.window, self.client)
        list_panel.show(callback)

    def show_alias_list_panel(self, callback):
        list_panel = AliasListPanel(
            self.window, self.client, self.settings.index)
        list_panel.show(callback)

    def show_index_template_list_panel(self, callback):
        list_panel = IndexTemplateListPanel(self.window, self.client)
        list_panel.show(callback)

    def show_warmer_list_panel(self, callback):
        list_panel = WarmerListPanel(
            self.window, self.client, self.settings.index)
        list_panel.show(callback)

    def show_field_list_panel(self, callback):
        list_panel = FieldListPanel(
            self.window, self.client,
            self.settings.index, self.settings.doc_type)
        list_panel.show(callback)

    def show_output_panel(self, text, syntax=None):
        self.window.run_command(
            "show_output_panel", {"text": text, "syntax": syntax})

    def show_object_output_panel(self, obj):
        options = dict(
            indent=4,
            ensure_ascii=False
        )

        self.show_output_panel(
            json.dumps(obj, **options),
            syntax="Packages/JavaScript/JSON.tmLanguage")

    def show_active_server(self):
        self.window.run_command("settings_show_active_server")

    @abstractmethod
    def run_request(self, *args, **kwargs):
        raise NotImplementedError()

    def run_request_wrapper(self, *args, **kwargs):
        try:
            response = self.run_request(*args, **kwargs)
        except Exception as e:
            sublime.error_message("Error: {}".format(e))
            return

        if response is not None:
            self.show_response(response)
            self.track_command()

    def request_thread(self, *args, **kwargs):
        thread = threading.Thread(
            target=self.run_request_wrapper, args=args, kwargs=kwargs)
        thread.start()

    def run(self, *args, **kwargs):
        self.request_thread(*args, **kwargs)


class CreateBaseCommand(BaseCommand):

    def run_request_wrapper(self, *args, **kwargs):
        try:
            response = self.run_request(*args, **kwargs)
        except Exception as e:
            sublime.error_message("Error: {}".format(e))
            return

        if response is not None:
            self.show_object_output_panel(response)
            self.track_command()


class DeleteBaseCommand(CreateBaseCommand):
    pass


class CatBaseCommand(CreateBaseCommand):

    def is_enabled(self):
        return True

    def run_request_wrapper(self, *args, **kwargs):
        try:
            response = self.run_request(*args, **kwargs)
        except Exception as e:
            sublime.error_message("Error: {}".format(e))
            return

        if response is not None:
            self.show_output_panel(response)
            self.track_command()


class SearchBaseCommand(BaseCommand):

    def extend_options(self, options, search_type=None):
        if search_type:
            self.command_name = "{base}-{search_type}".format(
                    base=self.command_name,
                    search_type=search_type.lower()
                )

        if search_type == "scan":
            options["params"] = dict(
                search_type=search_type,
                scroll=self.settings.scroll_size
            )
        elif search_type is not None:
            options["params"] = dict(
                search_type=search_type
            )
        return options


class SettingsBaseCommand(BaseCommand):

    def is_enabled(self):
        return True
