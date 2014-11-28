#!/usr/bin/env python2
from __future__ import print_function
import os
import sys
import fnmatch
import argparse
import tempfile
import subprocess
from datetime import datetime
try:
    import markdown2
except ImportError:
    MARKDOWN = False
else:
    MARKDOWN = True

__author__ = 'Granitosaurus Dex'
# multiversioning
VERSION = sys.version_info[0]
IS_3 = True if VERSION == 3 else False
input = input if IS_3 else raw_input

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

    table, td, th {
        border: 1px solid black;
        padding: 5px;
    }

    th {
        text-align: left;
        width: 100px;
    }

    th#title_header, th#msg_header, td#title, td#msg {
        background-color: #0b0b0b;
    }

    td#msg, th#msg_header {
        background-color: #0f0f0f;
    }
"""
DEFAULT_FORMAT = lambda msg, cat, date, title: DEFAULT_HTML.format(msg=msg, cat=cat, date=date, title=title)
DEFAULT_HTML = """
<!--default template for a plog-->
        <head>
        <link rel="stylesheet" type="text/css" href="theme.css">
        </head>
        <table>
        <tr>
            <th class='meta_header'>
            Category:
            </th>
            <td class='meta_text'>
            {cat}
            </td>
        </tr>
        <tr>
            <th class='meta_header'>
            Date:
            </th>
            <td class='meta_text'>
            {date}
            </td>
        </tr>
        <tr>
            <th id='title_header'>
            Title:
            </th>
            <td id='title'>
            {title}
            </td>
        </tr>
        <tr>
            <th id='msg_header'>
            Log:
            </th>
            <td id='msg'>
            {msg}
            </td>
        </tr>
        </table>
"""
#----------------------------------------------------------------------------------------------------------------------


class PlogBookLite:
    """
    This is main class for plogbook log book
    """

    def __init__(self, location=None):
        self.location = location or os.getcwd()

    def write_plog(self, editor=False, markdown=False):
        """
        This method is the main method that is runned to start the process of recording the plog
        """
        # Data Input and formatting
        date = datetime.now().strftime('%x-%X')
        print(''.center(80, '_'))
        print('|' + 'Writting Plog for {}'.format(date).center(78) + '|')
        print(''.center(80, '-'))
        category = input('Category: ')
        title = input('Title: ')
        print(''.center(80, '-'))
        if not editor:
            print('Log:')
            msg = sys.stdin.read()
        else:
            f = tempfile.NamedTemporaryFile(mode='w+t', delete=False)
            n = f.name
            f.close()
            print('Log Input will be taken from editor: {}'.format(editor))
            subprocess.call([editor, n])
            with open(n) as f:
                msg = f.read()
        # If markdown convert to html
        print(''.center(80, '-'))
        if markdown and MARKDOWN:
            msg = markdown2.markdown(msg)
        # Writing to disk
        save_directory = os.path.join(self.location, category)
        if MARKDOWN and markdown:
            print('|' + 'converting log message to html(from markdown)'.center(78, ' ') + '|')
        print('|' + 'Saving plog <{}.html>'.format(title).center(78, ' ') + '|')
        print('|' + 'to {}'.format(save_directory).center(78, ' ') + '|')
        print(''.center(80, '_'))
        # Making the plog from the data
        plog = self.make_log_html(msg=msg,
                                  cat=category,
                                  title=title,
                                  date=date)

        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        with open(os.path.join(save_directory, title + '.html'), 'w') as html_file:
            html_file.write(plog)
        if not os.path.exists(os.path.join(save_directory, 'theme.css')):
            with open(os.path.join(save_directory, 'theme.css'), 'w') as css_file:
                css_file.write(DEFAULT_CSS)


    @staticmethod
    def make_log_html(msg, cat, title, date):
        """
        Converts data to html file
        """
        msg = ''.join(['<p>{msg}</p>'.format(msg=msg) for msg in msg.split('\n')])
        log = DEFAULT_FORMAT(msg=msg, cat=cat, date=date, title=title)
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
        plogbook.write_plog(editor=args.editor, markdown=args.markdown)

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