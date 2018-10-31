.. :changelog:

History
=======

0.6.0 (2018-10-01)
------------------
* Removed dependency on bitarray (no binary wheels)
* Added details on installation for non-python users
* 2 years almost since last update!

0.5.0 (2016-10-03)
------------------
* Fixed version display in release version.
* Removed support for mongo extract

0.4.8 (2016-10-02)
------------------
* added support for latin1 encoding of csv extract
* fixes to setup process so that mideu.yml file is installed
* fixed de43 split to allow more formats for different countries

0.4.6 (2016-08-09)
------------------
* added ``--no1014blocking`` option to allow processing of VBS structure files.

0.4.5 (2016-08-06)
------------------
* check that all of message consumed by fields otherwise raise exception
* get rid of a heap of debugging prints that were clogging the output
* allow freestyle de43 fields with the de43 processor enabled. Use regex rather than string splits

0.4.4-0.4.3 (2016-08-03)
------------------------
* Fix issue with mideu when no parameters passed (stack trace)
* Some more debugging messages provided with -d switch
* signed the release with key for 0.4.4. need to publish my pub key somewhere..

0.4.2 (2016-03-13)
------------------
* Complete data elements added to default config.
* Added versioneer support for easier package versions

0.4.1 (2015-12-16)
------------------
* Additional data elements added to default config file.

0.4.0 (2015-10-05)
------------------
* Now supporting python 2.6 (for all those still using RHEL 6)
* Headers rows in mideu csv extracts don't work in 2.6

0.3.0 (2015-10-03)
------------------
* added sub commands for mideu
* mideu now supports IPM encoding conversion between ascii and ebcdic
* Now faster using list comps instead of slow loops

0.2.0 (2015-08-28)
------------------
* Support for config override for mideu - see usage doco
* Progress bar while using mideu.. it takes a while
* Now supports python 3.4, 3.5 and 2.7. Upgrade if you are using 2.6
* New usage documentation

0.1.0 (2015-08-20)
------------------
* First release.
