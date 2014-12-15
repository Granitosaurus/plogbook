#!/usr/bin/env python2
from __future__ import print_function
import os
import re
import sys
import fnmatch
import argparse
import tempfile
import subprocess

from datetime import datetime

# # External package import (things that don't come with python and are optional)
# Markdown2 is for markdown to html conversion
import webbrowser

try:
    import markdown2
except ImportError:
    MARKDOWN = False
else:
    MARKDOWN = True

# # multi-versioning
VERSION = sys.version_info[0]
IS_3 = True if VERSION == 3 else False
if IS_3:
    from urllib.request import urlopen
    from urllib.parse import quote

    input = input
else:
    from urllib2 import urlopen
    from urllib import quote

    input = raw_input

# ---------------------------------------------------------------------------------------------------------------------
# EDIT these to change css and html.
# Note if you change DEFAULT_HTML be sure to check the DEFAULT_FORMAT lambda function which fills up the plog
# You might need to adjust <...>_FORMAT constants if you decide to change html or css.
# ---------------------------------------------------------------------------------------------------------------------
DEFAULT_CSS = """
/*Default css for plogbook*/
    body {
        background-color: #c3c3c3;
        font-family: "Courier New", courier, monospace;
        color: #ffffff;
    }

    table {
        width: 70%;
        margin-top: 50px;
        margin-left: 15%;
        margin-right: 15%;
        border-collapse: collapse;
        background-color: #727c8b;
    }

    table, td, th {
        border: 1px solid #c6c6c6;
        padding: 5px;
    }

    th {
        text-align: left;
        width: 100px;
    }

    td#msg_value, th#msg_header {
        background-color: #3f3a4b;
        border-top: 4px solid #cdcdcd;
    }

    .cat_header, .main_header{
        background-color: #3f3a4b;
    }

    a {
        text-decoration: none;
        color: white;
    }
    a:hover{
        text-decoration: underline;
        color: white;
    }
"""
DEFAULT_PLOG_FORMAT = lambda msg, cat, date, title, template: template.format(msg=msg, cat=cat, date=date, title=title)
DEFAULT_PLOG = """
<!--default template for a plog-->
        <head>
        <link rel="stylesheet" type="text/css" href="theme.css">
        </head>
        <table id='plog_table'>
        <tr>
            <th id='category_header'>
            Category:
            </th>
            <td id='category_value'>
            {cat}
            </td>
        </tr>
        <tr>
            <th id='date_header'>
            Date:
            </th>
            <td id='date_value'>
            {date}
            </td>
        </tr>
        <tr>
            <th id='title_header'>
            Title:
            </th>
            <td id='title_value'>
            {title}
            </td>
        </tr>
        <tr>
            <th id='msg_header'>
            Log:
            </th>
            <td id='msg_value'>
            {msg}
            </td>
        </tr>
        </table>
"""
DEFAULT_CAT_FORMAT = lambda template, items: template.format(items=items)
DEFAULT_CAT = """
<!--default template for a plog-->
<head>
    <link rel="stylesheet" type="text/css" href="theme.css">
</head>
<table id='cat_table'>
    <tr>
        <th id='cat_header_title' class='cat_header'>
            Title
        </th>
        <th id='cat_header_date' class='cat_header'>
            Date
        </th>
        <th id='cat_header_location' class='cat_header'>
            Location
        </th>
        <th id='cat_header_entry' class='cat_header'>
            ID#
        </th>
    </tr>
    {items}
</table>
"""
DEFAULT_CAT_ITEM_FORMAT = lambda cat_id, date, relative_location, title, location, template: template.format(
    cat_id=cat_id, date=date, relative_location=relative_location, title=title, location=location)
