# Wikipedia dump to JSON converter
[![Build Status](https://travis-ci.org/cemsbr/wikipedia2json.svg?branch=master)](https://travis-ci.org/cemsbr/wikipedia2json)
[![Coverage Status](https://coveralls.io/repos/cemsbr/wikipedia2json/badge.svg?branch=master)](https://coveralls.io/r/cemsbr/wikipedia2json?branch=master)

I wrote this project to convert `enwiki-20150304-pages-articles.xml.bz2` to a JSON file that can be properly loaded by Spark's `jsonFile` method. Other dates and other languages may also work (`*-*-pages-articles.xml.bz2`).

## Scripts

### w2j.py
Converts pages in the XML file (`<page>.*</page>`) to JSON format, one page per line.

To validate the output, use `check_json.py` and to limit the output size into one or many files, use `split.py` (see *Tips* section).

* **Input**: wikipedia XML dump by stdin or filename
* **Output**: one-line JSON per page element

```bash
# Converts the whole XML to JSON
bzcat enwiki-*.xml.bz2 | w2j.py >enwiki.json
# Compressed output
bzcat enwiki-*.xml.bz2 | w2j.py | \
bzip2 >enwiki.json.bz2
```

### check_json.py
Filters valid one-line JSONs.

* **Input**: one-line JSONs by stdin or filename
* **Output**
 * **Stdout**: valid JSONs
 * **Stderr**: invalid JSONs and, in the end, the total amount of processed lines

```bash
# Filename
check_json.py enwiki.json 2>not_valid.json >/dev/null
# stdin
bzcat enwiki.json.bz2 | \
check_json.py 2>not_valid.json >/dev/null
```

### split.py
Splits the input in many custom-sized files, in a *line-by-line* way. If adding the next line exceeds the specified size, it won't be appended.

* **Input**: multiline text by stdin
* **Output**: write specified files

```bash
# 100M.json file will have the first 100 MB.
# 924M.json will have the remaining 924 MB to complete 1GB.
cat enwiki.json | \
split.py 100M 100M.json 1G 924M.json
```

## Tips

### Limit conversion by size
You can use the `split.py` script to limit the conversion:
```bash
# Convert up to 10MB of JSON file
bzcat enwiki-*.xml.bz2 | w2j.py | \
split.py 10M enwiki_small.json
```

### Validation while converting
You can use `check_json.py` together with `w2j.py` to convert and check for errors at the same time:
```bash
bzcat enwiki-*.xml.bz2 | w2j.py | \
check_json.py 2>not_valid.json >enwiki_valid.json
```

### Different sizes of the same data - Saving storage
If you want to run an application with different sizes of the same data (e.g. scalability experiment), you can save storage space by splitting and then `cat`ing all files up to the desired size.

For example, suppose we want to use the first 4 and 16 GB of enwiki and put them in Hadoop Distributed File System (HDFS):
```bash
# enwiki04G.json will have the first 4GB of data
# enwiki16G.json will have the next 12GB
cat enwiki.json | split.py 4G enwiki04G.json 16G enwiki16G.json
# Upload 4G to HDFS
hadoop fs -copyFromLocal enwiki04G.json /enwiki/04.json
# Upload 16G to HDFS
cat *.json | hadoop fs -put - hdfs://master/enwiki/16.json
```

To save much more space, you can use gzip or bzip2. As `split.py` does not compress data, we will use linux named pipes:
```bash
# Create named pipes
mkfifo enwiki04G.json enwiki16G.json
# Compress data from named pipes in background
cat enwiki04G.json | bzip2 >enwiki04G.json.bz2 &
cat enwiki16G.json | bzip2 >enwiki16G.json.bz2 &
# Unaltered split.py command
cat enwiki.json | split.py 4G enwiki04G.json 16G enwiki16G.json
# Delete the named pipes (they are just files)
rm enwiki04G.json enwiki16G.json
# Upload to HDFS using bzcat
bzcat enwiki04G.json.bz2 | hadoop fs -put - hdfs://master/enwiki/04.json
bzcat *.json.bz2 | hadoop fs -put - hdfs://master/enwiki/16.json
```

This way, you will need only 4.3G to generate files with 20G in total. You may want to use pbzip2 for parallel (de)compressing.

### Pipe party :)
To convert the enwiki XML to JSON, verify the output, split line by line and compress the output at once:

```bash
# Create named pipes
mkfifo enwiki04G.json enwiki16G.json
# Compress data from named pipes in background
cat enwiki04G.json | pbzip2 >enwiki04G.json.bz2 &
cat enwiki16G.json | pbzip2 >enwiki16G.json.bz2 &
# All but output compression
bzcat enwiki-*.xml.bz2 | w2j.py | \
check_json.py 2>not_valid.json | \
split.py 4G enwiki04G.json 16G enwiki16G.json
# Delete the named pipes (they are just files)
rm enwiki04G.json enwiki16G.json
```

## External resources
* [enwiki-20150304-pages-articles.xml.bz2](https://dumps.wikimedia.org/enwiki/20150304/enwiki-20150304-pages-articles.xml.bz2)
* [Wikimedia database backup dumps](https://dumps.wikimedia.org/backup-index.html)
* [Spark JSON datasets](http://spark.apache.org/docs/latest/sql-programming-guide.html#json-datasets)
