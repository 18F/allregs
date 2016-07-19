# AllRegs

Reformatting the Code of Federal Regulations to use the US Web Design Standards.
Inspired by, and depending on, [eRegs](https://github.com/eregs/regulations-parser).

To install, run:
```bash
$ pip install -r requirements.txt
```

You may need to do some work to get lxml running on your system.
It's usually a huge hassle, but I would recommend [this](http://stackoverflow.com/questions/5178416/pip-install-lxml-error)
StackOverflow page as a starting point.

To get set up and build the first 100 sections of each part, run:

```bash
% bash build.sh
```

Which will run:
```bash
mkdir -p data/text
mkdir -p html/sections
mkdir -p html/titles
mkdir -p html/parts
npm install
cp node_modules/uswds/dist/css/uswds.min.css css
cp node_modules/uswds/dist/fonts/* fonts
python get_cfr_text.py
python parse_structure.py --debug
```

To run on all the regs, it is much faster to use the parallel_run.sh script:
```bash
$ bash parallel_run.sh
```
This will kick off a separate background process for each title. It takes
~90 minutes to run on a 16 core server (!).

### Panama Canal
Note that title 35 no longer exists. It is not a data error. The title regulated
the panama canal which the US no longer controls.

### Other errors
You may see other errors in the regs, for example missing part descriptions.
That is what "alpha" means in the title- this work is a tech demonstration and
not intended for serious legal reference or research.

### Public domain

This project is in the worldwide [public domain](LICENSE.md). As stated in [CONTRIBUTING](CONTRIBUTING.md):

> This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).
>
> All contributions to this project will be released under the CC0 dedication. By submitting a pull request, you are agreeing to comply with this waiver of copyright interest.