DEFAULT_CAT_ITEM = """
    <tr>
        <td id='cat_entry_title'>
            <a href='{relative_location}'>{title}</a>
        </td>
        <td id='cat_entry_date'>
            {date}
        </td>
        <td id='cat_entry_location'>
            {location}
        </td>
        <td id='cat_entry_id'>
            {cat_id}
        </td>
    </tr>
"""
DEFAULT_MAIN_FORMAT = lambda template, items: template.format(items=items)
DEFAULT_MAIN = """
<!--default template for a plog-->
<head>
    <link rel="stylesheet" type="text/css" href="theme.css">
</head>
<table id='main_table'>
    <tr>
        <th id='main_header_title' class='main_header'>
            Name
        </th>
        <th id='main_header_count' class='main_header'>
            Plog count
        </th>
        <th id='main_header_date' class='main_header'>
            Date
        </th>
        <th id='main_header_location' class='main_header'>
            Location
        </th>
        <th id='main_header_entry' class='main_header'>
            ID#
        </th>
    </tr>
    {items}
</table>
"""
DEFAULT_MAIN_ITEM_FORMAT = lambda relative_location, name, count, date, location, main_id, template: template.format(
    relative_location=relative_location, name=name, count=count, date=date, location=location, main_id=main_id)
DEFAULT_MAIN_ITEM = """
    <tr>
        <td id='main_entry_title'>
            <a href={relative_location}>{name}</a>
        </td>
        <td id='main_entry_date'>
            {count}
        </td>
        <td id='main_entry_date'>
            {date}
        </td>
        <td id='main_entry_location'>
            {location}
        </td>
        <td id='main_entry_id'>
            {main_id}
        </td>
    </tr>
"""
# ----------------------------------------------------------------------------------------------------------------------


