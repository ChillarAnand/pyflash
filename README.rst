pyflash
=======

Get flash like super powers by automating everyday tasks!



Install
========

.. code-block:: shell

    $ pip install pyflash

flash needs several third party packages depending on the command being used. Packages which are available on PyPi will get installed as a requirements. sortphotos_, ocropy_ are not available on PyPi. You have to download them and add them to your python path.

.. _sortphotos: https://github.com/andrewning/sortphotos
.. _ocropy: https://github.com/tmbdev/ocropy


For otp command to work, we have to setup a `~/.pyflash.ini` file in the following format.


.. code-block:: shell

    [otp]
    gmail = secret_code_for_gmail
    twitter = secret_code_for_twitter


Usage
=========

.. code-block:: shell

    Usage: flash [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      adb_connect         Scan network and connect to adb via network.
      download_book       Search and download book by name
      download_imd_data   Download IMD data for given range.
      download_subtitles  Download subtitles for videos in a directory.
      fix_build           Fix a failing CI build.
      fix_imports         Fix imports in a python project.
      ipa_install         Resign & install iOS apps.
      nsedb               Create/Sync NSE stocks OHLC data.
      ocr                 Run given OCR engine on given image.
      organize_books      Organize books in a specified directory.
      organize_downloads  Organize downloaded files.
      organize_photos     Organize photos by date.
      otp                 Show OTP
      pg_stats            Show stats for postgres database.
      procfile            Start processes in Procfile
      rate_movies         Show IMDb/RT ratings for movies and series.
      rent_receipts       Generate monthly rent receipts for a given...
      send_to_kindle      Send books to kindle via Dropbox/IFTTT.
      split_pdf           Split pdf horizontally/vertically.
      validate_aadhaar    Check if given AADHAAR number is valid.



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
