#!/usr/bin/env python2
from __future__ import print_function
import os
import re
import sys
import fnmatch
import tempfile
import subprocess

from datetime import datetime

# import Plogbook

# # External package import (things that don't come with python and are optional)
# Markdown2 is for markdown to html conversion
# from plog import Plog
from plogbook.plog import Plog


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


class PlogBook:
    """
    This is main class for Plogbook log book
    """
    templates = ['theme.css', 'plog.html', 'category.html', 'category_item.html', 'main.html', 'main_item.html']

    def __init__(self, location=None):
        """
        :param location: location of the Plogbook, if not provided current working directory will be taken
        """
        self.location = location or os.getcwd()
        self.template_theme = self.read_teamplate('theme.css') or self.read_default_template('theme.css')
        self.template_plog = self.read_teamplate('plog.html') or self.read_default_template('plog.html')
        self.template_cat = self.read_teamplate('category.html') or self.read_default_template('category.html')
        self.template_cat_item = self.read_teamplate('category_item.html') or self.read_default_template('category_item.html')
        self.template_main = self.read_teamplate('main.html') or self.read_default_template('main.html')
        self.template_main_item = self.read_teamplate('main_item.html') or self.read_default_template('main_item.html')

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
        # Theme for Plogbook main
        if not os.path.exists(os.path.join(self.location, 'theme.css')) or override_theme:
            if override_theme:
                print('Overriding theme with newly generated one')
            self.write_theme(self.location)

    def read_teamplate(self, template):
        """
        Reads the template if it doesn't exist returns None
        :param template: template file name, i.e. theme.css, see self.templates for full names
        :return: Template file content or None
        """
        if template not in self.templates:
            print('Invalid files argument "{}" for template writing,'
                  ' must be one of:\n{}'.format(template, ', '.join(self.templates)))
            return None
        template_path = os.path.join(self.location, 'templates', template)

        if not os.path.exists(template_path):
            return None

        with open(template_path, 'r') as of:
            return of.read()

    def read_default_template(self, template):
        """
        Returns default template read from "default_styles" directory
        :param template: template name see, self.templates or default_styles directory for all possible names
        :return: returns template file contents.
        """
        template_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'default_styles', template)
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
            files = self.templates

        # Check template directory
        template_dir = os.path.join(save_directory, 'templates')
        if not os.path.exists(template_dir):
            os.makedirs(template_dir)

        # Check for invalid files
        for index, file in enumerate(files):
            if file not in self.templates:
                print('Invalid files argument "{}" for template writing,'
                      ' must be one of:\n{}'.format(file, ', '.join(self.templates)))
                del files[index]

        for file in files:
            file_path = os.path.join(template_dir, file)
            if not os.path.exists(file_path) or override:
                print('created:', file_path)
                with open(file_path, mode='w') as of:
                    of.write(self.read_default_template(file))

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
        Generates and writes landing main.html for the whole Plogbook to save_directory
        """
        if not save_directory:
            save_directory = self.location
        with open(os.path.join(save_directory, 'main.html'), 'w') as main:
            main.write(self.make_main_html(directory=save_directory))

    def make_main_html(self, directory=None):
        """
        Generates main.html for the Plogbook.
        """
        if not directory:
            directory = self.location
        categories = self.find_categories(directory=directory, silent=True)
        categories = sorted(categories, key=lambda x: x.plog_count, reverse=True)
        items = []
        for index, cat in enumerate(categories):
            plog_count = cat.plog_count
            items.append(self.template_main_item.format(template=self.template_main_item,
                                                        relative_location=quote(os.path.join(cat.name, 'main.html')),
                                                        name=cat.name,
                                                        count=plog_count,
                                                        date=cat.creation_date,
                                                        location=cat.location,
                                                        main_id=index + 1))
        items = '\n'.join(items)
        completed_main = self.template_main.format(template=self.template_main,items=items)
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
            items.append(self.template_cat_item.format(template=self.template_cat_item,
                                                       cat_id=index + 1,
                                                       date=plog.date,
                                                       relative_location=quote(plog.title),
                                                       title=plog.title.replace('.html', ''),
                                                       location=plog.location))
        items = '\n'.join(items)
        completed_main = self.template_cat.format(template=self.template_cat, items=items)
        return completed_main

    def make_log_html(self, msg, cat, title, date):
        """
        Converts data to html fil.
        Turns all input new lines into paragraphs
        """
        msg = ''.join(['<p>{msg}</p>'.format(msg=msg) for msg in msg.split('\n')])
        log = self.template_plog.format(template=self.template_plog, msg=msg, cat=cat, date=date, title=title)
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
        :param directory: Plogbook directory, defaults to self.location
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
