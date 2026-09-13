from enum import Enum, auto


class Hints(Enum):
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


HINTS_TITLES = {
    Hints.BOOTSTRAP: "Bootstrap incomplete",
    Hints.NETWORK_LIVENESS: "Network down",
    Hints.ENOUGH_DIR_INFO: "Not enough directory information",
    Hints.REACHABILITY: "ORPort or DirPort unreachable",
    Hints.GOOD_SERVER_DESCRIPTOR: "Server descriptors denied",
    Hints.ED_CONSENSUS_FLAG: "NoEdConsensus flag",
    Hints.NO_VALID_FLAG: "Missing Valid flag",
    Hints.NO_RUNNING_FLAG: "Missing Running flag",
    Hints.VERSION_OBSOLETE: "Tor binary version is obsolete",
    Hints.VERSION_UNRECOMMENDED: "Tor binary version is not recommended",
    Hints.NO_STABLE_FLAG: "Missing Stable flag",
    Hints.MIDDLE_ONLY_FLAG: "MiddleOnly flag",
    Hints.BAD_EXIT_FLAG: "BadExit flag",
    Hints.NO_FAST_FLAG: "Missing Fast flag",
}

HINTS_DESCRIPTIONS = {
    Hints.BOOTSTRAP: 'Your relay is not done bootstrapping. Wait a few minutes, and if it is still incomplete, check your logs for any warnings or errors. Current bootstrap phase is: "{phase}" ({percent}%).',
    Hints.NETWORK_LIVENESS: "Tor has not observed any network activity for the past few seconds. Is your network down? If not, check your logs for any warnings or errors.",
    Hints.ENOUGH_DIR_INFO: "Our directory information is no longer up-to-date enough to build circuits. Is your network down? If not, check your logs for any warnings or errors.",
    Hints.REACHABILITY: "The Tor network is not able to reach your configured {ports}. Have you opened the correct ports to the internet? Is your network down?",
    Hints.GOOD_SERVER_DESCRIPTOR: "The directories have not accepted our server descriptors. Have you tampered with descriptor information? If not, check your logs for any warnings or errors.",
    Hints.ED_CONSENSUS_FLAG: "An Ed25519 key in the router's descriptor or microdescriptor does not reflect authority consensus. Have you tampered with descriptor information? If not, check your logs for any warnings or errors.",
    Hints.NO_VALID_FLAG: "Authorities have decided that your relay is not valid. Check your logs for any warnings or errors.",
    Hints.NO_RUNNING_FLAG: "Your relay is not currently usable over all its published ORPorts. Have you opened the correct ports to the internet? Is your network down?",
    Hints.VERSION_OBSOLETE: "Upgrade ASAP. Recommended is {version}.",
    Hints.VERSION_UNRECOMMENDED: "Upgrade NOW. Recommended is {version}.",
    Hints.NO_STABLE_FLAG: "Your relay has not been up for long enough or its mean time between failure is too low. Is the Tor process occasionally crashing? Is your server rebooting? Is your network stable?",
    Hints.MIDDLE_ONLY_FLAG: "Your relay is considered unsuitable for usage other than as a middle relay. Check your logs for any warnings or errors.",
    Hints.BAD_EXIT_FLAG: "Your relay is believed to be useless as an exit node because its ISP censors it, because it is behind a restrictive proxy, or for some similar reason. Take appropriate action.",
    Hints.NO_FAST_FLAG: "Your relay doesn't have enough bandwidth to build high-bandwidth circuits. Fit a bigger pipe, or accept that your relay will be underused.",
    Hints.OK: "Your Tamagonion has a clean bill of health!",
}


class Stats(Enum):
    NICKNAME = auto()
    UPTIME = auto()
    CONNECTIONS = auto()
    DOWNLOAD = auto()
    UPLOAD = auto()
    VERSION = auto()


STATS_DESCRIPTIONS = {
    Stats.NICKNAME: "Relay nickname: {name}",
    Stats.UPTIME: "Uptime: {uptime}",
    Stats.CONNECTIONS: "Connections (N/L/Co/F/Cl): {new}/{launched}/{connected}/{failed}/{closed}",
    Stats.DOWNLOAD: "Download (Cur/Avg/Tot): {current} / {average} / {total}",
    Stats.UPLOAD: "Upload (Cur/Avg/Tot): {current} / {average} / {total}",
    Stats.VERSION: "Version: {version}",
}


class Statuses(Enum):
    NETWORK_LIVENESS = auto()
    BOOTSTRAP_PROGRESS = auto()
    ENOUGH_DIR_INFO = auto()
    GOOD_SERVER_DESCRIPTOR = auto()
    REACHABILITY = auto()
    VERSION_STATUS = auto()


STATUSES_DESCRIPTION = {
    Statuses.NETWORK_LIVENESS: "Network liveness: {network_liveness}",
    Statuses.BOOTSTRAP_PROGRESS: "Bootstrap progress: {bootstrap_progress}",
    Statuses.ENOUGH_DIR_INFO: "Enough directory info: {enough_dir_info}",
    Statuses.GOOD_SERVER_DESCRIPTOR: "Good server descriptor: {good_server_descriptor}",
    Statuses.REACHABILITY: "Reachability: {reachability}",
    Statuses.VERSION_STATUS: "Version status: {version_status}",
}
