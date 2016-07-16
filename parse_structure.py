import re
from regparser.tree.xml_parser.reg_text import (get_markers,
                                                RegtextParagraphProcessor,
                                                initial_markers)
from regparser.tree.depth.derive import derive_depths
from regparser.tree.depth import markers as mtypes
import sys
import os


class Parser:
    def __init__(self):
        dummy_processor = RegtextParagraphProcessor()
        self.additional_constraints = dummy_processor.additional_constraints()

        self.typos = {"50": {"Sec. 263.53  Other funds.": "Sec. 253.53  Other funds."},
                      "12": {"Part 1221_MARGIN AND CAPITAL REQUIREMENTS FOR COVERED SWAP ENTITIES":
                             "PART 1221_MARGIN AND CAPITAL REQUIREMENTS FOR COVERED SWAP ENTITIES"},
                      "32": {"Sec. 856.7  Action after final decision.":
                             "Sec. 865.7  Action after final decision."},
                      "36": {"Sec. 36.19  Special actions.":
                             "Sec. 242.19  Special actions."}}


    def start_at_part(self, sections, part_start):
        started = False
        for section in sections:
            if int(section[0]) >= int(part_start):
                started = True
            if started:
                yield section

    def end_at_part(self, sections, end_part):
        for section in sections:
            if int(section[0]) > int(end_part):
                break
            yield section

    def debug(self, sections):
        for i, section in enumerate(sections):
            if i > 50:
                print('stopped (debug mode on)')
                break
            yield section

    def clean_text(self, lines):
        for line in lines:
            if not re.search('\[\[[pP]age.*\]\]', line):
                if self.title[0] in self.typos\
                 and line.strip() in self.typos[self.title[0]]:
                    print "typo found"
                    print line
                    print 'changed to:'
                    print self.typos[self.title[0]][line.strip()]
                    yield self.typos[self.title[0]][line.strip()] + '\n'
                else:
                    yield line

    def find_sections(self, lines):
        part = None
        section = None
        last_line = ''

        for line in lines:
            section_start = re.match('Sec\.\s+([0-9]+)\.([0-9]+)  [A-Z]', line)

            part_match_line = re.match("\s*PART [0-9]+[_\s]+" +
                                       "(:?Mc)?(:?8\(a\))?" +
                                       "(?:C\[Ocirc\]TE)?" +
                                       "(?:DoD)?" +
                                       "[^a-z]{5}" +
                                       "(:?\[RESERVED\])?", line)
            part_match = False
            if part_match_line:
                full_part_str = line
                for i in range(10):
                    full_part_str = full_part_str.replace('\n', ' ')
                    part_match = re.match("\s*PART ([0-9]+)[_\s]+" +
                                          "((:?Mc)?(:?8\(a\))?" +
                                          "(?:C\[Ocirc\]TE)?" +
                                          "(?:DoD)?" +
                                          "(?:[^a-z]{5})?.*)(:?(:?\[RESERVED\])|" +
                                          "(:?\-\-)|(:?Subpart)|" +
                                          "(:?Authority)|(:?Sec\.))",
                                          full_part_str, re.S)
                    if part_match:
                        break
                    full_part_str += lines.next()
                if part_match:
                    description = re.sub("\s+", " ", part_match.group(2))\
                                    .title().strip()
                    self.parts.append((part_match.group(1),
                                      description))
                else:
                    print full_part_str


            chapter_start = re.match("\s+CHAPTER", line)
            subchapter_start = re.match("\s+Subpart [A-Z]_", line)
            end_section = part_match or chapter_start or subchapter_start
            if end_section:
                part = None
                section = None

            if section_start and last_line.isspace():
                part = section_start.groups()[0]
                section = section_start.groups()[1]

            last_line = line
            if part and section:
                yield (part, section, line)

    def yield_sections(self, lines):
        last_section = None
        last_part = None
        text = ''
        for part, section, line in lines:
            if last_section and last_part and (section is not last_section or
                                               part is not last_part):
                section_header = line + lines.next()[2]
                section_header = section_header.replace('\n', ' ')
                match = re.match('Sec.\s+{0}.{1}+\s+([^\.]+)'
                                 .format(part, section),
                                 section_header)

                section_description = re.sub("\s+", " ",
                                             match.group(1).strip())

                if last_part not in self.sections:
                    self.sections[last_part] = [(last_part,
                                                 last_section,
                                                 section_description)]
                else:
                    self.sections[last_part].append((last_part,
                                                     last_section,
                                                     section_description))

                yield (last_part, last_section, text)
                text = ''
            text += line
            last_section = section
            last_part = part

    def split_text_by_marker(self, marker, text):
        regex = "(\(\s?{}\s?\))".format(marker)
        splits = re.split(regex, text, maxsplit=1)

        if len(splits) < 3:
            print(text)

        return splits[0], splits[1] + splits[2]

    def get_subsections_for_paragraph(self, paragraph, next_paragraph):
        subsections = []
        if next_paragraph:
            next_markers = initial_markers(next_paragraph)
            if len(next_markers) > 0:
                next_marker = next_markers[0]
            else:
                next_marker = None
        else:
            next_marker = None
        markers = get_markers(paragraph, next_marker)
        if not markers:
            subsections.append(('MARKERLESS', paragraph))
        else:
            tail = paragraph
            for marker in markers:
                    head, tail = self.split_text_by_marker(marker, tail)
                    subsections.append((marker, tail))
        return subsections

    def get_subsections(self, section):
        paragraphs = [re.sub(r"\n(\S)", r"\1", p.strip())
                      for p in re.split("\n +", section[2])]
        subsections = []
        last_paragraph = None
        for p in paragraphs:
            if(last_paragraph):
                subsections.extend(
                        self.get_subsections_for_paragraph(last_paragraph, p))
            last_paragraph = p
        subsections.extend(self.get_subsections_for_paragraph(p, None))
        return subsections

    def markers_are_valid(self, markers):
        all_markers = set(markers)
        all_types = []
        for mtype in mtypes.types:
            all_types += list(mtype)

        all_types = set(all_types)

        return not all_markers.difference(all_types) and len(markers) < 150

    def get_depths(self, subsections):
        markers = [s[0] for s in subsections]

        if self.markers_are_valid(markers):
            solution = derive_depths(markers, self.additional_constraints)
        else:
            solution = None

        if solution:
            depths = [assignment.depth for assignment in solution[0]]
        else:
            depths = [0]*len(markers)
            print("..PARSE FAILED")
            # print(markers)
            # print(subsections)
            self.section_failures += 1

        result = []
        for depth, subsection in zip(depths, subsections):
                result.append((depth, subsection[0], subsection[1]))
        return result

    def parse_structure(self, sections):
        for section in sections:
            subsections = self.get_subsections(section)
            print("Parsing {0}CFR {1}.{2}..."
                  .format(self.title[0], section[0], section[1]))
            result = self.get_depths(subsections)
            self.sections_processed += 1
            yield [section[0], section[1], result]

    def render_sections(self, sections):
        section_html = open('master.tmpl.html').read()
        par_html = '<p class="depth{0}">{1}</p>'

        title_subheader = """<h3>
                                <a href="/">CFR</a><span>&nbsp/&nbsp</span>
                                <a href="html/titles/title{0}.html">
                                    Title {0}
                                </a><span>&nbsp/&nbsp</span>
                                <a href="html/parts/{0}CFR{1}.html">Part {1}
                                </a><span>&nbsp/&nbsp<span>
                                {2}
                            </h3>
                            """

        for section in sections:
            content = ''
            for i, subsection in enumerate(section[2]):
                if i == 0:
                    content += title_subheader.format(self.title[0],
                                                      section[0],
                                                      subsection[2])
                else:
                    formatted_paragraph = re.sub(r"^(\(\S+\))", r"<em>\1</em>",
                                                 subsection[2])
                    content += par_html.format(subsection[0],
                                               formatted_paragraph)
            rendered = section_html.format(content)
            yield (section[0], section[1], rendered)

    def write_part(self, title, part, sections):
        master_html = open('master.tmpl.html').read()
        table_boilerplate = open('table.tmpl.html').read()

        title_subheader = """<h3>
                                <a href="/">CFR</a><span>&nbsp/&nbsp</span>
                                <a href="html/titles/title{0}.html">
                                    Title {0}
                                </a><span>&nbsp/&nbsp</span>
                                Part {1}: {2}
                            </h3>
                            """.format(
                                title[0], part[0], part[1])
        section_data_row = """
                <tr>
                  <td scope="row"><a href="html/sections/{0}CFR{1}.{2}.html">
                        Section {1}.{2}
                        </a>
                  </td>
                  <td scope="row">{3}</td>
                </tr>
                """

        rows = ''
        for section in sections:
            rows += section_data_row.format(title[0], section[0],
                                            section[1], section[2])

        content = title_subheader + table_boilerplate.format('Section No.',
                                                             rows)
        html = master_html.format(content)

        filename = 'html/parts/{0}CFR{1}.html'.format(title[0], part[0])
        f = open(filename, 'w')
        f.write(html)
        f.close()

        print('wrote: %s' % filename)

    def write_title(self, title, parts):
        master_html = open('master.tmpl.html').read()
        table_boilerplate = open('table.tmpl.html').read()

        title_subheader = """<h3>
                                <a href="/">CFR</a> /
                                Title {0}: {1}</h3>
                            """.format(
                                title[0], title[1])
        part_data_row = """
                <tr>
                  <td scope="row"><a href="html/parts/{0}CFR{1}.html">Part {1}
                  </a></td>
                  <td scope="row">{2}</td>
                </tr>
                """

        rows = ''
        for part in parts:
            rows += part_data_row.format(title[0], part[0], part[1])

        content = title_subheader + table_boilerplate.format('Part No.', rows)
        html = master_html.format(content)

        filename = 'html/titles/title%s.html' % title[0]
        f = open(filename, 'w')
        f.write(html)
        f.close()

        print('wrote: %s' % filename)

    def write_index(self, titles):
        master_html = open('master.tmpl.html').read()
        table_boilerplate = open('table.tmpl.html').read()

        title_data_row = """
                <tr>
                  <th scope="row"><a href="html/titles/title{0}.html">Title {0}</a></th>
                  <td>{1}</td>
                </tr>
                """

        rows = ''
        for title in titles:
            rows += title_data_row.format(title[0], title[1])

        content = table_boilerplate.format('Title No.', rows)
        html = master_html.format(content)

        filename = 'index.html'
        f = open(filename, 'w')
        f.write(html)
        f.close()

        print('wrote: %s' % filename)

    def write_section(self, year, title, section):
        filename = 'html/sections/{0}CFR{1}.{2}.html'.format(title,
                                                             section[0],
                                                             section[1])
        f = open(filename, 'w')
        f.write(section[2])
        f.close()

    def get_title(self, filename):
        f = open(filename)
        head = ''
        for i, line in enumerate(f):
            head += line
            if i == 25:
                break
        match = re.match(".*\s+Title ([0-9]+)\s+((?:\S+\s)+)", head, re.S)
        title = match.groups()[0]
        description = match.groups()[1].strip()

        return (title, description)

    def run(self, title_start, title_end, debug,
            part_start, part_end):
        filenames = []
        for filename in os.listdir('data/text'):
            title = int(re.search("([0-9]+)CFR", filename).group(1))

            if title >= title_start and title <= title_end:
                filenames.append('data/text/' + filename)

        titles = []
        self.sections_processed = 0
        self.section_failures = 0
        for filename in filenames:
            self.title = self.get_title(filename)
            titles.append(self.title)
            match = re.search("[0-9]+CFR\-\(([0-9]+)\)", filename)
            year = match.groups()[0]

            f = open(filename)

            self.parts = []
            self.sections = {}

            sections = self.yield_sections(
                         self.find_sections(
                          self.clean_text(f)))

            if debug:
                sections = self.debug(sections)

            if part_start:
                sections = self.start_at_part(sections, part_start)

            if part_end:
                sections = self.end_at_part(sections, part_end)

            for result in self.render_sections(
                           self.parse_structure(sections)):
                self.write_section(year, self.title[0], result)
            self.write_title(self.title, self.parts)

            for part_key in self.sections:
                part = [p for p in self.parts if p[0] == part_key]

                if len(part) == 0:
                    print("Couldn't find part...")
                    print self.parts
                    print part_key
                    part = (part_key, 'Unknown Part')
                else:
                    part = part[0]
                self.write_part(self.title, part, self.sections[part_key])

            f.close()

        self.write_index(titles)

        # Report on failure rate
        failure_rate = 100*(float(self.section_failures /
                                  float(self.sections_processed)))
        print('%d sections processed, %d failures (%.2f%%)' %
              (self.sections_processed, self.section_failures,
               failure_rate))

if __name__ == "__main__":
    parser = Parser()
    debug = None
    title_start = 1
    title_end = 50
    part_start = None
    part_end = None
    for arg in sys.argv:
        if arg == '--debug':
            debug = True
        if arg.startswith('--title-start='):
            title_start = int(arg.split('=')[1])
        if arg.startswith('--title-end='):
            title_end = int(arg.split('=')[1])
        if arg.startswith('--part-start='):
            part_start = int(arg.split('=')[1])
        if arg.startswith('--part-end='):
            part_end = int(arg.split('=')[1])
    parser.run(title_start, title_end, debug, part_start, part_end)
