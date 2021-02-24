from kivymd.app import MDApp as App
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
from kivymd.theming import ThemeManager
from flask import Flask as FlaskApp
from os import access as file_exists
from os import F_OK as file_exists_param
from os.path import join as join_path
from os.path import isdir as is_dir
from os import name as os_type
from flask import request as req
from flask_cors import CORS as cors_for_flask
from threading import Thread as NewThread
from requests import get as req_get


Config.set('kivy', 'keyboard_mode', 'systemanddock')


class Container(BoxLayout):
    def __init__(self, *args, **kwargs):
        self.is_server_on = False
        self.port = 5000
        self.host = '127.0.0.1'
        self.path = '/storage/emulated/0/'
        if os_type == 'nt':
            from os import getcwd as get_current_dir
            get_current_dir()
        self.app = None
        self.can_shutdown = False
        self.read_config()
        super().__init__(**kwargs)

    def read_config(self):
        if file_exists('androidwebserver.txt', file_exists_param):
            config = self.fastread('androidwebserver.txt').split('\n')
            self.port = int(config[0])
            self.host = str(config[1])
            self.path = str(config[2])

    def fastwrite(self, filename, content):
        temp_file = open(filename, 'w')
        temp_file.write(content)
        temp_file.close()

    def fastread(self, filename):
        temp_file = open(filename, 'r')
        read = temp_file.read()
        temp_file.close()
        return read

    def shutdown(self):
        self.can_shutdown = True
        req_get(f'http://{self.host}:{self.port}/shutdown_this_fucking_server')

    def run_app(self):
        self.app.run(self.host, port=self.port, debug=False)

    def error404(self):
        error_404_path = join_path(self.path, '404')
        if file_exists(error_404_path + '.html', file_exists_param):
            return self.fastread(join_path(self.path, '404.html')), 404
        elif file_exists(error_404_path + '.htm', file_exists_param):
            return self.fastread(join_path(self.path, '404.htm')), 404
        else:
            return 'Error404', 404

    def toggle_server(self):
        if self.is_server_on:
            self.runserver_btn.text = 'Run Server!'
            self.shutdown()
            self.is_server_on = False
        else:
            self.port = int(self.port_text.text)
            if self.port < 1 or self.port > 27125:
                self.port = 5000
                self.port_text.text = str(self.port)
            self.app = FlaskApp(__name__, static_folder=self.path, template_folder=self.path)
            cors_for_flask(self.app)

            @self.app.route('/shutdown_this_fucking_server')
            def shutdown_this_fucking_server():
                if self.can_shutdown:
                    func = req.environ.get('werkzeug.server.shutdown')
                    if func:
                        func()
                        return 'True'
                    else:
                        return 'False'
                else:
                    return 'False'

            @self.app.route('/')
            def main_index():
                index_path = join_path(self.path, 'index')
                if file_exists(index_path + '.html', file_exists_param):
                    return self.fastread(join_path(self.path, 'index.html'))
                elif file_exists(index_path + '.htm', file_exists_param):
                    return self.fastread(join_path(self.path, 'index.htm'))
                else:
                    return self.error404()

            @self.app.route('/<path:url>')
            def main(url):
                if is_dir(join_path(self.path, url)):
                    index_path = join_path(self.path, url, 'index')
                    if file_exists(index_path + '.html', file_exists_param):
                        print(join_path(self.path, url, 'index.html'))
                        return self.fastread(join_path(self.path, url, 'index.html'))
                    elif file_exists(index_path + '.htm', file_exists_param):
                        return self.fastread(join_path(self.path, url, 'index.htm'))
                    else:
                        return self.error404()
                elif url[-5:] == '.html' or url[-4:] == '.htm':
                    joined = join_path(self.path, url)
                    if file_exists(joined, file_exists_param):
                        return self.fastread(joined)
                    else:
                        return self.error404()
                else:
                    joined = join_path(self.path, url)
                    print(joined)
                    if file_exists(joined, file_exists_param):
                        return self.app.send_static_file(url)
                    else:
                        return self.error404()

            self.app.use_reloader = False
            self.can_shutdown = False
            self.runserver_btn.text = 'Stop Server!'
            NewThread(target=self.run_app).start()
            self.is_server_on = True


class AndroidWebServerApp(App):
    def __init__(self, *args, **kwargs):
        self.theme_cls = ThemeManager()
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.theme_style = 'Light'
        self.title = 'Android Web Server'
        super().__init__(**kwargs)

    def build(self):
        return Container()


if __name__ == '__main__':
    AndroidWebServerApp().run()
