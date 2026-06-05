
import logging
import os
import sys
import numpy as np
import cv2
import pyrealsense2 as rs

from rtde_receive import RTDEReceiveInterface  # use to get UR5e pose via RTDE

from libs.log_setting import CommonLog
from libs.auxiliary import create_folder_with_date, get_ip, popup_message


# create dataset folder
cam0_origin_path = create_folder_with_date()

# logger
logger_ = logging.getLogger(__name__)
logger_ = CommonLog(logger_)


def callback(color_image, rtde_receive):

    # use global counter for image naming
    global count

    # display live stream
    cv2.imshow("Capture_Video", color_image)

    # keyboard input
    k = cv2.waitKey(1) & 0xFF

    # press 'q' to quit
    if k == ord('q'):
        logger_.info("Exit program")
        sys.exit(0)

    # press 's' to save data
    if k == ord('s'):
		
        # get current robot TCP pose
        state, pose = get_pose(rtde_receive)

        logger_.info(
            f'get state: {"successed" if state else "failed"}, '
            f'{f"current pose: {pose}" if state else None}')

        # save only if pose acquisition succeeds
        if state:

            # pose file path
            filename = os.path.join(cam0_origin_path, "poses.txt")
            # convert pose float list as .csv format
            with open(filename, 'a+') as f:
                pose_ = [str(i) for i in pose]
                new_line = f'{",".join(pose_)}\n'
                f.write(new_line)
            
            # image file path
            image_path = os.path.join(cam0_origin_path,f"{count}.jpg")
            
            # save image
            success = cv2.imwrite(image_path, color_image)

            if success:
                logger_.info(f"=== Data collection {count} round success ===")
                count += 1
            else:

                logger_.error_("Failed to save image")


def get_pose(rtde_receive):

    try:
        # UR5e TCP pose: [x, y, z, rx, ry, rz], unit: meters + radians
        pose = rtde_receive.getActualTCPPose()
        return True, pose
    except Exception as e:
        return False, f"Robot connection failed: {str(e)}"


def displayD435i(rtde_receive):

    # create RealSense pipeline
    pipeline = rs.pipeline()

    # create config object
    config = rs.config()

    # enable color stream, resize, configure format bgr uint8, frame per second 30
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8,30)

    try:
        # start pipeline
        pipeline.start(config)
    except Exception as e:
        logger_.error_(f"Camera connection failed!: {e}")
        popup_message("Reminder", "Camera connection failed")
        sys.exit(1)

    # initialize image counter
    global count
    count = 1

    logger_.info("Start hand-eye calibration dataset collection")

    try:
        while True:
            # wait for camera frames
            frames = pipeline.wait_for_frames()
            
            # get color frame only
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue
            
            # convert frame -> numpy array
            color_image = np.asanyarray(color_frame.get_data())

            # process frame
            callback(color_image, rtde_receive)

    finally:
        pipeline.stop() # stop camera
        cv2.destroyAllWindows() # close OpenCV windows


if __name__ == '__main__':

    # get robot IP
    robot_ip = get_ip()
    logger_.info(f'Robot IP: {robot_ip}')

    # verify robot IP
    if not robot_ip: # get_ip() return false -> not false = true and excute this block 
        popup_message("Warning", "Invalid robot IP")
        sys.exit(1)

    # verify RTDE connection
    try:
        # create a interface (RTDE client) to communicate with robot
        rtde_receive = RTDEReceiveInterface(robot_ip)
        logger_.info("UR5e RTDE connection OK")
        # start dataset collection
        displayD435i(rtde_receive)

    except Exception as e:
        logger_.error(f"RTDE connection failed: {e}")
        popup_message("Warning", "UR5e RTDE connection failed")
        sys.exit(1)
