Calibration Intel realsense camera D435i, mounted on gripper of robot arm Universal UR5e

1. Hardwares
- Robot arm:
  + Universal Robot UR5e
  + IP address: 172.31.1.200
- Camera
  + Intel Realsense D435i
  + Cable ISY IUC-3000, USB to USB-C, 1 meter
- PC:
  + OS: Ubuntu 22.04
- Checkerboard
  + Calib.io
  + Type: Checkerboard
  + Rows x Columns x Checker size: 9x12x20 [unit: mm]
    
2. Softwares
- the package from my repo
- Configurate PC

3. PC Configuration
- Set up real-time scheduling
- Install RTDE driver
- Connect to the Robot via ethernet cable
- Setting IP address as 172.31.1.201
- Install SDK and update firmware for the camera
  + Note: building package librealsense2 with python wrapper SDK
    (-DBUILD_PYTHON_BINDINGS=true)
- Connect to Camera via USB cable

4. Collect Data
- Use teach pendant to power the robot on
- launch file collect_data.py from my package
- move TCP to a desired pose and press “s” to save data (images + TCP pose wrt base frame)
- moving TCP to other pose and repeat step 3 until get enough data

5. Computation
- Extract checker point pose (matrix B) from images
- Extract TCP pose (Matrix A) from dataset (file poses.txt)
- Use A & B to solve equation AX = XB for X
- All these steps can be done by launching file compute_in_hand.py
