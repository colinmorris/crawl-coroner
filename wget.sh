#!/bin/bash

# recursive, no parents, no directories (flat), robots off, no host prefixing, only morgue files, 
wget -r -np -nd -e robots=off -nH -A 'morgue-*.txt' -R '=*' -P 'morguefiles' http://crawl.akrasiac.org/rawdata/scone/
