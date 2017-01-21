#!/bin/bash

# Download morgue files from CAO
# Originally used wget for this, but ran into an issue where it would crawl a
# bunch of differently sorted versions of the same directory:
#       http://unix.stackexchange.com/questions/73367/how-do-i-prevent-wget-from-loading-apache-directory-listings-in-different-orders
# TODO: Should probably have filtered down to files no older than X, since we 
# can't really parse morguefiles from ancient versions anyways
lftp -e 'mirror -I morgue*.txt' http://crawl.akrasiac.org/rawdata/
