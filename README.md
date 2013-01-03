WarcMiddleware
==============
WarcMiddleware lets users seamlessly download a mirror copy of a website when
running a web crawl with the Python web crawler Scrapy. WarcMiddleware is a
DownloaderMiddleware for Scrapy that saves a web crawl to a Web ARChive (WARC)
file (ISO 28500).

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

Example project
===============
The entire github directory serves as an example project which will download
a website and save it as a WARC file. To try it, download the repository as a
zip file and extract it. After installing the prerequisites listed above, run:

    $ scrapy crawl simplespider

Scrapy will then save the website into a file named out.warc.

Usage in other Scrapy projects
==============================
A Scrapy project is needed to use WarcMiddleware. To create one, from a command
prompt run:

    $ scrapy startproject crawltest

This will create a crawltest directory (dir) with another crawltest dir inside.
Copy warcmiddleware.py and warcrecords.py next to scrapy.cfg in the outer
crawltest dir. Also copy over the hanzo dir to the outer dir.

In the inner dir, open settings.py and add the following lines to the bottom:

    DOWNLOADER_MIDDLEWARES = {'warcmiddleware.WarcMiddleware': 543}
    ITEM_PIPELINES = ['scrapy.contrib.pipeline.images.ImagesPipeline']
    IMAGES_STORE = './images'

This will enable the WarcMiddleware and enable image downloading. Additionally,
create a simple spider by copying the
[simplespider.py](https://github.com/iramari/WarcMiddleware/blob/master/crawltest/spiders/simplespider.py)
file into the spiders dir.
Finally, to start the spider, from a command prompt in the outer dir run:

    $ scrapy crawl simplespider

This should output an images dir and a WARC file named out.warc.