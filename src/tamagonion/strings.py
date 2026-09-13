from enum import Enum, auto

from tamagonion import art


class Hint(Enum):
    BOOTSTRAP = auto()
    NETWORK_LIVENESS = auto()
    ENOUGH_DIR_INFO = auto()
    REACHABILITY = auto()
    GOOD_SERVER_DESCRIPTOR = auto()
    ED_CONSENSUS_FLAG = auto()
    NO_VALID_FLAG = auto()
    NO_RUNNING_FLAG = auto()
    VERSION_OBSOLETE = auto()
    VERSION_UNRECOMMENDED = auto()
    NO_STABLE_FLAG = auto()
    MIDDLE_ONLY_FLAG = auto()
    BAD_EXIT_FLAG = auto()
    NO_FAST_FLAG = auto()
    OK = auto()


HINT_TITLES = {
    Hint.BOOTSTRAP: "Bootstrap incomplete",
    Hint.NETWORK_LIVENESS: "Network down",
    Hint.ENOUGH_DIR_INFO: "Not enough directory information",
    Hint.REACHABILITY: "ORPort or DirPort unreachable",
    Hint.GOOD_SERVER_DESCRIPTOR: "Server descriptors denied",
    Hint.ED_CONSENSUS_FLAG: "NoEdConsensus flag",
    Hint.NO_VALID_FLAG: "Missing Valid flag",
    Hint.NO_RUNNING_FLAG: "Missing Running flag",
    Hint.VERSION_OBSOLETE: "Tor binary version is obsolete",
    Hint.VERSION_UNRECOMMENDED: "Tor binary version is not recommended",
    Hint.NO_STABLE_FLAG: "Missing Stable flag",
    Hint.MIDDLE_ONLY_FLAG: "MiddleOnly flag",
    Hint.BAD_EXIT_FLAG: "BadExit flag",
    Hint.NO_FAST_FLAG: "Missing Fast flag",
}

HINT_DESCRIPTIONS = {
    Hint.BOOTSTRAP: 'Your relay is not done bootstrapping. Wait a few minutes, and if it is still incomplete, check your logs for any warnings or errors. Current bootstrap phase is: "{phase}" ({percent}%).',
    Hint.NETWORK_LIVENESS: "Tor has not observed any network activity for the past few seconds. Is your network down? If not, check your logs for any warnings or errors.",
    Hint.ENOUGH_DIR_INFO: "Our directory information is no longer up-to-date enough to build circuits. Is your network down? If not, check your logs for any warnings or errors.",
    Hint.REACHABILITY: "The Tor network is not able to reach your configured {ports}. Have you opened the correct ports to the internet? Is your network down?",
    Hint.GOOD_SERVER_DESCRIPTOR: "The directories have not accepted our server descriptors. Have you tampered with descriptor information? If not, check your logs for any warnings or errors.",
    Hint.ED_CONSENSUS_FLAG: "An Ed25519 key in the router's descriptor or microdescriptor does not reflect authority consensus. Have you tampered with descriptor information? If not, check your logs for any warnings or errors.",
    Hint.NO_VALID_FLAG: "Authorities have decided that your relay is not valid. Check your logs for any warnings or errors.",
    Hint.NO_RUNNING_FLAG: "Your relay is not currently usable over all its published ORPorts. Have you opened the correct ports to the internet? Is your network down?",
    Hint.VERSION_OBSOLETE: "Upgrade ASAP. Recommended is {version}.",
    Hint.VERSION_UNRECOMMENDED: "Upgrade NOW. Recommended is {version}.",
    Hint.NO_STABLE_FLAG: "Your relay has not been up for long enough or its mean time between failure is too low. Is the Tor process occasionally crashing? Is your server rebooting? Is your network stable?",
    Hint.MIDDLE_ONLY_FLAG: "Your relay is considered unsuitable for usage other than as a middle relay. Check your logs for any warnings or errors.",
    Hint.BAD_EXIT_FLAG: "Your relay is believed to be useless as an exit node because its ISP censors it, because it is behind a restrictive proxy, or for some similar reason. Take appropriate action.",
    Hint.NO_FAST_FLAG: "Your relay doesn't have enough bandwidth to build high-bandwidth circuits. Fit a bigger pipe, or accept that your relay will be underused.",
    Hint.OK: "Your Tamagonion has a clean bill of health!",
}


