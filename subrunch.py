import sublime
import sublime_plugin
import os
import re


def defaults(key):
    scriptExt = '.coffee'
    default_settings = {
        'app_dir': 'app',

        'models': {
            'dir': 'models',
            'ext': scriptExt,
            'postfix': ''
        },
        'views': {
            'dir': 'views',
            'ext': scriptExt,
            'postfix': '_view'
        },
        'controllers': {
            'dir': 'controllers',
            'ext': scriptExt,
            'postfix': '_controller'
        },
        'templates': {
            'dir': 'views/templates',
            'ext': '.hbs',
            'postfix': ''
        },
        'styles': {
            'dir': 'views/styles',
            'ext': '.styl',
            'postfix': ''
        },

        'script_ext': scriptExt,
        'styles_ext': '.styl',
        'template_ext': '.hbs'
      }
    return default_settings[key]


def app_dir(window):
    return os.path.join(os.path.join(window.folders()[0], defaults('app_dir')))


def module_name(filename):
    print filename
    reg = r"(_controller)?(_view)?(_test)?\.[\w]*"
    return re.sub(reg, '', filename)


def open_file_if_exists(window, filename):
    if os.path.isfile(filename):
        window.open_file(filename)
    else:
        sublime.status_message(filename + ' does not exist')


class SubrunchCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.options = [
            ('Views', {'command': 'subrunch_list_modules', 'args': {'module': 'views'}}),
            ('Models', {'command': 'subrunch_list_modules', 'args': {'module': 'models'}}),
            ('Templates', {'command': 'subrunch_list_modules', 'args': {'module': 'templates'}}),
            ('Styles', {'command': 'subrunch_list_modules', 'args': {'module': 'styles'}}),
            ('Controllers', {'command': 'subrunch_list_modules', 'args': {'module': 'controllers'}}),
            ('Open corresponding model', {'command': 'subrunch_corresponding_brunch_module', 'args': {'module': 'models'}}),
            ('Open corresponding view', {'command': 'subrunch_corresponding_brunch_module', 'args': {'module': 'views'}}),
            ('Open corresponding template', {'command': 'subrunch_corresponding_brunch_module', 'args': {'module': 'templates'}}),
            ('Open corresponding style', {'command': 'subrunch_corresponding_brunch_module', 'args': {'module': 'styles'}}),
            ('Open corresponding controller', {'command': 'subrunch_corresponding_brunch_module', 'args': {'module': 'controllers'}}),
        ]

        self.window.show_quick_panel(map(lambda t: t[0], self.options), self.callback)

    def callback(self, index):
        if index == -1:
            return
        else:
            self.window.run_command(
                self.options[index][1]['command'],
                self.options[index][1]['args']
            )


class SubrunchListModulesCommand(sublime_plugin.WindowCommand):
    def run(self, module):
        modulesPath = os.path.join(defaults('app_dir'), defaults(module)['dir'])
        absoluteModulesPath = os.path.join(self.window.folders()[0], modulesPath)

        items = []
        self.paths = []
        for dirname, dirnames, filenames in os.walk(absoluteModulesPath):
            for filename in filenames:
                print filename
                print dirname
                name, ext = os.path.splitext(filename)
                if ext == defaults(module)['ext']:
                    items.append([name, os.path.join(dirname[len(self.window.folders()[0]) + 1:], filename)])
                    self.paths.append(os.path.join(dirname, filename))

        self.window.show_quick_panel(items, self.openFile)

    def openFile(self, index):
        if index == -1:
            return
        open_file_if_exists(self.window, self.paths[index])


class SubrunchCorrespondingBrunchModuleCommand(sublime_plugin.WindowCommand):
    def run(self, module):
        modules = module

        # get current file path relative to app_dir, e.g. ~/my_app/app/views/sub_views/some_view.coffee to /views/sub_views/some_view.coffee
        activeModule = self.window.active_view().file_name()[len(app_dir(self.window)):]
        # remove module name - /views/sub_views/some_view.coffee to sub_views/some_view.coffee
        activeModule = re.sub(r"^/.*?/", '', activeModule)
        activeModule = module_name(activeModule)

        moduleAbsDir = os.path.join(app_dir(self.window), defaults(modules)['dir'])
        activeModuleFilename = activeModule + defaults(modules)['postfix'] + defaults(modules)['ext']

        exactCorrespondingPath = os.path.join(
            moduleAbsDir,
            activeModuleFilename
        )

        if os.path.isfile(exactCorrespondingPath):
            self.window.open_file(exactCorrespondingPath)
        else:
            self.inexactPaths = self.get_inexact_corresponding_paths(moduleAbsDir, activeModuleFilename)
            if len(self.inexactPaths) == 0:
                sublime.status_message('No corresponding ' + modules + ' for ' + activeModule)
            elif len(self.inexactPaths) == 1:
                self.window.open_file(self.inexactPaths[0])
            else:
                self.window.show_quick_panel(self.inexactPaths, self.openFile)

    def get_inexact_corresponding_paths(self, correspondingModulePath, activeModuleFilename):
        moduleBaseName = os.path.basename(activeModuleFilename)
        paths = []
        for dirname, dirnames, filenames in os.walk(correspondingModulePath):
            for filename in filenames:
                if filename == moduleBaseName:
                    # paths.append(os.path.join(dirname[len(self.window.folders()[0]) + 1:], filename))
                    paths.append(os.path.join(dirname, filename))
        return paths

    def openFile(self, index):
        if index == -1:
            return
        open_file_if_exists(self.window, self.inexactPaths[index])
