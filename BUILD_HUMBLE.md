# Baxter ROS 2 (Humble) — Build & Run

This workspace controls a Baxter Research Robot from a ROS 2 Humble workstation.
Baxter itself runs **ROS 1**; the bridge to it is done over **rosbridge
(WebSocket) using `roslibpy`** — *not* `ros1_bridge`. There is therefore no need
to compile any ROS 1 code.

> Build this on **Ubuntu 22.04 + ROS 2 Humble**. It cannot be built on Windows
> (no native ROS 2). The Python sources have been syntax-checked, but a full
> `colcon build` must be run on a Humble machine.

## Packages

| Package | Type | Purpose |
|---|---|---|
| `baxter_common_ros2/baxter_core_msgs` | ament_cmake | Baxter message definitions |
| `baxter_common_ros2/baxter_maintenance_msgs` | ament_cmake | Calibration/maintenance messages |
| `baxter_common_ros2/baxter_description` | ament_cmake | URDF + meshes (RViz model) |
| `baxter_common_ros2/rethink_ee_description` | ament_cmake | Gripper descriptions |
| `baxter_common_ros2/baxter_bridge` | **COLCON_IGNORE'd** | ROS1↔ROS2 native bridge — *not used*, kept ignored on purpose |
| `baxter_dataflow` | ament_python | `wait_for`, `Signal` helpers |
| `baxter_interface` | ament_python | Baxter SDK classes ported to roslibpy |
| `baxter_ik` | ament_python | IK / tactile-experiment clients |
| `baxter_rosbridge_adapter` | ament_python | Joint-state bridge, RViz launch, interactive CLIs |

`baxter_bridge` stays disabled (its `COLCON_IGNORE` file). Remove that file only
if you specifically want to compile the native bridge (requires the ROS 1 message
toolchain); the rest of the workspace does not depend on it.

## 1. System / Python dependencies

```bash
sudo apt update
sudo apt install -y ros-humble-desktop python3-colcon-common-extensions \
    python3-rosdep ros-humble-robot-state-publisher ros-humble-xacro ros-humble-rviz2

# Python deps used by the roslibpy-based nodes
pip3 install roslibpy numpy opencv-python matplotlib
```

`rosdep` covers the declared dependencies:

```bash
cd ~/baxter_ros2_ws
rosdep install --from-paths src --ignore-src -r -y
```

### Optional / hardware-only deps
- `baxter_ik` nodes `daimon_sensor` and `live_classifier`, plus the
  offline `neural_network.py` trainer, need **PyTorch** (`pip3 install torch`) and
  the **proprietary Daimon SDK `dmrobotics`** (no public package). These are *not*
  required for the core nodes below and have no rosdep keys, so install them only
  if you use the tactile sensor.

## 2. Build

```bash
cd ~/baxter_ros2_ws
colcon build --symlink-install
source install/setup.bash
```

## 3. Configure the connection to Baxter

All nodes default to host `130.251.13.31`, port `9090`. Make sure
`rosbridge_server` is running on Baxter (ROS 1 side):

```bash
# on Baxter / its ROS 1 master
roslaunch rosbridge_server rosbridge_websocket.launch
```

Override the address at runtime, e.g.:

```bash
ros2 run baxter_rosbridge_adapter baxter_cli --ros-args -p baxter_host:=<IP> -p baxter_port:=9090
```

## 4. Run

**RViz visualization (live joint states):**
```bash
ros2 launch baxter_rosbridge_adapter baxter_visualization.launch.py
```

**Interactive robot CLI** (enable/disable, grippers, head, arm poses):
```bash
ros2 run baxter_rosbridge_adapter baxter_cli
```

**Grippers-only CLI:**
```bash
ros2 run baxter_rosbridge_adapter baxter_grippers_cli
```

**Arm calibration** (remove grippers first):
```bash
ros2 run baxter_rosbridge_adapter calibrate_arm --limb left
# or the baxter_interface entry point:
ros2 run baxter_interface Calibrate --limb left
```

**IK / experiment clients:**
```bash
ros2 run baxter_ik ik_baxter            # interactive IK swipe tool
ros2 run baxter_ik position_kinematics  # read endpoint pose
ros2 run baxter_ik repetitive_ik        # scripted repetitions
ros2 run baxter_ik test                 # connection smoke test
ros2 run baxter_ik daimon_sensor        # needs torch + dmrobotics + sensor hardware
```

## What was fixed for Humble

- **`baxter_interface`**: repaired broken imports (`from .baxter_dataflow import …`
  / `from .signals import …` → the local `.wait_for` module); added missing
  `import roslibpy`/`import time` and renamed `WebSocketHead` → `Head` in
  `head.py`; added real dependencies to `package.xml`; pruned 10 phantom
  `console_scripts` entry points that pointed at non-existent `main()` functions
  (the SDK modules are libraries — only `Calibrate` is a node).
- **`baxter_rosbridge_adapter`**: rewrote `calibrate_arm.py` from an incompatible
  native-rclpy form to the roslibpy paradigm used by the rest of the project;
  added the `baxter_interface` dependency; wrapped `robot_description` in
  `ParameterValue(..., value_type=str)` (required on Humble); corrected the launch
  filename in the README.
- **`baxter_ik`**: aligned `package.xml` with what the code actually imports
  (added numpy/opencv/matplotlib, dropped unused launch/rviz/urdf deps),
  documented the torch/dmrobotics hardware-only deps.
- **`baxter_dataflow`**: filled in description/license and `buildtool_depend`.

## Connection-failure handling

`roslibpy.Ros.run()` *raises* `RosTimeoutError` when it cannot reach rosbridge.
Previously every node called `run()` and then checked `is_connected` — dead code,
so a failed connection produced a raw Python traceback (see `LOG/log.txt`). All 11
connection sites (baxter_cli, baxter_grippers_cli, joint_state_bridge, both
calibrate_arm, ik_baxter, position_kinematics, repetitive_ik, test, daimon_sensor,
material_classification) now catch the failure and exit cleanly with:

```
Could not connect to Baxter rosbridge at ws://130.251.13.31:9090: Failed to connect to ROS.
Check that the robot is on, rosbridge_server is running, and the host/port are correct.
```

So the traceback in `LOG/log.txt` simply meant the robot was not reachable — set
the right address with `-p baxter_host:=<IP>` (adapter nodes) or `--host <IP>`
(calibrate_arm), and make sure `rosbridge_server` is running on Baxter.

## Known runtime caveats (research code in `baxter_ik`, not build blockers)

- Hard-coded host IP `130.251.13.31` and Daimon camera serial `S2508080069`.
- `daimon_sensor.py` writes datasets under `"Dataset"` while `neural_network.py`
  reads from `"DataSets"` — reconcile the folder name before training.
- Feature-count mismatch: `material_classification.py` builds a 5-feature model,
  but `utilities.preprocess_experiment_run` produces 4 features.
- `daimon_sensor.py` uses inconsistent relative path depths (5 vs 6 levels up) for
  its output dir; prefer an absolute path.

These depend on the experiment design and the physical tactile sensor, so they
were left for you to decide rather than guessed at.
