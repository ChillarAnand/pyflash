pyflash
=======

Get flash like super powers by automating everyday tasks!



Install
========

.. code-block:: shell

    $ pip install pyflash


Quickstart
==========

.. code-block:: shell

    $ pyflash --help
    $ python -m pyflash --help


Commands
=========


python-version-readiness
--------------------------

This command is useful to detect the python version readiness when compared to top 5000 most downloaded PyPI packages.

.. code-block:: shell

    # Command to download and install top 300 packages for the given python version and generate a log file
    $ flash python-version-readiness --python /usr/local/bin/python3.10 --number 300


    # Show top 10 lines of the log file
    $ head -n 11 pvr.python3.10.log
    [
      {
         "download_count": 267740673,
         "project": "boto3",
         "is_ready": true
      },
      {
        "download_count": 203850147,
        "project": "botocore",
        "is_ready": true
      },


    # Show packages that are failed to install
    $ grep false -C 1 pvr.python3.10.log
        "project": "pyodbc",
        "is_ready": false
      },
      --
        "project": "tensorflow",
        "is_ready": false
      },
      --
        "project": "backports-zoneinfo",
        "is_ready": false
      },
      --


otp
----

This command is used to generate OTP for 2 factor authentication.

Setup a file called `~/.pyflash.ini` and then run `otp` command.


.. code-block:: shell

    $ cat ~/.pyflash.ini
    [otp]
    gmail = secret_key_of_gmail
    vault = secret_key_of_vault

    $ python -m pyflash otp
    gmail: 282910
    vault: 420529


Note
------

flash needs several third party packages depending on the command being used. Packages which are available on PyPi will get installed as a requirements. sortphotos_, ocropy_ are not available on PyPi. You have to download them and add them to your python path.

.. _sortphotos: https://github.com/andrewning/sortphotos
.. _ocropy: https://github.com/tmbdev/ocropy



Help
======

.. code-block:: shell

    Usage: python -m pyflash [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      adb-connect               Scan network and connect to adb via network.
      download-book             Search and download book by name
      download-imd-data         Download IMD data for given range.
      download-subtitles        Download subtitles for videos in a directory.
      fix-build                 Fix a failing CI build.
      fix-imports               Fix imports in a python project.
      ipa-install               Resign & install iOS apps.
      nsedb                     Create/Sync NSE stocks OHLC data.
      ocr                       Run given OCR engine on given image.
      organize-books            Organize books in a specified directory.
      organize-downloads        Organize downloaded files.
      organize-photos           Organize photos by date.
      otp                       Show OTP
      pg-stats                  Show stats for postgres database.
      procfile                  Start processes in Procfile
      python-version-readiness  Show version readiness of top python packages.
      rate-movies               Show IMDb/RT ratings for movies and series.
      rent-receipts             Generate monthly rent receipts for a given FY.
      send-to-kindle            Send books to kindle via Dropbox/IFTTT.
      split-pdf                 Split pdf horizontally/vertically.
      validate-aadhaar          Check if given AADHAAR number is valid or not.
