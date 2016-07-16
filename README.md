# AllRegs

A pretty, search engine optimized, easily shareable version of the text of
the most recent annual editions of the Code of Federal Regulations (CFR).

Inspired by, and depending on, eRegs.

To Run Everything:

```bash
% bash build.sh
```

Which will run:
```bash
$ mkdir -p data/text
$ mkdir -p html/sections
$ mkdir -p html/titles
$ mkdir -p html/parts
$ python get_cfr_text.py
$ python parse_structure.py --debug
```
