Secret Santa
============

Synopsis
--------

This tool is designed for use within a small friend group; the tool will read in participant data from a configuration file and match participants, taking account for blacklisted matches. There is built in functionality to send participants their matches via email, but you will need your own account and SMTP server to make this happen.

There is also a verbose mode to enable debugging and printing of status information throughout the script; this can be helpful as you may end up generating participant blacklists that render resolution of valid matched impossible (see section on troubleshooting below).

Usage
-----

The santa is called via the command line and does not require any arguments. You can specify a configuration file and set the send and verbose flags:

~~~
cd Secret-Santa
cp example.santa.yaml santa.yaml
#Now edit the configuration file to your liking 
santa.py -i <path_to_config> --send --verbose
~~~

Configuration File
-----------------

The default configuration file is 'santa.yaml', located in the script working directory; you can specify an alternative file on the command line. You will need to provide all data, including emails, even if no email is to be sent; if you don't have these, just use the dummy emails in the file. You'll need to make your own copy of this file as described in the Usgae section.

Troubleshooting
---------------

You can set the verbose flag in the script to monitor matching and progress. This may be required where your blacklist is prohibitive; it would be possible, in a simple case to specify a prohibitive list, for example:

~~~python
participant_data:
        Alice : alice@domain.local
        Bob : bob@domain.local
        Charlie : charlie@domain.local

blacklist:
        - - Alice
          - Bob
        - - Alice
          - Charlie
~~~

It can be seen from a short inspection that no matching is permitted for Alice in this case, but this is not always obvious. Setting the verbose command line option will help you determine the root of your problem.

Dependencies
------------
    *pyyaml
    *smtplib
