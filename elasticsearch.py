# -*- coding: utf-8 -*-
from urllib.parse import urlencode
import sublime
import sublime_plugin

DEFAULT_PARAMS = {'pretty': 'true'}
SKIP_PATH = (None, '', b'', [], ())


def make_path(*parts):
    return '/'.join([p for p in parts if p not in SKIP_PATH])


class BaseElasticsearchCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.settings = sublime.load_settings('Elasticsearch.sublime-settings')
        self.servers = self.settings.get('servers')
        self.active_server = self.settings.get("active_server")
        if not self.active_server:
            self.active_server = list(self.servers.keys())[0]

        server_settings = self.servers[self.active_server]

        self.base_url = server_settings.get(
            'base_url', 'http://localhost:9200/')
        if not self.base_url.endswith('/'):
            self.base_url += '/'

        self.index = server_settings.get('index', 'test')
        self.doc_type = server_settings.get('doc_type', 'test')
        self.http_headers = server_settings.get('http_headers', {})

        self.analyzer = server_settings.get('analyzer', 'default')
        self.enabled_create_index = server_settings.get(
            'enabled_create_index', False)
        self.enabled_put_mapping = server_settings.get(
            'enabled_put_mapping', False)
        self.enabled_delete_document = server_settings.get(
            'enabled_delete_document', False)
        self.enabled_delete_index = server_settings.get(
            'enabled_delete_index', False)
        self.enabled_delete_mapping = server_settings.get(
            'enabled_delete_mapping', False)
        self.enabled_index_document = server_settings.get(
            'enabled_index_document', False)
        self.enabled_register_query = server_settings.get(
            'enabled_register_query', False)
        self.enabled_delete_percolator = server_settings.get(
            'enabled_delete_percolator', False)

    def get_request_url(self, url, params):
        params = urlencode(params or DEFAULT_PARAMS)
        if url:
            return '{0}{1}?{2}'.format(self.base_url, url, params)
        return '{0}?{1}'.format(self.base_url, params)

    def run_request(self, method, url=None, body=None, params=None):
        curl_command = ['curl', '-s', '-X', method]
        request_url = self.get_request_url(url, params)
        curl_command += [request_url]

        if body:
            curl_command += ['-d', body]

        for k, v in self.http_headers.items():
            curl_command += ['-H', "{0}: {1}".format(k, v)]

        self.window.run_command('exec', {'cmd': curl_command, 'quiet': True})

    def get_selection_text(self):
        view = self.window.active_view()
        sels = view.sel()
        if len(sels) == 1 and sels[0].empty():
            text = view.substr(sublime.Region(0, view.size()))
            return text
        text = ''.join([view.substr(sel) for sel in sels])
        return text

    def set_index(self, index_name):
        if not index_name:
            return  # canceled
        self.servers[self.active_server]['index'] = index_name
        self.settings.set('servers', self.servers)
        self.save_settings()
        self.status_message('Changed index: {0}'.format(index_name))

    def set_doc_type(self, doc_type):
        if not doc_type:
            return  # canceled
        self.servers[self.active_server]['doc_type'] = doc_type
        self.settings.set('servers', self.servers)
        self.save_settings()
        self.status_message('Changed Type: {0}'.format(doc_type))

    def set_analyzer(self, analyzer):
        if not analyzer:
            return  # canceled
        self.servers[self.active_server]['analyzer'] = analyzer
        self.settings.set('servers', self.servers)
        self.save_settings()
        self.status_message('Changed Type: {0}'.format(analyzer))

    def save_settings(self):
        sublime.save_settings('Elasticsearch.sublime-settings')

    def get_index(self, callback):
        self.window.show_input_panel(
            'Index: ', self.index, callback, None, None)

    def get_doc_type(self, callback):
        self.window.show_input_panel(
            'Document Type: ', self.doc_type, callback, None, None)

    def get_doc_id(self, callback):
        self.window.show_input_panel(
            'Document Id: ', '', callback, None, None)

    def get_analyzer(self, callback):
        self.window.show_input_panel(
            'Analyzer: ', self.analyzer, callback, None, None)

    def status_message(self, message):
        sublime.status_message(message)

    def panel(self, text):
        output_panel = self.window.get_output_panel("textarea")
        output_panel.set_syntax_file('')
        self.window.run_command("show_panel", {"panel": "output.textarea"})
        output_panel.run_command("insert", {"characters": text})


