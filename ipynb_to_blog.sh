#!/bin/bash

if [[ $# -lt 3 ]]
then
    echo "usage: $0 ipynb_file slug title mathjax?"
    exit 1
fi

if [[ $# -eq 4 ]]
then
mathjax=$(cat << EOF
<script type="text/x-mathjax-config">
MathJax.Hub.Config({
  tex2jax: {inlineMath: [['$','$'], ['\\\(','\\\)']]}
  });
  </script>
  <script type="text/javascript" async src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_CHTML">
  </script>
EOF
)
fi

dest=~/src/colinmorris.github.com
stem="${1%.*}"
slug=$2
jupyter nbconvert --Application.output_files_dir=${slug} --config nbconvert_html_config.py $1

sed -i "s/src=\"${slug}/src=\"\/assets\/${slug}/" ${stem}.html
cat - ${stem}.html << EOF | sponge ${stem}.html
---
layout: notebook-post
title: "$3"
---
$mathjax
EOF

mv ${stem}.html ${dest}/_posts/`date -I`-${slug}.html
assetdir=${dest}/assets/${slug}
if [ -d $assetdir ]
then
    rm -I -r $assetdir
fi
mv ${slug} ${dest}/assets/
