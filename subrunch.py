import sublime, sublime_plugin
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

def module_name(filename):
  reg = r"(_controller)?(_view)?(_test)?\.[\w]*"
  return re.sub(reg, '', filename)

def open_file_if_exists(window, filename):
  if os.path.isfile(filename):
    window.open_file(filename)
  else:
    sublime.status_message(filename + ' does not exist')

class SubrunchCommand(sublime_plugin.WindowCommand):
  def run(self):
    self.options = {
      'List views': {
        'command': 'subrunch_list_modules',
        'args': {
          'module': 'views'
        }
      },
      'List models': {
        'command': 'subrunch_list_modules',
        'args': {
          'module': 'models'
        }
      },
      'List templates': {
        'command': 'subrunch_list_modules',
        'args': {
          'module': 'templates'
        }
      },
      'List styles': {
        'command': 'subrunch_list_modules',
        'args': {
          'module': 'styles'
        }
      },
      'List controllers': {
        'command': 'subrunch_list_modules',
        'args': {
          'module': 'controllers'
        }
      },
      'Open corresponding model': {
        'command': 'subrunch_corresponding_brunch_module',
        'args': {
          'module': 'models'
        }
      },
      'Open corresponding view': {
        'command': 'subrunch_corresponding_brunch_module',
        'args': {
          'module': 'views'
        }
      },
      'Open corresponding template': {
        'command': 'subrunch_corresponding_brunch_module',
        'args': {
          'module': 'templates'
        }
      },
      'Open corresponding style': {
        'command': 'subrunch_corresponding_brunch_module',
        'args': {
          'module': 'styles'
        }
      },
      'Open corresponding controller': {
        'command': 'subrunch_corresponding_brunch_module',
        'args': {
          'module': 'controllers'
        }
      },
    }

    self.window.show_quick_panel(self.options.keys(), self.callback)

  def callback(self, index):
    if index == -1:
      return 
    else:
      self.window.run_command(
        self.options[self.options.keys()[index]]['command'], 
        self.options[self.options.keys()[index]]['args']
      )

class SubrunchListModulesCommand(sublime_plugin.WindowCommand):
  def run(self, module):
    modulesPath = os.path.join(defaults('app_dir'), defaults(module)['dir'])
    absoluteModulesPath = os.path.join(self.window.folders()[0], modulesPath)

    items = []
    self.paths= []
    for dirname, dirnames, filenames in os.walk(absoluteModulesPath):
      for filename in filenames:
        name, ext = os.path.splitext(filename)
        if ext == defaults(module)['ext']:
          items.append([name, os.path.join(modulesPath, filename)])
          self.paths.append(os.path.join(absoluteModulesPath, filename))

    self.window.show_quick_panel(items, self.openFile)

  def openFile(self, index):
    if index == -1:
      return
    open_file_if_exists(self.window, self.paths[index])

class SubrunchCorrespondingBrunchModuleCommand(sublime_plugin.WindowCommand):
  def run(self, module):
    modules = module

    activeModule = os.path.basename(self.window.active_view().file_name())

    open_file_if_exists(
      self.window, 
      os.path.join(
        self.window.folders()[0], 
        defaults('app_dir'), 
        defaults(modules)['dir'], 
        module_name(activeModule) + defaults(modules)['postfix'] + defaults(modules)['ext']
      )
    )
    