class SearchRequestCommand(BaseElasticsearchCommand):

    def run(self):
        super(SearchRequestCommand, self).run()
        url = make_path(self.index, self.doc_type, '_search')
        body = self.get_selection_text()
        self.run_request('POST', url, body)


class CreateIndexCommand(BaseElasticsearchCommand):

    def run(self):
        super(CreateIndexCommand, self).run()

        if not self.enabled_create_index:
            self.status_message('*** Disabled Create Index! ***')
            return

        self.get_index(self.create_index)

    def create_index(self, index):
        if not index:
            self.status_message('Canceled')
            return

        url = make_path(self.index)
        self.run_request('PUT', url)
        self.set_index(index)


class PutMappingCommand(BaseElasticsearchCommand):

    def run(self):
        super(PutMappingCommand, self).run()

        if not self.enabled_put_mapping:
            self.status_message('*** Disabled Put Mapping! ***')
            return

        if not self.index:
            self.get_index(self.set_index)
            return

        self.get_doc_type(self.put_mapping)

    def set_index(self, index):
        super(PutMappingCommand, self).set_index(index)
        self.run()

    def put_mapping(self, doc_type):
        if not doc_type:
            self.status_message('Canceled')
            return

        url = make_path(self.index, '_mapping', doc_type)
        body = self.get_selection_text()
        self.run_request('PUT', url, body)

        self.set_doc_type(doc_type)


class AnalyzeCommand(BaseElasticsearchCommand):

    def run(self):
        super(AnalyzeCommand, self).run()

        if not self.index:
            self.get_index(self.set_index)
            return

        self.get_analyzer(self.analyze)

    def set_index(self, index):
        super(AnalyzeCommand, self).set_index(index)
        self.run()

    def analyze(self, analyzer):
        if not analyzer:
            self.status_message('canceled')
            return

        url = make_path(self.index, '_analyze')
        body = self.get_selection_text()
        params = {'analyzer': analyzer}
        params.update(DEFAULT_PARAMS)
        self.run_request('POST', url, body, params)

        self.set_analyzer(analyzer)


class ClusterHealthCommand(BaseElasticsearchCommand):

    def run(self):
        super(ClusterHealthCommand, self).run()

        url = make_path('_cat', 'health')
        params = {'v': 'true'}
        self.run_request('GET', url, None, params)


class ListAllIndexesCommand(BaseElasticsearchCommand):

    def run(self):
        super(ListAllIndexesCommand, self).run()

        url = make_path('_cat', 'indices')
        params = {'v': 'true'}
        self.run_request('GET', url, None, params)


class GetIndexSettingsCommand(BaseElasticsearchCommand):

    def run(self):
        super(GetIndexSettingsCommand, self).run()

        self.get_index(self.get_index_settings)

    def get_index_settings(self, index):
        if not index:
            self.status_message('Canceled')
            return

        url = make_path(index, '_settings')
        self.run_request('GET', url)
        self.set_index(index)


class GetMappingCommand(BaseElasticsearchCommand):

    def run(self):
        super(GetMappingCommand, self).run()

        if not self.index:
            self.get_index(self.set_index)
            return

        self.get_doc_type(self.get_mapping)

    def set_index(self, index):
        super(GetMappingCommand, self).set_index(index)
        self.run()

    def get_mapping(self, doc_type):
        if not doc_type:
            self.status_message('Canceled')
            return

        url = make_path(self.index, '_mapping', doc_type)
        self.run_request('GET', url)

        self.set_doc_type(doc_type)


