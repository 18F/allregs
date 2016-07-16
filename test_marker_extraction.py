from regparser.tree.xml_parser.reg_text import get_markers, any_depth_p, collapsed_markers

text = """(b)(1) Pursuant to 5 U.S.C. 552a(j)(2), records contained in FEC 12,"""
"""
Office of Inspector General Investigative Files, are exempt from the
provisions of 5 U.S.C. 552a, except subsections (b), (c) (1) and (2),
(e)(4) (A) through (F), (e) (6), (7), (9), (10), and (11) and (f) , and
the corresponding provisions of 11 CFR part 1, to the extent this system
of records relates in any way to the enforcement of criminal laws."""

text = """(d) Meeting. (1) Meeting means the deliberation of at least
four voting members of the Commission in collegia where such deliberations
determine or result in the joint conduct or disposition of official Commission
business. For the purpose of this section, joint conduct does not include,
for example, situations where the requisite number of members is physically
present in one place but not conducting agency business as a body
(e.g., at a meeting at which one member is giving a speech while a
number of other members are present in the audience).
A deliberation conducted through telephone or similar
communications equipment by means\n\nof which all persons
participating can hear each other will be considered a
meeting under this section."""

text = """    (d) Meeting. (1) Meeting means the deliberation of at least four
voting members of the Commission in collegia where such deliberations
determine or result in the joint conduct or disposition of official
Commission business."""

print(get_markers(text))
print(any_depth_p.parseString(text))
print(collapsed_markers(text))
