#!/usr/bin/env bash

video_dir=$1
output_dir=$2

for file in ${video_dir}/*.mp4; do
    filename=$(basename -- "$file")
    filename="${filename%.*}"
    destination="${output_dir}/${filename}"
    echo ${destination}
    mkdir -p "${output_dir}/${filename}";
    ffmpeg -i "$file" "$destination/%06d.jpg";
done