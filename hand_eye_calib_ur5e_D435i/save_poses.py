"""
convert TCP poses to homogenous transformation matrix 4x4 and save as csv file
"""
import csv
import numpy as np
import cv2

# ur5e return rotation vector (axis-angle) i.e rotate around vector v=[1, 1, 1]
# convert rotation vector to rotation matrix (TCP wrt base)
def rotation_axis_to_rotation_matrix(rx, ry, rz):
    R_, _ = cv2.Rodrigues(np.array([rx, ry, rz], dtype=np.float64))
    return R_


def pose_to_homogeneous_matrix(pose):

    x, y, z, rx, ry, rz = pose
    R = rotation_axis_to_rotation_matrix(rx, ry, rz) # rotation matrix
    t = np.array([x, y, z]).reshape(3, 1)            # translation vector (column)
    
    # homogenous matrix
    H = np.eye(4)        # identify matrix 4x4
    H[:3, :3] = R        # assign R to first 3x3  
    H[:3, 3] = t[:, 0]   # assign t to last column

    return H


def save_matrices_to_csv(matrices, file_name):

    rows, cols = matrices[0].shape # shape of first homo matrix (4x4) 
    num_matrices = len(matrices)   # number of TCP poses
    combined_matrix = np.zeros((rows, cols * num_matrices)) # create a matrix 0 4X(4*number of TCP poses)

    # loop through all matrices
    for i, matrix in enumerate(matrices):
        # stack each matrix to 4 columns horizontally -> H =[H1|H2|H3|...]
        combined_matrix[:, i * cols: (i + 1) * cols] = matrix

    with open(file_name, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        for row in combined_matrix: # each row in H will be overwritten into 1 line of csv file
            csv_writer.writerow(row)


def poses_main(filepath):

    # open poses.txt
    with open(filepath, "r") as f:
        # read all lines from .txt file
        lines = f.readlines()

    # iterate through each line of txt file and flatten data
    lines = [float(i) for line in lines for i in line.split(',')]

    matrices = [] # create a list to store transformation matrix
    for i in range(0,len(lines),6):  # iterate every pose
        matrices.append(pose_to_homogeneous_matrix(lines[i:i+6])) # each pose (6 steps) -> homogenous matrix


    # save homogenous transformation matrix as RobotToolPoase.csv
    save_matrices_to_csv(matrices, f'RobotToolPose.csv')

