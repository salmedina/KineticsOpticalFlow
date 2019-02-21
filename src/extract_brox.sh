#!/bin/bash

python3 build_of.py /mnt/kinetics/video /mnt/kinetics/of_brox  --num_worker=6 --flow_type=brox --df_path=/home/salvadom/Devel/dense_flow --out_format=dir --ext=mp4 --frame_step=1 --num_gpu=6
