#!/bin/bash
autoproc=/home/ndhuang/spt_code/sptpol_software/autotools/autoprocess_spt_data.py

python $autoproc idf_ra23hdec-35_clusters --processes=3 --threads=6
python $autoproc idf_ra1hdec-35_clusters --processes=3 --threads=6
python $autoproc idf_ra3hdec-35_clusters --processes=3 --threads=6
python $autoproc idf_ra5hdec-35_clusters --processes=3 --threads=6
python $autoproc idf_ra3hdec-25_clusters --processes=3 --threads=6