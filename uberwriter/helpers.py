# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# BEGIN LICENSE
# Copyright (C) 2012, Wolf Vollprecht <w.vollprecht@gmail.com>
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
# END LICENSE

### DO NOT EDIT THIS FILE ###

"""Helpers for the application."""
import logging
import os
import shutil

import gi
import pypandoc
from gi.overrides.Pango import Pango

from uberwriter.settings import Settings

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # pylint: disable=E0611

from uberwriter.config import get_data_file
from uberwriter.builder import Builder


def get_builder(builder_file_name):
    """Return a fully-instantiated Gtk.Builder instance from specified ui
    file

    :param builder_file_name: The name of the builder file, without extension.
        Assumed to be in the 'ui' directory under the data path.
    """
    # Look for the ui file that describes the user interface.
    ui_filename = get_data_file('ui', '%s.ui' % (builder_file_name,))
    if not os.path.exists(ui_filename):
        ui_filename = None

    builder = Builder()
    builder.set_translation_domain()
    builder.add_from_file(ui_filename)
    return builder


def path_to_file(path):
    """Return a file path (file:///) for the given path"""

    return "file://" + path


def get_media_file(media_file_path):
    """Return the full path of a given filename under the media dir
       (starts with file:///)
    """

    return path_to_file(get_media_path(media_file_path))


def get_media_path(media_file_name):
    """Return the full path of a given filename under the media dir
       (doesn't start with file:///)
    """

    media_path = get_data_file('media', '%s' % (media_file_name,))
    if not os.path.exists(media_path):
        media_path = None
    return media_path


def get_css_path(css_file_name):
    """Return the full path of a given filename under the css dir
       (doesn't start with file:///)
    """
    return get_media_path("css/{}".format(css_file_name))


def get_script_path(script_file_name):
    """Return the full path of a given filename under the script dir
    """
    script_path = get_data_file('lua', '%s' % (script_file_name,))
    if not os.path.exists(script_path):
        script_path = None
    return script_path


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


def set_up_logging(opts):
    # add a handler to prevent basicConfig
    root = logging.getLogger()
    null_handler = NullHandler()
    root.addHandler(null_handler)

    formatter = logging.Formatter(
        "%(levelname)s:%(name)s: %(funcName)s() '%(message)s'")

    logger = logging.getLogger('uberwriter')
    logger_sh = logging.StreamHandler()
    logger_sh.setFormatter(formatter)
    logger.addHandler(logger_sh)

    lib_logger = logging.getLogger('uberwriter')
    lib_logger_sh = logging.StreamHandler()
    lib_logger_sh.setFormatter(formatter)
    lib_logger.addHandler(lib_logger_sh)

    # Set the logging level to show debug messages.
    if opts.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug('logging enabled')
    if opts.verbose and opts.verbose > 1:
        lib_logger.setLevel(logging.DEBUG)


def get_help_uri(page=None):
    # help_uri from source tree - default language
    here = os.path.dirname(__file__)
    help_uri = os.path.abspath(os.path.join(here, '..', 'help', 'C'))

    if not os.path.exists(help_uri):
        # installed so use gnome help tree - user's language
        help_uri = 'uberwriter'

    # unspecified page is the index.page
    if page is not None:
        help_uri = '%s#%s' % (help_uri, page)

    return help_uri


def show_uri(parent, link):
    screen = parent.get_screen()
    Gtk.show_uri(screen, link, Gtk.get_current_event_time())


def alias(alternative_function_name):
    '''see http://www.drdobbs.com/web-development/184406073#l9'''
    def decorator(function):
        '''attach alternative_function_name(s) to function'''
        if not hasattr(function, 'aliases'):
            function.aliases = []
        function.aliases.append(alternative_function_name)
        return function
    return decorator


def exist_executable(command):
    """return if a command can be executed in the SO

    Arguments:
        command {str} -- a command
    
    Returns:
        {bool} -- if the given command exists in the system
    """

    return shutil.which(command) is not None


def get_descendant(widget, child_name, level, doPrint=False):
    if widget is not None:
        if doPrint: print("-"*level + str(Gtk.Buildable.get_name(widget)) +
                          " :: " + widget.get_name())
    else:
        if doPrint: print("-"*level + "None")
        return None
    #/*** If it is what we are looking for ***/
    if Gtk.Buildable.get_name(widget) == child_name: # not widget.get_name() !
        return widget
    #/*** If this widget has one child only search its child ***/
    if (hasattr(widget, 'get_child') and
            callable(getattr(widget, 'get_child')) and
            child_name != ""):
        child = widget.get_child()
        if child is not None:
            return get_descendant(child, child_name, level+1,doPrint)
    # /*** Ity might have many children, so search them ***/
    elif (hasattr(widget, 'get_children') and
          callable(getattr(widget, 'get_children')) and
          child_name != ""):
        children = widget.get_children()
        # /*** For each child ***/
        found = None
        for child in children:
            if child is not None:
                found = get_descendant(child, child_name, level+1, doPrint) # //search the child
                if found: return found


def get_char_width(widget):
    return Pango.units_to_double(
        widget.get_pango_context().get_metrics().get_approximate_char_width())


def pandoc_convert(text, to="html5", args=[], outputfile=None):
    fr = Settings.new().get_value('input-format').get_string() or "markdown"
    args.extend(["--quiet"])
    return pypandoc.convert_text(text, to, fr, extra_args=args, outputfile=outputfile)
