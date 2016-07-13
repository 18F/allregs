import re
from regparser.tree.xml_parser.reg_text import (get_markers,
                                                RegtextParagraphProcessor)
from regparser.tree.depth.derive import derive_depths

dummy_processor = RegtextParagraphProcessor()
additional_constraints = dummy_processor.additional_constraints()
relaxed_constraints = dummy_processor.relaxed_constraints()


def skip_page_counts(lines):
    for line in lines:
        if not re.search('\[\[[pP]age.*\]\]', line):
            yield line


def add_section_text(lines):
    for line in lines:
        if re.match('Sec\.\s+([0-9]+)\.([0-9]+)', line):
            line = line.replace('Sec.', 'Section')
        yield line


def find_sections(lines):
    part = None
    section = None
    for line in lines:
        section_start = re.match('Sec\.\s+([0-9]+)\.([0-9]+)', line)
        part_start = re.match("PART|\s+Subpart", line)

        if part_start:
            part = None
            section = None

        if section_start:
            part = section_start.groups()[0]
            section = section_start.groups()[1]

        if part and section:
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


def split_text_by_marker(marker, text):
    regex = "(\({}\))".format(marker)
    splits = re.split(regex, text, maxsplit=1)
    return splits[0], splits[1] + splits[2]


def get_subsections(section):
    paragraphs = [re.sub(r"\n(\S)", r"\1", p.strip())
                  for p in re.split("\n +", section[2])]
    subsections = []
    for p in paragraphs:
        markers = get_markers(p)
        if not markers:
            subsections.append(('MARKERLESS', p))
        else:
            tail = p
            for marker in markers:
                    head, tail = split_text_by_marker(marker, tail)
                    subsections.append((marker, tail))
    return subsections


def get_depths(subsections):
    markers = [s[0] for s in subsections]
    solution = derive_depths(markers, additional_constraints)

    # if not solution:
    #    solution = derive_depths(markers, relaxed_constraints)

    if solution:
        depths = [assignment.depth for assignment in solution[0]]
    else:
        depths = [0]*len(markers)

    result = []
    for depth, subsection in zip(depths, subsections):
            result.append((depth, subsection[0], subsection[1]))
    return result


def parse_structure(sections):
    for section in sections:
        subsections = get_subsections(section)
        result = get_depths(subsections)
        yield [section[0], section[1], result]


def render_sections(sections):
    section_html = open('section.tmpl.html').read()
    par_html = '<p class="depth{0}">{1}</p>'
    for section in sections:
        content = ''
        for i, subsection in enumerate(section[2]):
            if i == 0:
                content += '<h3>{0}</h3>'.format(subsection[2])
            else:
                formatted_paragraph = re.sub(r"^(\(\S+\))", r"<em>\1</em>",
                                             subsection[2])
                content += par_html.format(subsection[0], formatted_paragraph)
        rendered = section_html.replace('**CONTENT**', content)
        yield (section[0], section[1], rendered)


def write_section(year, title, section):
    filename = 'html/sections/{1}CFR{2}.{3}({0}).html'.format(
                                    year, title, section[0], section[1])
    f = open(filename, 'w')
    f.write(section[2])
    f.close()
    print('wrote: %s' % filename)

filename = 'data/text/CFR-2016-title11.txt'
match = re.search("CFR-([0-9]+)-title([0-9]+)", filename)
year = match.groups()[0]
title = match.groups()[1]

f = open(filename)


for result in render_sections(parse_structure(yield_sections(
                              find_sections(skip_page_counts(f))))):
    write_section(year, title, result)

f.close()
