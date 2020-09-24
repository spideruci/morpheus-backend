#!/bin/zsh
. ~/.zshrc

pluperfect https://github.com/apache/commons-io --config .spider.yml > ../results/logs/commons-io.log 2>&1 
# pluperfect https://github.com/apache/commons-cli --config .spider.yml > ../results/logs/commons-cli.log 2>&1
# pluperfect https://github.com/jhy/jsoup --config .spider.yml > ../results/logs/jsoup.log 2>&1
# pluperfect https://github.com/alibaba/fastjson --config .spider.yml > ../results/logs/fastjson.log 2>&1
