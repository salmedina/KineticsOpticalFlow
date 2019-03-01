__author__ = 'yjxiong'

import os
import os.path as osp
import glob
import sys
from pipes import quote
from multiprocessing import Pool, current_process
import multiprocessing as mp
from joblib import Parallel, delayed
import argparse
import traceback

# GLOBALS
src_path = ''
out_path = ''


def dump_frames(vid_path):
    import cv2
    video = cv2.VideoCapture(vid_path)
    vid_name = vid_path.split('/')[-1].split('.')[0]
    out_full_path = osp.join(out_path, vid_name)

    fcount = int(video.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
    try:
        os.mkdir(out_full_path)
    except OSError:
        pass
    file_list = []
    for i in range(fcount):
        ret, frame = video.read()
        assert ret
        cv2.imwrite('{}/{:06d}.jpg'.format(out_full_path, i), frame)
        access_path = '{}/{:06d}.jpg'.format(vid_name, i)
        file_list.append(access_path)
    print('{} done'.format(vid_name))
    sys.stdout.flush()
    return file_list


def run_optical_flow(vid_item, algo_id, frame_step):
    vid_path, vid_id = vid_item
    out_full_path = osp.splitext(vid_path.replace(src_path, out_path))[0]
    vid_name = osp.basename(out_full_path)
    try:
        os.makedirs(out_full_path)
    except OSError:
        print('{} {} Skipping, cannot create {}'.format(vid_id, vid_name, out_full_path))
        return True

    current = current_process()
    dev_id = (int(current._identity[0]) - 1) % NUM_GPU + 2 # Touching from GPU #2
    image_path = 'None'
    flow_x_path = '{}/flow_x'.format(out_full_path)
    flow_y_path = '{}/flow_y'.format(out_full_path)

    # Extract OF 
    cmd = osp.join(df_path, 'build/extract_gpu')+' -f={} -x={} -y={} -i={} -b=20 -t={} -d={} -s={} -o={}'.format(
        quote(vid_path), quote(flow_x_path), quote(flow_y_path), quote(image_path), algo_id, dev_id, frame_step, out_format)
    
    try: 
        os.system(cmd)
    except:
        print('{} {} ERROR {}'.format(vid_id, vid_name, traceback.print_exc()))
        return False

    print('{} {} done'.format(vid_id, vid_name))
    sys.stdout.flush()
    return True

def save_list(in_list, save_path):
    with open(save_path, 'w') as save_file:
        save_file.write('\n'.join(in_list))

def load_list(load_path):
    loaded_list = None
    with open(load_path, 'r') as load_file:
        loaded_list = load_file.read().splitlines()
    return loaded_list

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="extract optical flows")
    parser.add_argument("src_dir")
    parser.add_argument("out_dir")
    parser.add_argument("--num_worker", type=int, default=8)
    parser.add_argument("--flow_type", type=str, default='tvl1', choices=['tvl1', 'farneback', 'brox'])
    parser.add_argument("--df_path", type=str, default='/code/app/dense_flow/', help='path to the dense_flow toolbox')
    parser.add_argument("--out_format", type=str, default='dir', choices=['dir','zip'],
                        help='path to the dense_flow toolbox')
    parser.add_argument("--ext", type=str, default='mp4', help='video file extensions')
    parser.add_argument("--frame_step", type=int, default=1, help='frame steps')
    parser.add_argument("--new_width", type=int, default=0, help='resize image width')
    parser.add_argument("--new_height", type=int, default=0, help='resize image height')
    parser.add_argument("--num_gpu", type=int, default=4, help='number of GPU')
    parser.add_argument("--start_index", type=int, default=0, help='start index in video list')

    args = parser.parse_args()

    out_path = args.out_dir
    src_path = args.src_dir
    num_worker = args.num_worker
    flow_type = args.flow_type
    df_path = args.df_path
    out_format = args.out_format
    ext = args.ext
    frame_step = args.frame_step
    new_size = (args.new_width, args.new_height)
    NUM_GPU = args.num_gpu
    start_index = args.start_index

    flow_type_dict = dict(tvl1=1, farneback=0, brox=2)

    if not osp.isdir(out_path):
        print("creating folder: "+out_path)
        os.makedirs(out_path)

    vid_list = []
    if not osp.exists('vidlist.cache'):
        print('Listing video files')
        vid_list = list(glob.iglob(osp.join(src_path, '**/*.%s' % ext), recursive=True))
        save_list('vidlist.cache', vid_list)
    else:
        print('Loading cached video list')
        vid_list = load_list('vidlist.cache')

    total_videos = len(vid_list)
    print('Total videos: {}'.format(total_videos))
    print('Starting processing from: {}'.format(start_index))

    if flow_type in flow_type_dict.keys():
        Parallel(n_jobs=num_worker)(delayed(run_optical_flow)(vid_item=vid_item, algo_id=flow_type_dict[flow_type], frame_step=args.frame_step) for vid_item in zip(vid_list[start_index:], range(start_index, total_videos)))