class Stat(Enum):
    NICKNAME = auto()
    UPTIME = auto()
    CONNECTIONS = auto()
    DOWNLOAD = auto()
    UPLOAD = auto()
    VERSION = auto()


STAT_DESCRIPTIONS = {
    Stat.NICKNAME: "Relay nickname: {name}",
    Stat.UPTIME: "Uptime: {uptime}",
    Stat.CONNECTIONS: "Connections (N/L/Co/F/Cl): {new}/{launched}/{connected}/{failed}/{closed}",
    Stat.DOWNLOAD: "Download (Cur/Avg/Tot): {current} / {average} / {total}",
    Stat.UPLOAD: "Upload (Cur/Avg/Tot): {current} / {average} / {total}",
    Stat.VERSION: "Version: {version}",
}


class Status(Enum):
    NETWORK_LIVENESS = auto()
    BOOTSTRAP_PROGRESS = auto()
    ENOUGH_DIR_INFO = auto()
    GOOD_SERVER_DESCRIPTOR = auto()
    REACHABILITY = auto()
    VERSION_STATUS = auto()
    FLAGS = auto()


STATUS_DESCRIPTION = {
    Status.NETWORK_LIVENESS: "Network liveness: {network_liveness}",
    Status.BOOTSTRAP_PROGRESS: "Bootstrap progress: {bootstrap_progress}",
    Status.ENOUGH_DIR_INFO: "Enough directory info: {enough_dir_info}",
    Status.GOOD_SERVER_DESCRIPTOR: "Good server descriptor: {good_server_descriptor}",
    Status.REACHABILITY: "Reachability: {reachability}",
    Status.VERSION_STATUS: "Version status: {version_status}",
    Status.FLAGS: "Flags: ",
}


class Misc(Enum):
    HINT_ORPORT_UNREACHABLE = auto()
    HINT_DIRPORT_UNREACHABLE = auto()
    HINT_ORPORT_AND_DIRPORT_UNREACHABLE = auto()
    HINT_MENU = auto()
    STATUS_LIVE = auto()
    STATUS_DOWN = auto()
    STATUS_REACHABLE = auto()
    STATUS_UNREACHABLE = auto()
    STATUS_YES = auto()
    STATUS_NO = auto()
    UNKNOWN = auto()
    HOME_DEFAULT_VERSION = auto()


MISC_STRINGS = {
    Misc.HINT_ORPORT_UNREACHABLE: "ORPort ({orport}) or DirPort ({dirport})",
    Misc.HINT_DIRPORT_UNREACHABLE: "ORPort ({orport})",
    Misc.HINT_ORPORT_AND_DIRPORT_UNREACHABLE: "DirPort ({dirport})",
    Misc.HINT_MENU: f"|{{up_dim}}Scroll {art.Effect.BOLD}{art.Effect.UNDERLINE}u{art.Effect.RESET}{{up_dim}}p{art.Effect.RESET}|{{down_dim}}Scroll {art.Effect.BOLD}{art.Effect.UNDERLINE}d{art.Effect.RESET}{{down_dim}}own{art.Effect.RESET}",
    Misc.STATUS_LIVE: "Live",
    Misc.STATUS_DOWN: "Down",
    Misc.STATUS_REACHABLE: "Reachable",
    Misc.STATUS_UNREACHABLE: "Unreachable",
    Misc.STATUS_YES: "Yes",
    Misc.STATUS_NO: "No",
    Misc.UNKNOWN: "Unknown",
    Misc.HOME_DEFAULT_VERSION: "0.0.0.0",
}


class Suffix(Enum):
    PERCENT = auto()
    BYTES = auto()
    KILOBYTES = auto()
    MEGABYTES = auto()
    GIGABYTES = auto()
    DAYS = auto()
    HOURS = auto()
    MINUTES = auto()
    SECONDS = auto()


SUFFIXES = {
    Suffix.PERCENT: "%",
    Suffix.BYTES: "B",
    Suffix.KILOBYTES: "KB",
    Suffix.MEGABYTES: "MB",
    Suffix.GIGABYTES: "GB",
    Suffix.DAYS: "d",
    Suffix.HOURS: "h",
    Suffix.MINUTES: "m",
    Suffix.SECONDS: "s",
}


class Separator(Enum):
    COMMA = auto()
    NEW_LINE = auto()


SEPARATORS = {Separator.COMMA: ", ", Separator.NEW_LINE: "\n"}
