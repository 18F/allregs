mkdir -p data/text
mkdir -p html/sections
mkdir -p html/titles
mkdir -p html/parts
python get_cfr_text.py
python parse_structure.py --debug
