import re
from regparser.tree.xml_parser.reg_text import (get_markers,
                                                RegtextParagraphProcessor)
from regparser.tree.depth.derive import derive_depths
import sys

class Parser:
    def __init__(self):
        dummy_processor = RegtextParagraphProcessor()
        self.additional_constraints = dummy_processor.additional_constraints()
        # relaxed_constraints = dummy_processor.relaxed_constraints()

    def debug(self, lines):
        for i, line in enumerate(lines):
            if i > 1000:
                print('stopped (debug mode on)')
                break
            yield line

    def skip_page_counts(self, lines):
        for line in lines:
            if not re.search('\[\[[pP]age.*\]\]', line):
                yield line

    def add_section_text(self, lines):
        for line in lines:
            if re.match('Sec\.\s+([0-9]+)\.([0-9]+)', line):
                line = line.replace('Sec.', 'Section')
            yield line

    def find_sections(self, lines):
        part = None
        section = None
        for line in lines:
            section_start = re.match('Sec\.\s+([0-9]+)\.([0-9]+)', line)
            part_start = re.match("PART|\s+Subpart", line)

            part_match = re.match("PART ([0-9]+)_(.*)--", line)
            if part_match:
                self.parts.append((part_match.group(1),
                                  part_match.group(2).title()))
            if part_start:
                part = None
                section = None

            if section_start:
                part = section_start.groups()[0]
                section = section_start.groups()[1]

            if part and section:
                yield (part, section, line)

    def yield_sections(self, lines):
        last_section = None
        last_part = None
        text = ''
        for part, section, line in lines:
            if last_section and last_part and (section is not last_section \
             or part is not last_part):
                section_header = line + lines.next()[2]
                section_header = section_header.replace('\n', ' ')
                section_description = re.match(
                                        'Sec.\s+[0-9]+\.[0-9]+\s+([^\.]+)',
                                        section_header).group(1).strip()
                section_description = re.sub("\s+", " ", section_description)

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
        regex = "(\({}\))".format(marker)
        splits = re.split(regex, text, maxsplit=1)
        return splits[0], splits[1] + splits[2]

    def get_subsections(self, section):
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
                        head, tail = self.split_text_by_marker(marker, tail)
                        subsections.append((marker, tail))
        return subsections

    def get_depths(self, subsections):
        markers = [s[0] for s in subsections]
        solution = derive_depths(markers, self.additional_constraints)

        # if not solution:
        #    solution = derive_depths(markers, relaxed_constraints)

        if solution:
            depths = [assignment.depth for assignment in solution[0]]
        else:
            depths = [0]*len(markers)
            self.section_failures += 1

        result = []
        for depth, subsection in zip(depths, subsections):
                result.append((depth, subsection[0], subsection[1]))
        return result

    def parse_structure(self, sections):
        for section in sections:
            subsections = self.get_subsections(section)
            result = self.get_depths(subsections)
            self.sections_processed += 1
            yield [section[0], section[1], result]

    def render_sections(self, sections):
        section_html = open('master.tmpl.html').read()
        par_html = '<p class="depth{0}">{1}</p>'

        title_subheader = """<h3>
                                <a href="/">CFR</a><span>&nbsp/&nbsp</span>
                                <a href="/html/titles/title{0}.html">
                                    Title {0}
                                </a><span>&nbsp/&nbsp</span>
                                <a href="/html/parts/{0}CFR{1}.html">Part {1}</a><span>&nbsp/&nbsp<span>
                                {2}
                            </h3>
                            """

        for section in sections:
            content = ''
            for i, subsection in enumerate(section[2]):
                if i == 0:
                    content += title_subheader.format(self.title[0], section[0], subsection[2])
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
                                <a href="/html/titles/title{0}.html">
                                    Title {0}
                                </a><span>&nbsp/&nbsp</span>
                                Part {1}
                            </h3>
                            """.format(
                                title[0], part)
        section_data_row = """
                <tr>
                  <th scope="row"><a href="/html/sections/{0}CFR{1}.{2}.html">
                        Section {1}.{2}
                        </a>
                  </th>
                  <td>{3}</td>
                </tr>
                """

        rows = ''
        for section in sections:
            rows += section_data_row.format(title[0], section[0],
                                            section[1], section[2])

        content = title_subheader + table_boilerplate.format('Section No.', rows)
        html = master_html.format(content)

        filename = 'html/parts/{0}CFR{1}.html'.format(title[0], part)
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
                  <th scope="row"><a href="/html/parts/{0}CFR{1}.html">Part {1}
                  </a></th>
                  <td>{2}</td>
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
                  <th scope="row"><a href="/html/titles/title{0}.html">Title {0}</a></th>
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
        print('wrote: %s' % filename)

    def get_title(self, filename):
        f = open(filename)
        head = ''
        for i, line in enumerate(f):
            head += line
            if i == 100:
                break
        match = re.match(".*\s+Title ([0-9]+)\s+((?:\S+\s)+)", head, re.S)
        title = match.groups()[0]
        description = match.groups()[1].strip()

        return (title, description)

    def run(self, debug=False):
        filenames = ['data/text/CFR-2016-title11.txt']
        titles = []

        self.sections_processed = 0
        self.section_failures = 0
        for filename in filenames:
            self.title = self.get_title(filename)
            titles.append(self.title)
            match = re.search("CFR-([0-9]+)-title([0-9]+)", filename)
            year = match.groups()[0]

            f = open(filename)

            if debug:
                f = self.debug(f)

            self.parts = []
            self.sections = {}
            for result in self.render_sections(
                           self.parse_structure(
                            self.yield_sections(
                             self.find_sections(
                              self.skip_page_counts(f))))):
                self.write_section(year, self.title[0], result)
            self.write_title(self.title, self.parts)

            for part in self.sections:
                self.write_part(self.title, part, self.sections[part])

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

    debug = False
    if '--debug' in sys.argv:
        debug = True
    parser.run(debug)
