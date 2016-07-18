for i in `seq 1 50`; do
  echo starting title $i
  python parse_structure.py --title-start=$i --title-end=$i --debug && echo finished title $i &
  sleep 5
done
wait
python parse_structure.py --title-only
