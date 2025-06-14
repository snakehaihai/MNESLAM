import time
import copy
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from tqdm import tqdm

import os
import numpy as np
import torch
import torch.nn as nn
from colorama import Fore, Style
from collections import OrderedDict
from tqdm import tqdm
import cv2

# from lietorch import SE3
# from time import gmtime, strftime, time, sleep
# import torch.multiprocessing as mp

from tracker.droid_net import DroidNet
from tracker.frontend import Frontend
from tracker.backend import Backend
from tracker.depth_video import DepthVideo
from tracker.motion_filter import MotionFilter

class Tracker(nn.Module):

    def __init__(self, config, SLAM):
        super(Tracker, self).__init__()

        self.config = config
        self.device = SLAM.device

        self.tracking_idx = SLAM.tracking_idx
        self.mapping_idx = SLAM.mapping_idx

        self.net = SLAM.net
        self.video = SLAM.video

        # filter incoming frames so that there is enough motion
        self.frontend_window = config['tracking']['frontend']['window']
        filter_thresh = config['tracking']['motion_filter']['thresh']
        self.motion_filter = MotionFilter(self.net, self.video, thresh=filter_thresh, device=self.device)

        # # frontend process
        self.frontend = Frontend(self.net, self.video, self.config, device=self.device)

        self.tracking_finished = SLAM.tracking_finished

    def run(self, timestamp, image, depth, intrinsic, gt_pose):

        '''
        Tracking camera pose using of the current frame
        Params:
            batch['c2w']: Ground truth camera pose [B, 4, 4]
            batch['rgb']: RGB image [B, H, W, 3]
            batch['depth']: Depth image [B, H, W, 1]
            batch['direction']: Ray direction [B, H, W, 3]
            frame_id: Current frame id (int)
        '''

        with torch.no_grad():
            self.motion_filter.track(timestamp, image, depth, intrinsic, gt_pose=gt_pose)
            self.frontend()



