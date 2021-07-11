# *jsonify html*

Jsonify HTML is a general-proposed, template-based parser to transform HTML to reusable JSON data. It can be thought as a *reverse engine* of template-based renders, e.g. Jinja.

---
🎉🎉 **Coming Soon: Jsonify HTML v2** 🎉🎉
include statement, pipe, sandbox, reference, simple script and all fruitful features, all make Jsonify HTML a full-fledged parser!

A preview of new syntax (in YAML format):
```yaml
# version: "2.0"                     # buildin settings

$i: 0                                # define variables

$post:
  Object:                            # anonymous object
    init():                          # init() function executes before parsing
      - clean()
    String title:                    # type annotation
      parse():                       # parse() function converts HTML to a JSON entry
        - select_one(.title)         # commands are functions ...
        - inner_text(strip=True)     # ... and can be called like those in Python
    Datetime date:
      - select_one(.date)            # parse() can be omitted for simple entries
      - inner_text(strip=True)
    String author:
      - select_one(.author)
      - inner_text(strip=True)
    Uri url:
      - select_one(.//a/@href)       # xpath is fully supported
    Integer id:
      - eval($i)                     # reference to a variable
    increment_id():                  # define a method called increment_id
      - exec($i += 1)
    final():                         # final() function executes after parsing
      - increment_id()               # methods are commands, too

List[Object]:                        # nested type annotation
  parse():
    - select_one(article)
    - inner_html()
    - clean()
    - select(.post)
    - foreach(e -> apply(e, $post))  # lambda without side-effects
```

---

All we need is a HTML document,

```html
<div class="text">Hello World</div>
```

and a template to parse it,

```json
{
    "$type": "str",
    "$cmd": [ ["select_one", ".text"], ["inner_text"] ]
}
```

`$type` specifies the data type of final objects, `$cmd` contains a list of instructions to tell the parser to `select_one`  DOM named `.text` and extract its `inner_text`. So we have,

```python
"Hello World"
```

## Requirements

Python 3.7+

## Installation

```shell
pip install --upgrade jsonify_html
```

## Examples

Our goal is to extract useful information in a HTML document. It's extremely useful when we **DON'T** have the original data, for example, the webpage you scraped from a website. Here is a page from James Potter's blog:

```html
<html>
<head>
    <title> an awesome blog </title>
</head>
<body>
    <!-- other DOMs -->
    <div class="post-list">
        <div class="post">
            <p class="title">How to convert HTML to JSON ?</p>
            <p class="meta">
                <span class="author">James Potter</span>
                <span class="date">2020-10-02</span>
                <span class="comments">20</span>
            </p>
            <p class="preview">Using <em>JSONify HTML</em> ! ...</p>
            <div class="image-container">
                <img src="post20201001_head.png">
            </div>
        </div>
        <div class="post">
            <p class="title">Hello World</p>
            <p class="meta">
                <span class="author">James Potter</span>
                <span class="date">2020-10-01</span>
                <span class="comments">5</span>
            </p>
            <p class="preview">I opened a blog! ...</p>
            <div class="image-container">
                <img src="post20201001_head.png">
            </div>
        </div>
    </div>
    <!-- other DOMs -->
</body>
</html>
```

We want well-structured data, presented as an object  in Python, or `JSON` for elsewhere. Let's try to write a **template**:

```json
// main.json
{
    "$type": "list",
    "$cmd": [
        ["select_one", ".post-list"],
        ["recursive"]
    ]
}
```

where `$type` tells the parser, our final object is a `list`, `$cmd`  is a list of command lines, each command line begins with the name of a command, then follows its arguments. There are two commands,

* `select_one` extracts `div.post-list` from our webpage, you may use either CSS or XPATH selectors.  

* `recursive` tells the parser to *automatically* identify and process every DOM inside `div.post-list` (which is extracted by the preceding command. ).

It works like magic! Right? All we need to do next, is to write some **sub-templates** to instruct the parser.

```json
// post.json
{
    "$type": "object",
    "$match": ".post",
    "name": "post",
    "title": {
        "$type": "str",
        "$cmd": [ ["select_one", ".title"], ["inner_text"] ]
    },
    "author": {
        "$type": "str",
        "$cmd": [ ["select_one", ".author"], ["inner_text"] ]
    },
    "date": {
        "$type": "datetime",
        "$cmd": [ ["select_one", ".date"], ["inner_text"] ]
    },
    "comments": {
        "$type": "int",
        "$cmd": [ ["select_one", ".comments"], ["inner_text"] ]
    },
    "preview": {
        "$type": "html",
        "$cmd": [ ["select_one", ".preview"], ["inner_html"] ]
    },
    "image": {
        "$type": "str",
        "$cmd": [ ["select_one", ".//img/@src"] ]
    }
}
```

Notice: each key starts with `$` indicates a keyword, it tells the parser essential instructions, otherwise, it would be the data key presented in final objects. A template can also include some sub-templates *in place*, for instance, `title` is a data key, and its value is a sub-template. Let's simply run a demo to see what we will get,

```
[folder structure]
+ root
|--- webpage.html
|--- main.json
|--- post.json
```

Here's the code:

```python
from jsonify_html import from_package
import json

html = open('webpage.html').read()
data = from_package('main.json', html)
print(json.dumps(data, indent=2))  # prettify JSON
```

It does work like magic! We finally got,

```json
// finial results
[
  {
    "name": "post",
    "title": "How to convert HTML to JSON ?",
    "author": "James Potter",
    "date": "2020-10-02T00:00:00",
    "comments": 20,
    "preview": "<p>Using <em>JSONify HTML</em> ! ...</p>",
    "image": "post20201001_head.png"
  },
  {
    "name": "post",
    "title": "Hello World",
    "author": "James Potter",
    "date": "2020-10-01T00:00:00",
    "comments": 5,
    "preview": "<p>I opened a blog! ...</p>",
    "image": "post20201001_head.png"
  }
]
```

What if we want to abbreviate those templates as a single one? It's straight forward with the `foreach` command:

```json
// template.json
{
    "$type": "list",
    "$cmd": [
        ["select", ".post"],
        ["foreach",
            {
                "template": {
                    "$type": "object",
                    "$match": ".post",
                    "name": "post",
                    "title": {
                        "$type": "str",
                        "$cmd": [ ["select_one", ".title"], ["inner_text"] ]
                    },
                    "author": {
                        "$type": "str",
                        "$cmd": [ ["select_one", ".author"], ["inner_text"] ]
                    },
                    "date": {
                        "$type": "datetime",
                        "$cmd": [ ["select_one", ".date"], ["inner_text"] ]
                    },
                    "comments": {
                        "$type": "int",
                        "$cmd": [ ["select_one", ".comments"], ["inner_text"] ]
                    },
                    "preview": {
                        "$type": "html",
                        "$cmd": [ ["select_one", ".preview"], ["inner_html"] ]
                    },
                    "image": {
                        "$type": "str",
                        "$cmd": [ ["select_one", ".//img/@src"] ]
                    }
                }
            }
        ]
    ]
}
```

 Note here we `select` all `.post`, instead of just one `.post-list`.

```python
from jsonify_html import from_template
import json

html = open('webpage.html').read()
template = json.load(open('template.json'))
data = from_template(template, html)
print(json.dumps(data, indent=2))  # prettify JSON
```

It again works!
