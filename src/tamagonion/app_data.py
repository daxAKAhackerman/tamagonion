from collections import defaultdict
from enum import StrEnum
from typing import Any, Self

from stem import DescriptorUnavailable
from stem.version import Version

from tamagonion import strings
from tamagonion.relay_manager import RelayManager

SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = SECONDS_IN_MINUTE * 60
SECONDS_IN_DAY = SECONDS_IN_HOUR * 24


class Flag(StrEnum):
    BAD_EXIT = "BadExit"
    EXIT = "Exit"
    FAST = "Fast"
    GUARD = "Guard"
    HS_DIR = "HSDir"
    MIDDLE_ONLY = "MiddleOnly"
    STABLE = "Stable"
    STALE_DESC = "StaleDesc"
    V2_DIR = "V2Dir"
    NO_ED_CONSENSUS = "NoEdConsensus"
    RUNNING = "Running"
    VALID = "Valid"


class VersionStatus(StrEnum):
    RECOMMENDED = "recommended"
    OBSOLETE = "obsolete"
    NEW = "new"
    NEW_IN_SERIES = "new in series"
    UNRECOMMENDED = "unrecommended"
    NONE_RECOMMENDED = "none recommended"
    UNKNOWN = "unknown"


class ORConnStatus(StrEnum):
    NEW = "NEW"
    LAUNCHED = "LAUNCHED"
    CONNECTED = "CONNECTED"
    FAILED = "FAILED"
    CLOSED = "CLOSED"


class AppData:
    relay_manager: RelayManager
    flags: list[str]
    version: Version
    recommended_version: str
    info: dict[str, Any]
    version_status: VersionStatus = VersionStatus.UNKNOWN
    uptime: float = 0.0
    connection_status_map: defaultdict[ORConnStatus, int]
    relay_name: str = strings.MISC_STRINGS[strings.Misc.UNKNOWN]
    orport: str = strings.MISC_STRINGS[strings.Misc.UNKNOWN]
    dirport: str = strings.MISC_STRINGS[strings.Misc.UNKNOWN]
    frame: int = 0
    frame_skip: bool = False
    instance: Self | None = None

    def __init(self, relay_manager: RelayManager) -> None:
        self.info = {}
        self.version = Version(strings.MISC_STRINGS[strings.Misc.HOME_DEFAULT_VERSION])
        self.flags = []
        self.connection_status_map = defaultdict(lambda: 0)

        self.relay_manager = relay_manager
        self._get_version()
        self._get_recommended_version()
        self._get_version_status()
        self._get_relay_name()
        self._get_orport()
        self._get_dirport()

    def __new__(cls, *args, **kwargs) -> Self:
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.__init(*args, **kwargs)
        return cls.instance

    def update(self) -> None:
        self._get_flags()
        self._get_uptime()
        self._get_info()
        self._get_orconn_status()

    def _get_flags(self) -> None:
        try:
            self.flags = self.relay_manager.controller.get_network_status().flags
        except DescriptorUnavailable:
            self.flags = []

    def _get_uptime(self) -> None:
        self.uptime = self.relay_manager.controller.get_uptime()

    @property
    def formated_uptime(self) -> str:
        uptime_as_int = int(self.uptime)
        days = uptime_as_int // SECONDS_IN_DAY
        hours = (uptime_as_int % SECONDS_IN_DAY) // SECONDS_IN_HOUR
        minutes = (uptime_as_int % SECONDS_IN_HOUR) // SECONDS_IN_MINUTE
        seconds = uptime_as_int % SECONDS_IN_MINUTE

        return f"{days}{strings.SUFFIXES[strings.Suffix.DAYS]} {hours:02}{strings.SUFFIXES[strings.Suffix.HOURS]} {minutes:02}{strings.SUFFIXES[strings.Suffix.MINUTES]} {seconds:02}{strings.SUFFIXES[strings.Suffix.SECONDS]}"

    def _get_version(self) -> None:
        self.version = self.relay_manager.controller.get_version()

    def _get_version_status(self) -> None:
        self.version_status = VersionStatus(self.relay_manager.controller.get_info("status/version/current"))

    def _get_recommended_version(self) -> None:
        self.recommended_version = self.relay_manager.controller.get_info("status/version/recommended") or strings.MISC_STRINGS[strings.Misc.UNKNOWN]

    def _get_relay_name(self) -> None:
        self.relay_name = self.relay_manager.controller.get_conf("Nickname") or strings.MISC_STRINGS[strings.Misc.UNKNOWN]

    def _get_orport(self) -> None:
        self.orport = self.relay_manager.controller.get_conf("ORPort") or strings.MISC_STRINGS[strings.Misc.UNKNOWN]

    def _get_dirport(self) -> None:
        self.dirport = self.relay_manager.controller.get_conf("DirPort") or strings.MISC_STRINGS[strings.Misc.UNKNOWN]

    def _get_info(self) -> None:
        bw_event_cache = self.relay_manager.controller.get_info("bw-event-cache")
        bw_event_latest = bw_event_cache.split(" ")[-1].split(",")
        traffic_read = self.relay_manager.controller.get_info("traffic/read")
        traffic_written = self.relay_manager.controller.get_info("traffic/written")
        bootstrap_phase = self.relay_manager.controller.get_info("status/bootstrap-phase").split(" ")[-1].split("=", 1)[-1].strip('"')

        self.info = {
            "traffic_read": int(traffic_read),
            "traffic_written": int(traffic_written),
            "bw_event_cache_down": int(bw_event_latest[0]),
            "bw_event_cache_up": int(bw_event_latest[1]),
            "bw_avg_down": int(traffic_read) / self.uptime,
            "bw_avg_up": int(traffic_written) / self.uptime,
            "network_liveness": self.relay_manager.controller.get_info("network-liveness") == "up",
            "bootstrap_percent": int(self.relay_manager.controller.get_info("status/bootstrap-phase").split(" ")[2].split("=")[-1]),
            "bootstrap_phase": bootstrap_phase,
            "enough_dir_info": self.relay_manager.controller.get_info("status/enough-dir-info") == "1",
            "good_server_descriptor": self.relay_manager.controller.get_info("status/good-server-descriptor") == "1",
            "reachability": self.relay_manager.controller.get_info("status/reachability-succeeded/or") == "1",
        }

    def _get_orconn_status(self) -> None:
        self.connection_status_map = defaultdict(lambda: 0)
        orconn_status = self.relay_manager.controller.get_info("orconn-status")

        for status in orconn_status.splitlines():
            _node, state = status.split(" ")
            self.connection_status_map[ORConnStatus(state)] += 1

    @staticmethod
    def format_bytes(b: int) -> str:
        if b < 10**3:
            return f"{int(b)}{strings.SUFFIXES[strings.Suffix.BYTES]}"
        elif b < 10**6:
            return f"{int(b / (10**3))}{strings.SUFFIXES[strings.Suffix.KILOBYTES]}"
        elif b < 10**9:
            return f"{int(b / (10**6))}{strings.SUFFIXES[strings.Suffix.MEGABYTES]}"
        else:
            return f"{int(b / (10**9))}{strings.SUFFIXES[strings.Suffix.GIGABYTES]}"
