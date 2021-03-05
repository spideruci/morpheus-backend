#!/bin/zsh

j11 && trinity https://github.com/serg-delft/jpacman-template --config .spider.yml --current  > ../results/logs/jpacman-framework.log 2>&1 
j11 && trinity https://github.com/apache/commons-io --config .spider.yml  --current > ../results/logs/commons-io.log 2>&1 
j8 && trinity https://github.com/apache/commons-cli --config .spider.yml  --current > ../results/logs/commons-cli.log 2>&1
j8 && trinity https://github.com/apache/commons-math --config .spider.yml  --current > ../results/logs/commons-cli.log 2>&1
j8 && trinity https://github.com/apache/maven --config .spider.yml  --current > ../results/logs/commons-cli.log 2>&1
j8 && trinity https://github.com/jhy/jsoup --config .spider.yml  --current > ../results/logs/jsoup.log 2>&1
