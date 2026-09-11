import argparse
import sys
from time import sleep

from tamagonion import art
from tamagonion.app_data import AppData
from tamagonion.draw import Paper, Pen, Screen, StopDrawingException
from tamagonion.relay_manager import RelayManager


def main() -> None:
    args = get_args()

    relay_manager = RelayManager(ip_addr=args.ip, port=args.port, password=args.password, socket_file=args.socket_file)
    app_data = AppData(relay_manager)
    paper = Paper(app_data)

    Pen.erase(include_frame=True)
    Pen.hide_cursor().move_home()

    try:
        paper.setup_scan_key()
        while True:
            app_data.update()
            Pen.draw(art.frame, 0, 0)
            paper.draw()

            for _i in range(20):
                if key := paper.scan_key():
                    match key.lower():
                        case "h":
                            paper.active_screen = Screen.HOME
                        case "s":
                            paper.active_screen = Screen.STATUS
                        case "i":
                            paper.active_screen = Screen.HINT
                        case "q":
                            raise StopDrawingException
                    break
                sleep(0.05)
    except KeyboardInterrupt, StopDrawingException:
        pass
    finally:
        Pen.erase(include_frame=True)
        Pen.move_home().show_cursor()
        paper.tear_down_scan_key()

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
