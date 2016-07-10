import re
from os import makedirs
from regparser.tree.paragraph import ParagraphParser


def skip_page_counts(lines):
    for line in lines:
        if not re.search('\[\[[pP]age.*\]\]', line):
            yield line


def find_sections(lines):
    part = None
    section = None
    for line in lines:
        section_start = re.match('Sec\.\s+([0-9]+)\.([0-9]+)', line)
        if section_start:
            part = section_start.groups()[0]
            section = section_start.groups()[1]
            part_start = re.match('PART', line)

        if part and section and not part_start:
            yield (part, section, line)


def yield_sections(lines):
    last_section = None
    last_part = None
    text = ''
    for part, section, line in lines:
        if last_section and section is not last_section \
         or part is not last_part:
            yield (last_part, last_section, text)
            text = ''
        text += line
        last_section = section
        last_part = part

title = 2
f = open('data/text/CFR-2016-title%d.txt' % title)

for section in yield_sections(find_sections(skip_page_counts(f))):
    print(section)
    print('*'*100)

f.close()