class IndexDocumentCommand(BaseElasticsearchCommand):

    def run(self):
        super(IndexDocumentCommand, self).run()

        if not self.enabled_index_document:
            self.status_message('*** Disabled Index Document! ***')
            return

        if not self.index:
            self.get_index(self.set_index)
            return

        if not self.doc_type:
            self.get_doc_type(self.set_doc_type)
            return

        self.get_doc_id(self.index_document)

    def set_index(self, index):
        super(IndexDocumentCommand, self).set_index(index)
        self.run()

    def set_doc_type(self, doc_type):
        super(IndexDocumentCommand, self).set_doc_type(doc_type)
        self.run()

    def index_document(self, doc_id):
        method = 'POST'
        url = make_path(self.index, self.doc_type)
        body = self.get_selection_text()
        if doc_id:
            method = 'PUT'
            url = make_path(self.index, self.doc_type, doc_id)
        self.run_request(method, url, body)


class DeleteDocumentCommand(BaseElasticsearchCommand):

    def run(self):
        super(DeleteDocumentCommand, self).run()

        if not self.enabled_delete_document:
            self.status_message('*** Disabled Delete Document! ***')
            return

        if not self.index:
            self.get_index(self.set_index)
            return

        if not self.doc_type:
            self.get_doc_type(self.set_doc_type)
            return

        self.get_doc_id(self.delete_document)

    def set_index(self, index):
        super(DeleteDocumentCommand, self).set_index(index)
        self.run()

    def set_doc_type(self, doc_type):
        super(DeleteDocumentCommand, self).set_doc_type(doc_type)
        self.run()

    def delete_document(self, doc_id):
        if not doc_id:
            self.status_message('Canceled')
            return

        url = make_path(self.index, self.doc_type, doc_id)
        self.run_request('DELETE', url)


class GetDocumentCommand(BaseElasticsearchCommand):

    def run(self):
        super(GetDocumentCommand, self).run()

        if not self.index:
            self.get_index(self.set_index)
            return

        if not self.doc_type:
            self.get_doc_type(self.set_doc_type)
            return

        self.get_doc_id(self.get_document)

    def set_index(self, index):
        super(GetDocumentCommand, self).set_index(index)
        self.run()

    def set_doc_type(self, doc_type):
        super(GetDocumentCommand, self).set_doc_type(doc_type)
        self.run()

    def get_document(self, doc_id):
        if not doc_id:
            self.status_message('Canceled')
            return

        url = make_path(self.index, self.doc_type, doc_id)
        self.run_request('GET', url)


class DeleteIndexCommand(BaseElasticsearchCommand):

    def run(self):
        super(DeleteIndexCommand, self).run()

        if not self.enabled_delete_index:
            self.status_message('*** Disabled Delete Index! ***')
            return

        self.get_index(self.delete_index)

    def delete_index(self, index):
        if not index:
            self.status_message('Canceled')
            return

        url = make_path(index)
        self.run_request('DELETE', url)


class DeleteMappingCommand(BaseElasticsearchCommand):

    def run(self):
        super(DeleteMappingCommand, self).run()

        if not self.enabled_delete_mapping:
            self.status_message('*** Disabled Delete Mapping! ***')
            return

        if not self.index:
            self.get_index(self.set_index)
            return

        self.get_doc_type(self.delete_mapping)

    def set_index(self, index):
        super(DeleteMappingCommand, self).set_index(index)
        self.run()

    def delete_mapping(self, doc_type):
        if not doc_type:
            self.status_message('Canceled')
            return

        url = make_path(self.index, doc_type)
        self.run_request('DELETE', url)

        self.set_doc_type(doc_type)


class RegisterPercolatorCommand(BaseElasticsearchCommand):

    def run(self):
        super(RegisterPercolatorCommand, self).run()

        if not self.enabled_register_query:
            self.status_message(
                '*** Disabled Register Query (Percolator)! ***')
            return

        if not self.index:
            self.get_index(self.set_index)

        self.get_doc_id(self.register_query)

    def set_index(self, index):
        super(RegisterPercolatorCommand, self).set_index(index)
        self.run()

    def register_query(self, doc_id):
        if not doc_id:
            self.status_message('Canceled')
            return

        url = make_path(self.index, '.percolator', doc_id)
        body = self.get_selection_text()
        self.run_request('PUT', url, body)


class ShowPercolatorCommand(BaseElasticsearchCommand):

    def run(self):
        super(ShowPercolatorCommand, self).run()

        if not self.index:
            self.get_index(self.set_index)
            return

        url = make_path(self.index, '.percolator', '_search')
        self.run_request('POST', url)

    def set_index(self, index):
        super(ShowPercolatorCommand, self).set_index(index)
        self.run()


