import argparse
import sys
from time import sleep

from tamagonion.app_data import AppData
from tamagonion.draw import Paper
from tamagonion.relay_manager import RelayManager


def main() -> None:
    args = get_args()

    print("\033[2J\033[H", end="")  # Clear the screen and reset cursor
    relay_manager = RelayManager(ip_addr=args.ip, port=args.port, password=args.password, socket_file=args.socket_file)
    app_data = AppData(relay_manager)
    paper = Paper(app_data)

    try:
        while True:
            app_data.update()
            paper.draw()
            sleep(1)
    except KeyboardInterrupt:
        pass

    paper.erase(include_frame=True)
    sys.exit(0)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="tamagonion",
        description="This is Stinky, it's a Tamagonion and it's running your Tor relay.",
        epilog="Hack the planet!",
    )

    parser.add_argument(
        "-i", "--ip", help="IP of the Tor relay where the control protocol listens. Can also be a hostname. Defaults to 127.0.0.1.", default="127.0.0.1"
    )
    parser.add_argument("-p", "--port", help="Control port. Defaults to 9051.", default="9051")
    parser.add_argument("-P", "--password", help="Control port password, if any", required=False)
    parser.add_argument("-s", "--socket-file", help="Path to the socket file to use instead of an IP", required=False)

    return parser.parse_args()


if __name__ == "__main__":
    main()
