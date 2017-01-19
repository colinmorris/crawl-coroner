#!/bin/bash

# TODO: Should probably have filtered down to files no older than X, since we can't really parse morguefiles from ancient versions anyways
lftp -e 'mirror -I morgue*.txt' http://crawl.akrasiac.org/rawdata/