class PlogBook:
    """
    This is main class for plogbook log book
    """
    templates = {'theme.css': DEFAULT_CSS, 'plog.html': DEFAULT_PLOG, 'category.html': DEFAULT_CAT,
                 'category_item.html': DEFAULT_CAT_ITEM, 'main.html': DEFAULT_MAIN, 'main_item.html': DEFAULT_MAIN_ITEM}

    def __init__(self, location=None):
        """
        :param location: location of the plogbook, if not provided current working directory will be taken
        """
        self.location = location or os.getcwd()
        self.template_theme = self.read_teamplate('theme.css') or DEFAULT_CSS
        self.template_plog = self.read_teamplate('plog.html') or DEFAULT_PLOG
        self.template_cat = self.read_teamplate('category.html') or DEFAULT_CAT
        self.template_cat_item = self.read_teamplate('category_item.html') or DEFAULT_CAT_ITEM
        self.template_main = self.read_teamplate('main.html') or DEFAULT_MAIN
        self.template_main_item = self.read_teamplate('main_item.html') or DEFAULT_MAIN_ITEM

    def write_plog(self, editor=None, markdown=False, convert_img=False, override_theme=False):
        """
        This method is the main method that is being run to start the process of recording the plog
        :param editor: whether to take 'message' part of the input via editor, otherwise input from shell will be taken
        :param markdown: whether the 'message' aprt of the input is markdown and requires conversion, this requires
        markdown2 external package
        :param convert_img: Whether to localize images found in 'img' tags, they will be saved over category/images/
        :param override_theme: Whether to override theme with a new one.
        """
        # Data Input and formatting
        date = datetime.now().strftime('%x-%X')
        print(''.center(80, '_'))
        print('|' + 'Writting Plog for {}'.format(date).center(78) + '|')
        print(''.center(80, '-'))
        category = input('Category: ')
        save_directory = os.path.join(self.location, category)
        if not os.path.exists(save_directory):  # If category doesn't exist, make it
            os.makedirs(save_directory)
        title = input('Title: ')
        file_name = os.path.join(save_directory, title + '.html')
        print(''.center(80, '-'))

        # # message input
        # For message input use editor if editor is true otherwise use stdin.read()
        msg = 'failed to capture message'
        if not editor:
            print('Log:')
            msg = sys.stdin.read()
        else:
            with tempfile.NamedTemporaryFile(mode='w+t') as temp_file:
                print('<Log Input will be taken from editor: {}>'.format(editor))
                subprocess.call([editor, temp_file.name])
                while True:
                    with open(temp_file.name) as f:
                        contents = f.read()
                        if contents:
                            msg = contents
                            break
                print(msg)

        # If markdown convert to html
        print(''.center(80, '-'))
        if markdown and MARKDOWN:
            msg = markdown2.markdown(msg)
            print('|' + 'converting log message to html(from markdown)'.center(78, ' ') + '|')

        # Converting html (bells and whistles)
        if convert_img:
            print('|' + 'converting html message through filters:'.center(78, ' ') + '|')
            print('|' + '-{}'.format('localize image' if convert_img else '').center(78, ' ') + '|')
            msg = self.convert_html(msg, save_directory=save_directory, localize_img=convert_img)

        # Making the plog from the data
        print('|' + 'Saving plog <{}.html>'.format(title).center(78, ' ') + '|')
        print('|' + 'to {}'.format(save_directory).center(78, ' ') + '|')
        print(''.center(80, '_'))
        plog = self.make_log_html(msg=msg,
                                  cat=category,
                                  title=title,
                                  date=date)

        ## Saving to disk
        # Log
        with open(file_name, 'w') as html_file:
            html_file.write(plog)
        # Theme
        if not os.path.exists(os.path.join(save_directory, 'theme.css')) or override_theme:
            if override_theme:
                print('Overriding theme with newly generated one')
            self.write_theme(save_directory)
        # Cat Main
        self.write_cat_html(save_directory=save_directory)
        # Plogbook Main
        self.write_main_html(save_directory=self.location)
        # Theme for plogbook main
        if not os.path.exists(os.path.join(self.location, 'theme.css')) or override_theme:
            if override_theme:
                print('Overriding theme with newly generated one')
            self.write_theme(self.location)

    def read_teamplate(self, template):
        if template not in self.templates.keys():
            print('Invalid files argument "{}" for template writing,'
                  ' must be one of:\n{}'.format(template, ', '.join(self.templates.keys())))
            return None
        template_path = os.path.join(self.location, 'templates', template)

        if not os.path.exists(template_path):
            return None

        with open(template_path, 'r') as of:
            return of.read()

    def write_templates(self, save_directory=None, files=None, override=False):
        """
        Writes styles directory with default files if they are missing
        :param save_directory: where styles folder will be created
        :param override: Whether to override even if style already exist
        :param files: list of which files to override, from the following: theme, plog,category, category_item, main_page,
        main_page_item. None will write ALL.
        """
        if not save_directory:
            save_directory = self.location
        if not files:
            files = self.templates.keys()

        # Check template directory
        template_dir = os.path.join(save_directory, 'templates')
        if not os.path.exists(template_dir):
            os.makedirs(template_dir)

        # Check for invalid files
        for index, file in enumerate(files):
            if file not in self.templates.keys():
                print('Invalid files argument "{}" for template writing,'
                      ' must be one of:\n{}'.format(file, ', '.join(self.templates.keys())))
                del files[index]

        for file in files:
            file_path = os.path.join(template_dir, file)
            if not os.path.exists(file_path) or override:
                print('created:', file_path)
                with open(file_path, mode='w') as of:
                    of.write(self.templates[file])

    def write_theme(self, save_directory=None):
        """
        Generates and writes theme.css to save_directory
        """
        if not save_directory:
            save_directory = self.location
        with open(os.path.join(save_directory, 'theme.css'), 'w') as css_file:
            css_file.write(self.template_theme)

    def write_cat_html(self, save_directory):
        """
        Generates and writes main.html to save_directory
        """
        with open(os.path.join(save_directory, 'main.html'), 'w') as main:
            main.write(self.make_cat_html(directory=save_directory))

    def write_main_html(self, save_directory=None):
        """
        Generates and writes landing main.html for the whole plogbook to save_directory
        """
        if not save_directory:
            save_directory = self.location
        with open(os.path.join(save_directory, 'main.html'), 'w') as main:
            main.write(self.make_main_html(directory=save_directory))

    def make_main_html(self, directory=None):
        """
        Generates main.html for the plogbook.
        """
        if not directory:
            directory = self.location
        categories = self.find_categories(directory=directory, silent=True)
        categories = sorted(categories, key=lambda x: x.plog_count, reverse=True)
        items = []
        for index, cat in enumerate(categories):
            plog_count = cat.plog_count
            items.append(DEFAULT_MAIN_ITEM_FORMAT(template=self.template_main_item,
                                                  relative_location=quote(os.path.join(cat.name, 'main.html')),
                                                  name=cat.name,
                                                  count=plog_count,
                                                  date=cat.creation_date,
                                                  location=cat.location,
                                                  main_id=index + 1))
        items = '\n'.join(items)
        completed_main = DEFAULT_MAIN_FORMAT(template=self.template_main,items=items)
        return completed_main

    def make_cat_html(self, directory=None):
        """
        Generates main.html for a category
        :param directory: where to look for plogs if None will look in self.location
        """
        if not directory:
            directory = self.location
        found_plogs = self.find_plogs(directory=directory, silent=True, recursive=False)
        found_plogs = sorted(found_plogs, key=lambda x: x.date, reverse=True)
        items = []
        for index, plog in enumerate(found_plogs):
            items.append(DEFAULT_CAT_ITEM_FORMAT(template=self.template_cat_item,
                                                 cat_id=index + 1,
                                                 date=plog.date,
                                                 relative_location=quote(plog.title),
                                                 title=plog.title.replace('.html', ''),
                                                 location=plog.location))
        items = '\n'.join(items)
        completed_main = DEFAULT_CAT_FORMAT(template=self.template_cat, items=items)
        return completed_main

    def make_log_html(self, msg, cat, title, date):
        """
        Converts data to html fil.
        Turns all input new lines into paragraphs
        """
        msg = ''.join(['<p>{msg}</p>'.format(msg=msg) for msg in msg.split('\n')])
        log = DEFAULT_PLOG_FORMAT(template=self.template_plog, msg=msg, cat=cat, date=date, title=title)
        return log

    @staticmethod
    def convert_html(html, save_directory, localize_img=False):
        """
        Makes html text go through various conversions
        :param html: html string
        :param save_directory: directory where html file will be saved
        :param localize_img: localizes images in the source and store them in location/title/images/
        :return: updated html string
        """
        if localize_img:
            # Handle file location
            image_location = os.path.join(save_directory, 'images')
            if not os.path.exists(image_location):
                os.makedirs(image_location)
            # Find tags and replace them with new ones
            img_tags = re.findall('img.*?src="(.*?)"', html)
            for src in img_tags:
                new_src = ''.join(re.findall('(\w+|\.)', src))
                html.replace(src, new_src)
                # Downloading and saving
                with open(os.path.join(image_location, new_src), 'wb') as image_file:
                    image_source = urlopen(src).read()
                    image_file.write(image_source)
        return html

    def find_plogs(self, directory=None, recursive=True, pretty_output=False, silent=False):
        """
        Finds all possible plogs in in the current directory.
        :param directory: where to look for plogs, defaults to self.location.
        :param recursive (default True): whether to recursively walk through every directory.
        :param pretty_output: data will be printed in a pretty table.
        :param silent: no data will be printed.
        """
        # based on http://stackoverflow.com/a/2186565/3737009, upvote the man!
        if not directory:
            directory = self.location
        found = []
        if recursive:
            for root, dirnames, filenames in os.walk(directory):
                if 'theme.css' not in filenames:
                    continue
                for filename in fnmatch.filter(filenames, '*.html'):
                    if filename == 'main.html':
                        continue
                    found.append(Plog(location=os.path.join(root, filename),
                                      title=filename))
        else:
            only_files = fnmatch.filter(os.listdir(directory), '*.html')
            for file in only_files:
                if file == 'main.html':
                    continue
                found.append(Plog(location=os.path.join(directory, file)))

        if silent:
            return found
        if pretty_output:
            print(''.center(145, '-'))
            print('{}|{}|{}|{}'.format('Location'.ljust(80, ' '), 'Category'.center(20, ' '), 'Title'.center(20, ' '),
                                       'Date'.center(20, ' ')))
            print(''.center(145, '-'))
        for f in found:
            print(f.__str__(pretty=pretty_output))
        return found

    def find_categories(self, directory=None, pretty_output=False, silent=False):
        """finds plog categories in a directory
        :param directory: plogbook directory, defaults to self.location
        :param pretty_output: data will be printed in a pretty table.
        :param silent: no data will be printed.
        """
        if not directory:
            directory = self.location
        found = []
        folders = [fdir for fdir in os.listdir(directory) if os.path.isdir(os.path.join(directory, fdir))]
        for folder in folders:
            folder_items = os.listdir(os.path.join(directory, folder))
            if folder == 'templates':
                continue
            if 'theme.css' in folder_items:
                found_plogs = self.find_plogs(directory=os.path.join(directory, folder), silent=True)
                found.append(PlogCategory(name=folder,
                                          location=os.path.join(directory, folder),
                                          plog_files=found_plogs))

        if silent:
            return found
        if pretty_output:
            print(''.center(65, '-'))
            print('{}|{}|{}'.format('Name'.center(30, ' '), 'Plog Count'.center(15, ' '),
                                    'Creation Date'.center(30, ' ')))
            print(''.center(65, '-'))
        for f in found:
            print(f.__str__(pretty=pretty_output))
        return found


