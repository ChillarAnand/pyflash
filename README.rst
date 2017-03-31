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
      ocr                 Run given OCR engine on given image.
      organize_books      Organize books in a specified directory.
      organize_downloads  Organize downloaded files.
      organize_photos     Organize photos by date.
      rent_receipts       Generate monthly rent receipts for a given financial year.
      send_to_kindle      Send books to kindle via Dropbox/IFTTT.
      split_pdf           Split pdf horizontally/vertically.
