#!/usr/bin/env bash

video_dir="/home/salvadom/Data/OF_Profiling/videos"
frames_dir="/home/salvadom/Data/OF_Profiling/frames"
output_dir="/home/salvadom/Data/OF_Profiling/turing"

rm -rf ${output_dir}/*

for video_path in ${video_dir}/*.mp4; do
    video_name=${video_path:t:r}
    video_frames_dir=${frames_dir}/${video_name}
    video_output_dir=${output_dir}/${video_name}
    echo "AppOFCuda --input=${video_frames_dir}/*.jpg --output=${video_output_dir}/${video_name} --gpuIndex=0 --preset=medium"
    #python3 AppOFCuda --input=${video_frames_dir}/*.jpg --output=${video_output_dir}/${video_name} --gpuIndex=0 --preset=medium
done