class Plog:
    """
    Storage and management class for a plog item.
    plog - is an .html file that is a table and contains title, date, category and log message
    """

    def __init__(self, location, category=None, title=None):
        """
        :param location: location of the plog on the hard-drive
        :param category: plog category, if not provided will be extracted from location
        :param title: name of the plog file
        """
        self.location = location
        self.title = title or os.path.split(self.location)[-1]
        self.category = category or os.path.split(os.path.split(self.location)[0])[-1]
        self.date = self.get_date()

    def __str__(self, pretty=False):
        if pretty:
            location = '...' + self.location.ljust(80, ' ')[-77::] \
                if len(self.location) > 80 else self.location.ljust(80, ' ')
            category = self.category.center(20, ' ')[:17] + '...' \
                if len(self.category) > 20 else self.category.center(20, ' ')
            title = self.title.center(20, ' ')[:17] + '...' \
                if len(self.title) > 20 else self.title.center(20, ' ')
            date = self.date.center(20, ' ')
            return u'{}|{}|{}|{}'.format(location, category, title, date)
        else:
            return u'{};{};{};{}'.format(self.location, self.category, self.title, self.date)

    def get_date(self):
        """finds the date when plog was created"""
        meta = os.stat(self.location)
        date = meta.st_ctime
        date = datetime.fromtimestamp(date)
        date = date.strftime('%x %X')
        return date


