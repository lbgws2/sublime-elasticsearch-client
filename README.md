# Elasticsearch Client for Sublime Text 3
... for only OS X

## Overview

## Installation
To install, clone to your "Packages" directory.

- OS X: ~/Library/Application\\ Support/Sublime\\ Text\\ 3/Packages

```bash
git clone https://github.com/kunihikokido/sublime-elasticsearch-client.git Elasticsearch
```


## Using
you can send a body

```json
{
    "query": {
        "match_all": {}
    }
}
```

Once you have a request ready, use shortcut ``Command + B`` or open the Command Palette (``Shift + Command + P``) and enter ``Elasticsearch Search Request``.

## Settings

User Settings (accessible from the *Preferences/Package Settings/Elasticsearch Client/Settings - User* menu)

Example:
```json
{
    "active_server": "localhost",
    "servers": {
        "localhost": {
            "base_url": "http://localhost:9200/",
            "index": "test",
            "doc_type": "test",
            "analyzer": "default",
            "enabled_create_index": true,
            "enabled_delete_mapping": true,
            "enabled_delete_document": true,
            "enabled_delete_index": true,
            "enabled_index_document": false,
            "enabled_put_mapping": true,
            "enabled_register_query": true,
            "enabled_delete_percolator": true,
        },
        "api.siba.tokyo": {
            "base_url": "https://api.siba.tokyo/public/",
            "index": "index-zgkksx-my-index",
            "doc_type": "webpages"
        }
    }
}
```

Setting                    | Description
-------------------------- | ----------------------------------
``active_server``          | Elasticsearch Active Server. You can change the ``Switch Server`` Command
``servers``                | Elasticsearch Server settings.

**servers.\<key\>**

Setting                    | Description
-------------------------- | ----------------------------------
``base_url``               | Elasticsearch API Endpoint URL. default: ``http://localhost:9200``
``index``                  | Elasticsearch Index name. default: ``test``
``doc_type``               | Elasticsearch Type name. default: ``test``
``analyzer``               | analyzer for Analyze Command. default: ``default``
``enabled_create_index``   | if set ``true`` you can create index. default: ``false``
``enabled_delete_mapping`` | if set ``true`` you can delete mapping. default: ``false``
``enabled_delete_document``| if set ``true`` you can delete document. default: ``false``
``enabled_delete_index``   | if set ``true`` you can delete index. default: ``false``
``enabled_index_document`` | if set ``true`` you can index document. default: ``false``
``enabled_put_mapping``    | if set ``true`` you can put mapping. default: ``false``
``enabled_register_query``    | if set ``true`` you can register query for percolator. default: ``false``
``enabled_delete_percolator``    | if set ``true`` you can delete registerd query for percolator. default: ``false``


## Commands
open the Command Palette (``Shift + Command + P``) and enter ``Elasticsearch ...``.

Command                            | Method    | Call API
---------------------------------- | --------- | -------------------------
Elasticsearch: Analyze             | POST      | ``/index/_analyze``
Elasticsearch: Cluster Health      | GET       | ``/_cat/health``
Elasticsearch: Create Index        | PUT       | ``/index``
Elasticsearch: Delete Document     | DELETE    | ``/index/type/id``
Elasticsearch: Delete Index        | DELETE    | ``/index/``
Elasticsearch: Delete Mapping      | PUT       | ``/index/_mapping/type``
Elasticsearch: Get Document        | GET       | ``/index/type/id``
Elasticsearch: Get Index Settings  | GET       | ``/index/_settings``
Elasticsearch: Get Mapping         | GET       | ``/index/_mapping/type``
Elasticsearch: Index Document      | PUT/POST  | ``/index/type/id``
Elasticsearch: List All Indexes    | GET       | ``/_cat/indices``
Elasticsearch: Put Mapping         | PUT       | ``/index/_mapping/type``
Elasticsearch: Search Request      | POST      | ``/index/type/_search``
Elasticsearch: Register Query for Percolator | PUT       | ``/index/.percolator/id``
Elasticsearch: Show Query for Percolator     | POST      | ``/index/.percolator/_search``
Elasticsearch: Match Query for Percolator    | POST      | ``/index/type/_percolate``
Elasticsearch: Delete Query for Percolator   | DELETE    | ``/index/.percolator/id``
Elasticsearch: Show Active Server  | -         |  ※ appears in the status bar.
Elasticsearch: Switch Servers      | -         |  ※ change the active server.
Elasticsearch: Change Index        | -         |  ※ change the index for active server.
Elasticsearch: Change Doc Type     | -         |  ※ change the doc type for active server.


## Snippets for Queries
file types ``*.es`` or set syntax ``Elasticsearch``

