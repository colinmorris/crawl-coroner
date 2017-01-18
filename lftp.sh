#!/bin/bash

lftp -e 'mirror -I morgue*.txt' http://crawl.akrasiac.org/rawdata/