class PlogCategory:
    """
    Storage and management class for plog category.
    """

    def __init__(self, name, location, plog_files=None):
        """
        :param name: category name.
        :param location: location of the category on the hard-drive.
        :param plog_files: list of plog_file the category contains. If None will find plogs itself in "location".
        :return:
        """
        self.name = name
        self.location = location
        self.plog_files = plog_files or PlogBook.find_plogs(location)
        self.plog_count = len(self.plog_files)
        self.creation_date = self.get_date()

    def get_date(self):
        """finds the date when category was created"""
        meta = os.stat(self.location)
        date = meta.st_ctime
        date = datetime.fromtimestamp(date)
        date = date.strftime('%x %X')
        return date

    def __str__(self, pretty=False):
        if pretty:
            name = self.name.center(30, ' ')
            plog_count = str(self.plog_count).center(15, ' ')
            date = self.creation_date.center(30, ' ')
            return u'{}|{}|{}'.format(name, plog_count, date)
        else:
            return u'{};{};{}'.format(self.name, self.plog_count, self.creation_date)


def run_argparse():
    """
    Main running function which executes the whole sequence with arguments by using 'argparse' module.
    """
    parser = argparse.ArgumentParser(description='Personal Log Book')
    parser.add_argument('--open', '-o', help='[default] open the plogbook in your default browser', action='store_true')
    parser.add_argument('--write', '-w', help='write a plog', action='store_true')
    parser.add_argument('--build_templates', '-bts',
                        help='builds templates for easy editing that will be used instead of default values, located '
                             'in <plogbook>/templates', action='store_true')
    parser.add_argument('--build_template', '-bt', help='build a specific templates only', nargs='+')
    parser.add_argument('--override', help='override any files being created, i.e. with --build_templates',
                        action='store_true')
    parser.add_argument('--find', help='finds plogs in the current directory', action='store_true')
    parser.add_argument('--find_categories', help='finds all categories in a plogbook', action='store_true')
    parser.add_argument('--findr', help='finds plogs in the current directory recursively', action='store_true')
    parser.add_argument('--pretty', '-p', help='prettifies output of console output i.e. --find and --findr',
                        action='store_true')
    parser.add_argument('--override_theme', '-ot', help='override theme with new one', action='store_true')

    parser.add_argument('--rebuild_main', '-rbm', help='rebuild main plogbook page', action='store_true')
    parser.add_argument('--rebuild_main_theme', '-rbt', help='rebuild main plogbook page theme', action='store_true')
    parser.add_argument('--rebuild_cat_main', '-rbcm', help='rebuild category main')
    parser.add_argument('--rebuild_cat_theme', '-rbct', help='rebuild category theme')

    parser.add_argument('--localize_images', '-li', help='Localize images found in @src and store them in plog folder '
                                                         'under images/', action='store_true')

    parser.add_argument('--location', '-loc', help='location of the plogbook, if not provided defaults to '
                                                   'current working directory')
    parser.add_argument('--editor', '-e', help='what editor to use to input plog message, i.e. nano')
    parser.add_argument('--markdown', '-md', help='markdown to html conversion for plog message', action='store_true')

    args = parser.parse_args()

    plogbook = PlogBook(location=args.location)
    if not len(sys.argv) > 1 or args.open:
        # If plogbook main.html exists open it else write plog
        main_path = os.path.join(args.location or '', 'main.html')
        if os.path.exists(main_path):
            webbrowser.open(main_path)
        else:
            start_new = input("New plogbook will be started in this folder, are you sure?(y/n)")
            if 'y' in start_new.lower():
                print("Now to finish up initiating write your first plog!")
                args.write = True

    if args.build_template:
        plogbook.write_templates(files=args.build_template, override=args.override)
    if args.build_templates:
        print('creating templates that will be used by plogbook, check <plogbook>/templates')
        plogbook.write_templates(override=args.override)
    if args.write or args.editor:
        if args.markdown:
            if not MARKDOWN:
                print('You need to install package "markdown2" for markdown conversion support, '
                      'try: sudo pip install markdown2\nNo conversion will be made!')
                args.markdown = False
        plogbook.write_plog(editor=args.editor,
                            markdown=args.markdown,
                            convert_img=args.localize_images,
                            override_theme=args.override_theme)

    if args.find:
        plogbook.find_plogs(recursive=False, pretty_output=args.pretty)
    if args.findr:
        plogbook.find_plogs(recursive=True, pretty_output=args.pretty)
    if args.rebuild_cat_theme:
        print('rebuilding theme for category: {}'.format(args.rebuild_cat_theme))
        plogbook.write_theme(os.path.join(plogbook.location, args.rebuild_cat_theme))
    if args.rebuild_main_theme:
        print('rebuilding theme plogbook, loc: {}'.format(plogbook.location))
        plogbook.write_theme()
    if args.rebuild_cat_main:
        print('rebuilding category main page  for category: {}'.format(args.rebuild_category_main))
        plogbook.write_cat_html(os.path.join(plogbook.location, args.rebuild_category_main))
    if args.rebuild_main:
        print('rebuilding plogbook main page')
        plogbook.write_main_html()
    if args.find_categories:
        plogbook.find_categories(pretty_output=args.pretty)


if __name__ == '__main__':
    run_argparse()