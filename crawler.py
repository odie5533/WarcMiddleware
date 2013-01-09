"""
Provides a simple interface to command the simplespider Scrapy spider.
"""
import argparse

import scrapy.cmdline

parser = argparse.ArgumentParser(description='Command-line Scrapy crawler')
parser.add_argument('-u', '--url', dest='urls', help='Comma-separated list of urls to crawl.')
parser.add_argument('-m', '--mirror', action='store_true', help="Crawl all internal anchor links on the first url's domain.")
parser.add_argument('-a', '--accept', dest='reg_accept',
                    help='Crawl only anchor links which match supplied comma-separated regular expressions.')
parser.add_argument('-x', '--reject', dest='reg_reject',
                    help='Do not crawl anchor links which match supplied comma-separated regular expressions.')
parser.add_argument('-D', '--domains',
                    help='Crawl only anchor links on the specified domains. Overrides -a.')
parser.add_argument('--url-file', help='File containing a list of urls to crawl.')
parser.add_argument('--sitemap', help='File containing a sitemap to crawl.')
args = parser.parse_args()

cmds = ['scrapy', 'crawl', 'simplespider']

if args.urls is not None:
    cmds.extend(['-a', 'urls=%s' % args.urls])
if args.url_file is not None:
    cmds.extend(['-a', 'url_file=%s' % args.url_file])
if args.sitemap is not None:
    cmds.extend(['-a', 'sitemap=%s' % args.sitemap])
if args.reg_accept is not None:
    cmds.extend(['-a', 'reg_accept=%s' % args.reg_accept])
if args.reg_reject is not None:
    cmds.extend(['-a', 'reg_reject=%s' % args.reg_reject])
if args.mirror:
    cmds.extend(['-a', 'mirror=true'])

if len(cmds) == 3:
    parser.print_help()
else:
    scrapy.cmdline.execute(cmds)
