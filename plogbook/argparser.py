import argparse
import os
import sys
import webbrowser

# # multi-versioning
VERSION = sys.version_info[0]
IS_3 = True if VERSION == 3 else False
if IS_3:
    input = input
else:
    input = raw_input
from plogbook.book import PlogBook, MARKDOWN


def run_argparse():
    """
    Main running function which executes the whole sequence with arguments by using 'argparse' module.
    """
    parser = argparse.ArgumentParser(description='Personal Log Book')
    parser.add_argument('--open', '-o', help='[default] open the Plogbook in your default browser', action='store_true')
    parser.add_argument('--write', '-w', help='write a plog', action='store_true')
    parser.add_argument('--build_templates', '-bts',
                        help='builds templates for easy editing that will be used instead of default values, located '
                             'in <Plogbook>/templates', action='store_true')
    parser.add_argument('--build_template', '-bt', help='build a specific templates only', nargs='+')
    parser.add_argument('--override', help='override any files being created, i.e. with --build_templates',
                        action='store_true')
    parser.add_argument('--find', help='finds plogs in the current directory', action='store_true')
    parser.add_argument('--find_categories', help='finds all categories in a Plogbook', action='store_true')
    parser.add_argument('--findr', help='finds plogs in the current directory recursively', action='store_true')
    parser.add_argument('--pretty', '-p', help='prettifies output of console output i.e. --find and --findr',
                        action='store_true')
    parser.add_argument('--override_theme', '-ot', help='override theme with new one', action='store_true')

    parser.add_argument('--rebuild_main', '-rbm', help='rebuild main Plogbook page', action='store_true')
    parser.add_argument('--rebuild_main_theme', '-rbt', help='rebuild main Plogbook page theme', action='store_true')
    parser.add_argument('--rebuild_cat_main', '-rbcm', help='rebuild category main')
    parser.add_argument('--rebuild_cat_theme', '-rbct', help='rebuild category theme')

    parser.add_argument('--localize_images', '-li', help='Localize images found in @src and store them in plog folder '
                                                         'under images/', action='store_true')

    parser.add_argument('--location', '-loc', help='location of the Plogbook, if not provided defaults to '
                                                   'current working directory')
    parser.add_argument('--editor', '-e', help='what editor to use to input plog message, i.e. nano')
    parser.add_argument('--markdown', '-md', help='markdown to html conversion for plog message', action='store_true')

    args = parser.parse_args()

    plogbook = PlogBook(location=args.location)
    if len(sys.argv) < 2 or args.open or (args.location and (len(sys.argv) < 4)):
        # If Plogbook main.html exists open it else write plog
        main_path = os.path.join(args.location or '', 'main.html')
        if os.path.exists(main_path):
            webbrowser.open(main_path)
        else:
            start_new = input("New Plogbook will be started in this folder, are you sure?(y/n)")
            if 'y' in start_new.lower():
                print("Now to finish up initiating write your first plog!")
                args.write = True

    if args.build_template:
        plogbook.write_templates(files=args.build_template, override=args.override)
    if args.build_templates:
        print('creating templates that will be used by Plogbook, check <Plogbook>/templates')
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
        print('rebuilding theme Plogbook, loc: {}'.format(plogbook.location))
        plogbook.write_theme()
    if args.rebuild_cat_main:
        print('rebuilding category main page  for category: {}'.format(args.rebuild_cat_main))
        plogbook.write_cat_html(os.path.join(plogbook.location, args.rebuild_cat_main))
    if args.rebuild_main:
        print('rebuilding Plogbook main page')
        plogbook.write_main_html()
    if args.find_categories:
        plogbook.find_categories(pretty_output=args.pretty)
