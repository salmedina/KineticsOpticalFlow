#!/usr/bin/env bash

video_dir=$1
output_dir=$2

for file in ${video_dir}/*.mp4; do
    filename=$(basename -- "$file")
    filename="${filename%.*}"
    echo "${output_dir}/${filename}"
    mkdir -p "${output_dir}/${filename}";
    ffmpeg -i "$file" -r 1 "$destination/%06d.jpg";
done