Preface
=======
I recommend installing WarcMiddleware in a virtual environment using virtualenv.
It does work without using one, but it will probably save you headaches later.
Please note that WarcMiddleware requires Scrapy v0.16.3 and requires Twisted
v12.2.0. It will not work with later versions.

Setting up the virtualenv
=========================
If you don't already have virtualenv installed, run: `pip install virtualenv`

To setup the virtual environment on Windows:

    virtualenv warcm_env\virt1 --no-site-packages
    cd warcm_env
    virt1\Scripts\activate

And on Linux:

    virtualenv warcm_env/virt1 --no-site-packages
    cd warcm_env
    source virt1/bin/activate

Linux / OS X Installation
=========================
If you are using Linux or OS X, you should be able to just run
`pip install -r pip_requirements.txt` and skip the rest of this document.

Windows Installation
====================
Download [Twisted-12.2.0.win32-py2.7.exe](http://twistedmatrix.com/Releases/Twisted/12.2/Twisted-12.2.0.win32-py2.7.exe)
and install with:

    easy_install Twisted-12.2.0.win32-py2.7.exe

Download [lxml-3.2.3.win32-py2.7.exe](https://pypi.python.org/pypi/lxml/3.2.3)
and install with:

    easy_install lxml-3.2.3.win32-py2.7.exe

Download pywin32 [pywin32-218.win32-py2.7.exe](http://sourceforge.net/projects/pywin32/files/pywin32/Build%20218/)
and install with:

    easy_install pywin32-218.win32-py2.7.exe

Install egenix-pyOpenSSL by running:

    easy_install -i https://downloads.egenix.com/python/index/ucs2/ egenix-pyopenssl

Install Scrapy:

    pip install w3lib queuelib
    pip install --no-deps scrapy==0.16.3

If you are using Windows, make sure you call crawler.py as `python crawler.py`
and not just `crawler.py`. The latter will use the Windows handler and open it
in Python outside the virtual environment.

You should now be able to run the examples and start using WarcMiddleware.