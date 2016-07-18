for i in `seq 1 50`; do
  echo starting title $i
  python parse_structure.py --title-start=$i --title-end=$i && echo finished title $i &
  sleep 2
done
wait
python parse_structure.py --title-only
