#!/usr/bin/env python3
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
try:
    import markdown2
except ImportError:
    MARKDOWN = False
else:
    MARKDOWN = True

# # multiversioning
VERSION = sys.version_info[0]
IS_3 = True if VERSION == 3 else False
if IS_3:
    from urllib.request import urlopen

    input = input
else:
    from urllib2 import urlopen

    input = raw_input

# ---------------------------------------------------------------------------------------------------------------------
# EDIT these to change css and html.
# Note if you change DEFAULT_HTML be sure to check the DEFAULT_FORMAT lambda function which fills up the plog
# ---------------------------------------------------------------------------------------------------------------------
DEFAULT_CSS = """
/*Default css for plogbook*/
    body {
        background-color: black;
        font-family: "Monospace", monospace, monospace;
        color: lawngreen;
    }

    table {
        width: 60%;
        margin-top: 50px;
        margin-left: 15%;
        margin-right: 15%;
        border-collapse: collapse;
        background-color: #0b0b0b;
    }
    <!-- this is more flexible even though ugly -->
    table#plog_table, td#category_value, th#category_header, td#date_value, th#date_header,
    td#title_value, th#title_header, td#msg_value, th#msg_header {
        border: 1px solid black;
        padding: 5px;
    }

    th {
        text-align: left;
        width: 100px;
    }

    td#msg_value, th#msg_header {
        background-color: #0f0f0f;
    }

    th.main_header {
    background-color: #0f0f0f;
    border: 1px solid black;
        padding: 5px;
    }
"""
DEFAULT_HTML_FORMAT = lambda msg, cat, date, title: DEFAULT_HTML.format(msg=msg, cat=cat, date=date, title=title)
DEFAULT_HTML = """
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
DEFAULT_MAIN_FORMAT = lambda items: DEFAULT_MAIN.format(msg=items)
DEFAULT_MAIN = """
<!--default template for a plog-->
<head>
    <link rel="stylesheet" type="text/css" href="theme.css">
</head>
<table id='main_table'>
    <tr>
        <th class='main_header'>
            Entry #
        </th>
        <th class='main_header'>
            Date
        </th>
        <th class='main_header'>
            Title
        </th>
        <th class='main_header'>
            Location
        </th>
    </tr>
    {items}
</table>
"""
DEFAULT_MAIN_ITEM_FORMAT = lambda entry, date, relative_loation, title, location: \
    DEFAULT_MAIN_ITEM.format(entry=entry, date=date, relative_loation=relative_loation, title=title, location=location)
DEFAULT_MAIN_ITEM = """
    <tr>
        <td id='header_entry'>
            {entry}
        </td>
        <td id='date_entry'>
            {date}
        </td>
        <td id='title_entry'>
            <a href='{relative_location}'>{title}</a>
        </td>
        <td id='location_entry'>
            {location}
        </td>
    </tr>
