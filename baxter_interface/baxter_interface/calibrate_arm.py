import argparse
import sys
import roslibpy
from baxter_interface.robot_enable import RobotEnable
from baxter_interface.robust_controller import RobustController

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--limb', required=True, choices=['left', 'right'])
    args = parser.parse_args()

    # WebSocket Connection
    host, port = '130.251.13.31', 9090
    client = roslibpy.Ros(host=host, port=port)
    try:
        client.run()
    except Exception as exc:
        print(f"ERROR: could not connect to Baxter rosbridge at ws://{host}:{port}: {exc}\n"
              "Check that the robot is on, rosbridge_server is running, and the host/port are correct.",
              file=sys.stderr)
        sys.exit(1)

    print("Enabling Robot...")
    rs = RobotEnable(client)
    rs.enable()

    print(f"Calibrating {args.limb} arm...")
    cat = RobustController(
        client, 
        f'/robustcontroller/{args.limb}/CalibrateArm',
        {'isEnabled': True, 'uid': 'sdk'},
        {'isEnabled': False, 'uid': 'sdk'}
    )
    cat.run()

    rs.disable()
    client.terminate()
    print("Done!")

if __name__ == '__main__':
    main()