class MatchPercolatorCommand(BaseElasticsearchCommand):

    def run(self):
        super(MatchPercolatorCommand, self).run()

        if not self.index:
            self.get_index(self.set_index)
            return

        if not self.doc_type:
            self.get_doc_type(self.set_doc_type)
            return

        url = make_path(self.index, self.doc_type, '_percolate')
        body = self.get_selection_text()
        self.run_request('POST', url, body)

    def set_index(self, index):
        super(MatchPercolatorCommand, self).set_index(index)
        self.run()

    def set_doc_type(self, doc_type):
        super(MatchPercolatorCommand, self).set_doc_type(doc_type)
        self.run()


class DeletePercolatorCommand(BaseElasticsearchCommand):

    def run(self):
        super(DeletePercolatorCommand, self).run()

        if not self.enabled_delete_percolator:
            self.status_message('*** Disabled Delete Percolator! ***')
            return

        if not self.index:
            self.get_index(self.set_index)
            return

        if not self.doc_type:
            self.get_doc_type(self.set_doc_type)
            return

        self.get_doc_id(self.delete_percolator)

    def set_index(self, index):
        super(DeletePercolatorCommand, self).set_index(index)
        self.run()

    def set_doc_type(self, doc_type):
        super(DeletePercolatorCommand, self).set_doc_type(doc_type)
        self.run()

    def delete_percolator(self, doc_id):
        if not doc_id:
            self.status_message('Canceled')
            return

        url = make_path(self.index, '.percolator', doc_id)
        self.run_request('DELETE', url)


class SwitchServersCommand(BaseElasticsearchCommand):

    def run(self):
        super(SwitchServersCommand, self).run()
        servers = list(self.servers.keys())
        self.window.show_quick_panel(servers, self.server_selected)

    def server_selected(self, index):
        if index == -1:
            sublime.status_message('Canceled')
            return  # canceled
        self.active_server = list(self.servers.keys())[index]
        self.settings.set("active_server", self.active_server)
        self.save_settings()


class ShowActiveServerCommand(BaseElasticsearchCommand):

    def run(self):
        super(ShowActiveServerCommand, self).run()
        self.panel(
            "Active Server Settings [{active_server}]\n"
            "=============================================================\n"
            "- base_url                     : {base_url}\n"
            "- index                        : {index}\n"
            "- doc_type                     : {doc_type}\n"
            "- analyzer                     : {analyzer}\n"
            "- enabled_create_index         : {enabled_create_index}\n"
            "- enabled_delete_document      : {enabled_delete_document}\n"
            "- enabled_delete_index         : {enabled_delete_index}\n"
            "- enabled_delete_mapping       : {enabled_delete_mapping}\n"
            "- enabled_delete_percolator    : {enabled_delete_percolator}\n"
            "- enabled_index_document       : {enabled_index_document}\n"
            "- enabled_put_mapping          : {enabled_put_mapping}\n"
            "- enabled_register_query       : {enabled_register_query}\n"
            "".format(
                active_server=self.active_server,
                base_url=self.base_url,
                index=self.index,
                doc_type=self.doc_type,
                analyzer=self.analyzer,
                enabled_create_index=self.enabled_create_index,
                enabled_delete_document=self.enabled_delete_document,
                enabled_delete_index=self.enabled_delete_index,
                enabled_delete_mapping=self.enabled_delete_mapping,
                enabled_delete_percolator=self.enabled_delete_percolator,
                enabled_index_document=self.enabled_index_document,
                enabled_put_mapping=self.enabled_put_mapping,
                enabled_register_query=self.enabled_register_query)
        )

        self.status_message(
            ': {0} ({1} / {2})'.format(
                self.active_server, self.index, self.doc_type))


class ChangeIndexCommand(BaseElasticsearchCommand):

    def run(self):
        super(ChangeIndexCommand, self).run()
        self.get_index(self.set_index)


class ChangeDocTypeCommand(BaseElasticsearchCommand):

    def run(self):
        super(ChangeDocTypeCommand, self).run()
        self.get_doc_type(self.set_doc_type)