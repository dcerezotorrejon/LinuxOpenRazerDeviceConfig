import signal
import threading
from collections.abc import Callable

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib


class SystemSignalHandler:
    def __init__(self, on_stop: Callable[[int, object], None]):
        self.on_stop = on_stop

    def register_handlers(self) -> None:
        signal.signal(signal.SIGINT, self.on_stop)
        signal.signal(signal.SIGTERM, self.on_stop)
        signal.signal(signal.SIGHUP, self.on_stop)
        signal.signal(signal.SIGQUIT, self.on_stop)


class SystemSleepListener:
    def __init__(self, on_sleep_event: Callable[[bool], None]):
        self.on_sleep_event = on_sleep_event
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Inicializa el listener de DBus para eventos de suspension."""
        try:
            DBusGMainLoop(set_as_default=True)
            bus = dbus.SystemBus()
            bus.add_signal_receiver(
                self.on_sleep_event,
                signal_name="PrepareForSleep",
                dbus_interface="org.freedesktop.login1.Manager",
                bus_name="org.freedesktop.login1",
            )

            def run_loop() -> None:
                loop = GLib.MainLoop()
                loop.run()

            self._thread = threading.Thread(target=run_loop, daemon=True)
            self._thread.start()
            print("Listener de suspension (DBus) iniciado correctamente.")
        except Exception as e:
            print(f"Advertencia: No se pudo configurar el listener de suspension. {e}")
