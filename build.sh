mkdir -p data/text
mkdir -p html/sections
mkdir -p html/titles
mkdir -p html/parts
mkdir fonts
npm install
cp node_modules/uswds/dist/css/uswds.min.css css
cp node_modules/uswds/dist/fonts/* fonts
python get_cfr_text.py
python parse_structure.py --debug