Abbreviation                    | tag
------------------------------- | ----------------------------------
bool                            | ``"bool": {...}``
boosting                        | ``"boosting": {...}``
commonterms                     | ``"common": {...}``
constantscore                   | ``"constant_score": {...}``
dismax                          | ``"dis_max": {...}``
filtered                        | ``"filtered": {...}``
functionscore                   | ``"function_score": {...}``
fuzzy                           | ``"fuzzy": {...}``
fuzzylike                       | ``"fuzzy_like_this": {...}``
fuzzylike                       | ``"fuzzy_like_this_field": {...}``
geoshape                        | ``"geo_shape": {...}``
haschild                        | ``"has_child": {...}``
ids                             | ``"ids": {...}``
indices                         | ``"indices": {...}``
matchall                        | ``"match_all": {..}``
match                           | ``"match": {...}``
morelike                        | ``"more_like_this": {...}``
multimatch                      | ``"multi_match": {...}``
nested                          | ``"nested": {...}``
prefix                          | ``"prefix": {...}``
querystring                     | ``"query_string": {...}``
range                           | ``"range": {...}``
regexp                          | ``"regexp": {...}``
simplequery                     | ``"simple_query_string": {...}``
spanfirst                       | ``"span_first": {...}``
spannear                        | ``"span_near": {...}``
spanmulti                       | ``"span_multi": {...}``
spannot                         | ``"span_not": {..}``
spanor                          | ``"span_or": {...}``
template                        | ``"template": {...}``
term                            | ``"term": {...}``
terms                           | ``"terms": {...}``
topchildren                     | ``"top_children": {...}``
wildcard                        | ``"wildcard": {...}``

## Snippets for Filters
file types ``*.es`` or set syntax ``Elasticsearch``

Abbreviation                    | tag
------------------------------- | ----------------------------------
and                             | ``"and": [...]``
bool                            | ``"bool": {...}``
exists                          | ``"exists": {...}``
geobounding                     | ``"geo_bounding_box": {...}``
geodistance                     | ``"geo_distance": {...}``
geopolygon                      | ``"geo_polygon": {...}``
geoshape                        | ``"geo_shape": {...}``
geohash                         | ``"geohash_cell": {...}``
haschild                        | ``"has_child": {...}``
hascparent                      | ``"has_parent": {...}``
ids                             | ``"ids": {...}``
indices                         | ``"indices": {...}``
limit                           | ``"limit": {...}``
matchall                        | ``"match_all": {..}``
missing                         | ``"missing": {...}``
nested                          | ``"nested": {...}``
not                             | ``"not": [...]``
or                              | ``"or": [...]``
prefix                          | ``"prefix": {...}``
range                           | ``"range": {...}``
regexp                          | ``"regexp": {...}``
script                          | ``"script": {...}``
term                            | ``"term": {...}``
terms                           | ``"terms": {...}``
type                            | ``"type": {...}``

## Snippets for Aggregations
file types ``*.es`` or set syntax ``Elasticsearch``

Abbreviation                    | tag
------------------------------- | ----------------------------------
aggsavg                         | ``"aggs": {..."avg": {...}``
aggscardinality                 | ``"aggs": {..."cardinality": {...}``
aggschildren                    | ``"aggs": {..."children": {...}``
aggsdatehistogram               | ``"aggs": {..."date_histogram": {...}``
aggsdaterange                   | ``"aggs": {..."date_range": {...}``
aggsextendedstats               | ``"aggs": {..."extended_stats": {...}``
aggsfilter                      | ``"aggs": {..."filter": {...}``
aggsfilters                     | ``"aggs": {..."filters": {...}``
aggsgeobounds                   | ``"aggs": {..."geo_bounds": {...}``
aggsgeodistance                 | ``"aggs": {..."geo_distance": {...}``
aggsgeohash                     | ``"aggs": {..."geohash_grid": {...}``
aggsglobal                      | ``"aggs": {..."global": {...}``
aggshistogram                   | ``"aggs": {..."histogram": {...}``
aggsipv4range                   | ``"aggs": {..."ip_range": {...}``
aggsmax                         | ``"aggs": {..."max": {...}``
aggsmin                         | ``"aggs": {..."min": {...}``
aggsmissing                     | ``"aggs": {..."missing": {...}``
aggsnested                      | ``"aggs": {..."nested": {...}``
aggspercentileranks             | ``"aggs": {..."percentile_ranks": {...}``
aggspercentiles                 | ``"aggs": {..."percentiles": {...}``
aggsrange                       | ``"aggs": {..."range": {...}``
aggsreversenested               | ``"aggs": {..."reverse_nested": {...}``
aggsscriptedmetric              | ``"aggs": {..."scripted_metric": {...}``
saggssignificantterm            | ``"aggs": {..."significant_terms": {...}``
saggsstat                       | ``"aggs": {..."stats": {...}``
aggssum                         | ``"aggs": {..."sum": {...}``
aggsterms                       | ``"aggs": {..."terms": {...}``
aggstophits                     | ``"aggs": {..."top_hits": {...}``
aggsvaluecount                  | ``"aggs": {..."value_count": {...}``


## Completions
file types ``*.es`` or set syntax ``Elasticsearch``

- _all
- _score
- asc
- desc
- false
- true

and etc..



