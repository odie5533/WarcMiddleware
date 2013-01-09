WarcMiddleware
==============
WarcMiddleware is a library that lets users save mirror backups of websites to
their computer. It is an addon for the Python web crawler Scrapy that saves
web server transactions (requests and responses) into a Web ARChive (WARC) file
(ISO 28500). The transactions can then be played back or viewed, similar
to using Archive.org's WayBackMachine. The WARC format is a standard method of
saving these transactions.

There are two ways to use WarcMiddleware: (1) as a replacement ClientFactory or
(2) as a DownloaderMiddleware. The former is recommended. As a ClientFactory,
WarcMiddleware hooks into Scrapy's HTTP class and saves the raw requests and
responses. The DownloaderMiddleware version configures itself to save the
requests and responses that Scrapy sends it. The problem with this method is
that Scrapy does not pass along the raw data and some of it is lost along the
way.

Prerequisites
=============
WarcMiddleware requires:

* [Scrapy](http://scrapy.org/)
 * [Python Imaging Library](http://www.pythonware.com/products/pil/)
 * [lxml](http://pypi.python.org/pypi/lxml/)
 * [Twisted](http://twistedmatrix.com/trac/)
     * [zope.interface](http://pypi.python.org/pypi/zope.interface)
     * [OpenSSL](http://slproweb.com/products/Win32OpenSSL.html)
     * [pyOpenSSL](https://launchpad.net/pyopenssl)

For Windows, many of these packages can be downloaded from
<http://www.lfd.uci.edu/~gohlke/pythonlibs/>.

Simple examples
===============
The entire github repository serves as an example project which will download
a website and save it as a WARC file. To try it, download the repository as a
zip file and extract it. After installing the prerequisites listed above, run:

    $ crawler.py --url http://www.eurogamer.net/

Scrapy will save the website into a file named out.warc.gz

Sitemap.xml archiving
---------------------
The crawler supports downloading urls from a sitemap.xml file.
As an example, this can be used to download all the posts from a Blogspot site.
To get the sitemap.xml from a Blogspot site, append "sitemap.xml" to the url and
save the file.

    http://dogs.blogspot.com/sitemap.xml

Crawl the sitemap using:

    $ crawler.py --sitemap sitemap.xml

Scrapy will save the website contents into a file name out.warc.gz

Mirroring a domain
------------------
The crawler supports crawling an entire domain or many domains.

If crawling a single domain, use:

    $ crawler.py --mirror --url http://example.com

Using --mirror is the same as using `--domains example.com`.

For multiple domains, the following will crawl anchor links on example.com that
lead to example.com or to othersite.com. And from othersite.com, it will crawl
anchor links that lead to either:

    $ crawler.py --domains example.com,othersite.com --url http://example.com

Note that using `--domains` will override `--mirror`.

Regular Expression crawling
---------------------------
The --accept and --reject parameters affect whether or not each anchor link on a
site is crawled. Each accepts a comma-separated list of regular expressions that
should either be crawled or never crawled. This does not affect downloading
external assets such as images or CSS files.

This example will not crawl anchor links that contain the string `/search/?`:

    $ crawler.py --mirror --reject /search/\? --url http://example.com

Crawling urls from a file
-------------------------
A file containing a list of urls, one per line, can be supplied:

    $ crawler.py --url-file index.txt

The crawler uses these urls as though they were supplied to the --url argument.
If no further arguments are given, the crawler will archive each url as well
as any external assets for that url, but will not crawl any anchor links. If
`--domains` is added, then it will crawl any anchor links matching the specified
domains. If `--mirror` is used instead of domains, then it will only crawl
anchor links that are on the domain of the first url in the file.

How to view WARC files
======================
After creating a WARC file, the contents can be played back allowing the user
to view the saved website. One way to view the saved site is to use [warc-proxy](https://github.com/alard/warc-proxy).
Warc-proxy creates a proxy that channels traffic from a web browser and responds
to requests to view websites. Rather than sending the live website, warc-proxy
sends back the saved website contents from the WARC file.

Usage in other Scrapy projects
==============================
A Scrapy project is needed to use WarcMiddleware. To create one, from a command
prompt run:

    $ scrapy startproject crawltest

This will create a crawltest directory (dir) with another crawltest dir inside.

After this, choose one of the following methods to use WarcMiddleware.

WarcClientFactory
-----------------
Copy warcclientfactory.py and warcrecords.py next to scrapy.cfg in the outer
crawltest dir. Also copy over the hanzo dir to the outer dir.

In the inner dir, open settings.py and add the following lines to the bottom:

    DOWNLOADER_HTTPCLIENTFACTORY = 'warcclientfactory.WarcHTTPClientFactory'

This will enable the custom WarcMiddleware ClientFactory. Additionally, create
a simple spider by copying the 
[simplespider.py](https://github.com/iramari/WarcMiddleware/blob/master/crawltest/spiders/simplespider.py)
file into the spiders dir.

Finally, to start the spider, from a command prompt in the outer dir run:

    $ scrapy crawl simplespider -a url=http://www.eurogamer.net/

This should output a WARC file named out.warc.gz

DownloaderMiddleware
--------------------
Copy warcmiddleware.py and warcrecords.py next to scrapy.cfg in the outer
crawltest dir. Also copy over the hanzo dir to the outer dir.

In the inner dir, open settings.py and add the following lines to the bottom:

    DOWNLOADER_MIDDLEWARES = {'warcmiddleware.WarcMiddleware': 820}

This will enable the WarcMiddleware. Additionally, create a simple spider by
copying the
[simplespider.py](https://github.com/iramari/WarcMiddleware/blob/master/crawltest/spiders/simplespider.py)
file into the spiders dir.

Finally, to start the spider, from a command prompt in the outer dir run:

    $ scrapy crawl simplespider -a url=http://www.eurogamer.net/

This should output a WARC file named out.warc.gz