"""
#----------------------------------------------------------------------------------------------------------------------


class PlogBookLite:
    """
    This is main class for plogbook log book
    """

    def __init__(self, location=None):
        self.location = location or os.getcwd()

    def write_plog(self, editor=False, markdown=False, convert_img=False):
        """
        This method is the main method that is runned to start the process of recording the plog
        """
        # Data Input and formatting
        date = datetime.now().strftime('%x-%X')
        print(''.center(80, '_'))
        print('|' + 'Writting Plog for {}'.format(date).center(78) + '|')
        print(''.center(80, '-'))
        category = input('Category: ')
        save_directory = os.path.join(self.location, category)
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        title = input('Title: ')
        file_name = os.path.join(save_directory, title + '.html')
        print(''.center(80, '-'))

        ## message input
        # For message input use editor if editor is true otherwise use stdin.read()
        if not editor:
            print('Log:')
            msg = sys.stdin.read()
        else:
            with tempfile.NamedTemporaryFile(mode='w+t') as temp_file:
                print('Log Input will be taken from editor: {}'.format(editor))
                subprocess.call([editor, temp_file.name])
                while True:
                    with open(temp_file.name) as f:
                        contents = f.read()
                        if contents:
                            msg = contents
                            break

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

        # Saving to disk
        with open(file_name, 'w') as html_file:
            html_file.write(plog)
        if not os.path.exists(os.path.join(save_directory, 'theme.css')):
            with open(os.path.join(save_directory, 'theme.css'), 'w') as css_file:
                css_file.write(DEFAULT_CSS)

    def convert_html(self, html, save_directory, localize_img=False):
        """
        Makes html text go through various conversions
        :param html: html string
        :param save_directory: directory where html file will be saved
        :param localize_img: localizes images in the source and store them in location/title/images/
        :return: updated html string
        """
        if localize_img:
            #Handle file location
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


    @staticmethod
    def make_log_html(msg, cat, title, date):
        """
        Converts data to html fil.
        Turns all input new lines into paragraphs
        """
        msg = ''.join(['<p>{msg}</p>'.format(msg=msg) for msg in msg.split('\n')])
        log = DEFAULT_HTML_FORMAT(msg=msg, cat=cat, date=date, title=title)
        return log

    def find_plogs(self, recursive=True, pretty_output=False):
        """
        Finds all possible plogs in in the current directory
        :param recursive (default True): whether to recursively walk through every directory
        """
        #based on http://stackoverflow.com/a/2186565/3737009, upvote the man!
        found = []
        if recursive:
            for root, dirnames, filenames in os.walk(self.location):
                if 'theme.css' not in filenames:
                    continue
                for filename in fnmatch.filter(filenames, '*.html'):
                    found.append(Plog(location=os.path.join(root, filename),
                                      title=filename))
        else:
            only_files = fnmatch.filter(os.listdir(self.location), '*.html')
            for file in only_files:
                found.append(Plog(location=os.path.join(self.location, file)))

        if pretty_output:
            print(''.center(145, '-'))
            print('{}|{}|{}|{}'.format('Location'.ljust(80, ' '), 'Category'.center(20, ' '), 'Title'.center(20, ' '),
                                       'Date'.center(20, ' ')))
            print(''.center(145, '-'))
        for f in found:
            print(f.__str__(pretty=pretty_output))


class Plog:
    """
    Storage and management class for a log item.
    """

    def __init__(self, location, category=None, title=None):
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
        meta = os.stat(self.location)
        date = meta.st_ctime
        date = datetime.fromtimestamp(date)
        date = date.strftime('%x %X')
        return date


def run():
    """
    Main running function which executes the whole sequence with arguments.
    """
    parser = argparse.ArgumentParser(description='Personal Log Book')
    parser.add_argument('--write', '-w', help='[default] write a plog', action='store_true')
    parser.add_argument('--markdown', '-md', help='markdown to html conversion for plog message', action='store_true')
    parser.add_argument('--localize_images', '-li', help='Localizes images found in @src and store them in plog folder '
                                                         'under images', action='store_true')
    parser.add_argument('--find', help='finds plogs in the curent directory', action='store_true')
    parser.add_argument('--findr', help='finds plogs in the curent directory recursively', action='store_true')
    parser.add_argument('--pretty', '-p', help='prettiefies output of --find and --findr', action='store_true')
    parser.add_argument('--location', '-loc', help='location of the plogbook')
    parser.add_argument('--editor', '-e', help='what editor to use to input plog message')
    args = parser.parse_args()

    plogbook = PlogBookLite(location=args.location)
    if not len(sys.argv) > 1 or args.write:
        if args.markdown:
            if not MARKDOWN:
                print('You need to install package "markdown2" for markdown conversion support, '
                      'try: sudo pip install markdown2\nNo conversion will be made!')
                args.markdown = False
        plogbook.write_plog(editor=args.editor, markdown=args.markdown, convert_img=args.localize_images)

    if args.find:
        plogbook.find_plogs(recursive=False, pretty_output=args.pretty)
    if args.findr:
        plogbook.find_plogs(recursive=True, pretty_output=args.pretty)


if __name__ == '__main__':
    run()
    # pb = PlogBookLite()
    #
    #
    # # pb.write_plog()
    # pb.find_plogs(recursive=True)