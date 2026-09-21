import glob
import importlib
import os

from flask import current_app as app


def override_function(name, func):
    app.overridden_functions[name] = func


def bypass_csrf_protection(f):
    """
    Decorator that allows a route to bypass the need for a CSRF nonce on POST requests.

    This should be considered beta and may change in future versions.

    :param f: A function that needs to bypass CSRF protection
    :return: Returns a function with the _bypass_csrf attribute set which tells CTFd to not require CSRF protection.
    """
    f._bypass_csrf = True
    return f


def get_plugin_names():
    modules = sorted(glob.glob(app.plugins_dir + "/*"))
    blacklist = {"__pycache__"}
    plugins = []
    for module in modules:
        module_name = os.path.basename(module)
        if os.path.isdir(module) and module_name not in blacklist:
            plugins.append(module_name)
    return plugins


def init_plugins(app):
    """
    Searches for the load function in modules in the CTFd/plugins folder. This function is called with the current CTFd
    app as a parameter. This allows CTFd plugins to modify CTFd's behavior.

    :param app: A CTFd application
    :return:
    """
    app.overridden_functions = {}
    app.plugins_dir = os.path.dirname(__file__)

    if app.config.get("SAFE_MODE", False) is False:
        for plugin in get_plugin_names():
            module = "." + plugin
            module = importlib.import_module(module, package="CTFd.plugins")
            module.load(app)
            print(" * Loaded module, %s" % module)
    else:
        print("SAFE_MODE is enabled. Skipping plugin loading.")
