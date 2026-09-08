from typing import Self

from stem.control import Controller, EventType

from tamagonion.utils import is_host_local


class RelayManager:
    controller: Controller
    is_local: bool = False
    instance: Self | None = None

    def __init(self, ip_addr: str, port: str, password: str | None, socket_file: str | None) -> None:
        if socket_file:
            self.controller = Controller.from_socket_file(socket_file)
        else:
            self.controller = Controller.from_port(address=ip_addr, port=int(port))  # type:ignore
        if password:
            self.controller.authenticate("password")
        else:
            self.controller.authenticate()

        if socket_file or is_host_local(ip_addr):
            self.is_local = True

        self.controller.add_event_listener(lambda: True, EventType["BW"])

    def __new__(cls, *args, **kwargs) -> Self:
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance.__init(*args, **kwargs)
        return cls.instance
