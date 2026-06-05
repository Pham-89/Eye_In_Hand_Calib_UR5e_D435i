
import os
import logging
import  yaml
import cv2
import numpy as np
from scipy.spatial.transform import Rotation as R

from libs.auxiliary import find_latest_data_folder
from libs.log_setting import CommonLog

from save_poses import poses_main

np.set_printoptions(precision=8,suppress=True)

logger_ = logging.getLogger(__name__)
logger_ = CommonLog(logger_)

# # latest dataset folder
current_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"eye_hand_data")

# image dataset directory
images_path = os.path.join("eye_hand_data",find_latest_data_folder(current_path))

# robot TCP poses file (poses.txt) - each line in .txt must match the corresponding image order
file_path = os.path.join(images_path,"poses.txt")


# load chessboard configuration from yaml file and convert to python dictionary
with open("config.yaml", 'r') as file:
    data = yaml.safe_load(file)  

XX = data.get("checkerboard_args").get("XX") # number of inner corners along x-axis
YY = data.get("checkerboard_args").get("YY") # number of inner corners along y-axis
L = data.get("checkerboard_args").get("L")   # chessboard square side [meter] 


def func():

     # current script directory
    path = os.path.dirname(__file__)

    ######################################
    # position corner at pixel level (int x, int y) 
    # however corners typically locate inside pixel -> sub-pixel corner (float x, float y)
    # refine sub-pixel corners: calculate sub-pixel corner from corner
    ######################################
    
    # termination criteria for sub-pixel corner refinement: max_iteration >= 30 or error =< 0.001
    criteria = (cv2.TERM_CRITERIA_MAX_ITER | cv2.TERM_CRITERIA_EPS, 30, 0.001)

    # create matrix 0 with shape number_cornersx3 (number_corners: xx*YY, 3 = position of corner (x, y, z))
    objp = np.zeros((XX * YY, 3), np.float32)
    # create a chessboard grid coordinate (x,y,0) (all corners on same plane: z=0)
    objp[:, :2] = np.mgrid[0:XX, 0:YY].T.reshape(-1, 2)
    # scale grid with chessboard square side     
    objp = L*objp

    obj_points = []     # create list to store 3D points
    img_points = []     # create list to store 2D points

    # get all calibration images from images_path
    images_num = [f for f in os.listdir(images_path) if f.endswith('.jpg')] 
    # loop through all images
    for i in range(1, len(images_num) + 1):  

        # full directory of current image: images_path/count.jpg
        image_file = os.path.join(images_path,f"{i}.jpg")

        if os.path.exists(image_file):
            logger_.info(f'reading image: {image_file}')

            # read image and convert to gray
            img = cv2.imread(image_file)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # size image: width x height
            size = gray.shape[::-1]
            # detect checkerboard corners and return its coordinate
            ret, corners = cv2.findChessboardCorners(gray, (XX, YY), None)

            if ret:  # if there is a corner
                obj_points.append(objp) # add to 3D list
                # refine corners to sub-pixel corners
                corners2 = cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), criteria)  
                
                # if refinement success: add sub-pixel corners to list 2D for calibration
                if [corners2]:
                    img_points.append(corners2)
                # if refinement failed: add origin corner to list 2D for calibration
                else:
                    img_points.append(corners)

    # number of corners for calibration
    N = len(img_points)
    print("N =", N)

    # calibrate camera to get
    # ret: return value, mtx: cam intrinsic matrix, dist: distortion coefficients
    # rvecs, tvecs: chessboard rotation matrix, translation vector wrt camera
    size = (1280, 720)
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, size, None, None)
    
    # compute chessboard pose wrt camera for each image
    # store as a list of calibrateHandEye() input
    R_cb = []
    t_cb = []
    for i in range(N):
    	ret, rvec, tvec = cv2.solvePnP(obj_points[i], img_points[i], mtx, dist)
    	R_cb.append(rvec)
    	t_cb.append(tvec)

    print("-----------------------------------------------------")

    # poses_main() from save_poses.py: read poses.txt at file_path directory
    # convert into homogenous transformation matrix and save as RoboToolPose.csv
    poses_main(file_path)   
    # create full directory to RobotToolPose.csv: path(current directory)/RobotToolPose.csv
    csv_file = os.path.join(path,"RobotToolPose.csv")
    # load TCP transform from csv file
    tool_pose = np.loadtxt(csv_file,delimiter=',')

    R_tool = [] # create a list to store TCP rotation matrix wrt base frame
    t_tool = [] # create a list to store TCP translation vector wrt base frame

    for i in range(int(N)):
        R_tool.append(tool_pose[0:3,4*i:4*i+3]) # add TCP rotation element to rotation matrix
        t_tool.append(tool_pose[0:3,4*i+3])     # add TCP translation element to translation vector

    # solve calibration equation to get R,t: camera rotation matrix, translation vector wrt TCP  
    Ro, tr = cv2.calibrateHandEye(R_tool, t_tool, R_cb, t_cb, cv2.CALIB_HAND_EYE_TSAI)

    return Ro,tr

if __name__ == '__main__':

    # calibration matrix [R t]
    rotation_matrix, translation_vector = func()

    # convert rotation matrix to quaternion
    rotation = R.from_matrix(rotation_matrix)
    quaternion = rotation.as_quat()
    # flaten translation vector (3,1) -> (3,)
    x, y, z = translation_vector.flatten()

    logger_.info(f"rotation matrix:\n {            rotation_matrix}")

    logger_.info(f"translation vector:\n {            translation_vector}")

    logger_.info(f"rotation quaternion：\n {             quaternion}")

