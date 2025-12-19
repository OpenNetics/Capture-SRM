
# talk/talk.py

#- Imports -----------------------------------------------------------------------------------------

import threading
from typing import Optional

import serial
from redwrenlib.utils.debug import alert

from .utils import all_ports, BAUDRATES
from .talk_signal import TalkSignals


#- Talk Class --------------------------------------------------------------------------------------

class Talk:

    # Initialises the Talk class, setting up signals and default serial parameters.
    def __init__(self):
        self.signals = TalkSignals()

        self._port: str = ""
        self._baudrate: int = 115200  # default rate

        self._serial_connection: Optional[serial.Serial] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False


    #- Getter/Setter -------------------------------------------------------------------------------

    # Returns the current serial port.
    @property
    def port(self) -> str: return self._port


    # Sets the serial port and restarts the connection if valid.
    @port.setter
    def port(self, port: str) -> None:
        self._cleanup() # safely close the existing connection

        if port in all_ports():
            self._port = port
            self._restart_connection()  # restart the connection
            return

        alert(f"Invalid port selected: {port}")


    # Returns the current baudrate.
    @property
    def baudrate(self) -> int: return self._baudrate


    # Sets the baudrate and restarts the connection if valid.
    @baudrate.setter
    def baudrate(self, rate: str) -> None:
        self._cleanup()

        if rate in BAUDRATES:
            self._baudrate = int(rate)
            self._restart_connection() # restart the connection
            return

        alert(f"Invalid baudrate selected: {rate}")


    #- Private Methods -----------------------------------------------------------------------------

    # Continuously reads data from the serial connection and emits signals for received data.
    def _read_loop(self):
        data_buffer = bytearray()

        while self._running and self._serial_connection and self._serial_connection.is_open:
            try:
                data = self._serial_connection.read()  # read byte-by-byte to handle partial lines

                if data:
                    b = data[0]
                    if b == 10:  # newline '\n'
                        line = data_buffer.decode(errors="replace").rstrip("\r")
                        data_buffer.clear()
                        self.signals.line_received.emit(line)

                    else:
                        data_buffer.append(b)
                        self.signals.single_received.emit(bytes([b]).decode('ascii'))

                else:
                    continue  # read timed out; allow loop to check _running

            except Exception as e:
                # alert(e) # uncomment to debug

                # ignore the error: otherwise prints logs for if invalid baudrate is selected among
                # other errors
                pass

        self._cleanup()


    # Safely closes the serial connection and cleans up resources.
    def _cleanup(self):
        if self._serial_connection:
            try:
                if self._serial_connection.is_open: self._serial_connection.close()

            except Exception: pass

            self._serial_connection = None


    # Stops the current read loop and restarts the connection with updated settings.
    def _restart_connection(self):
        # stop read loop and wait
        self._running = False
        if self._thread: self._thread.join(timeout=1.0)

        # start the system again
        self.start()


    #- Public Methods ------------------------------------------------------------------------------

    # Initialises the serial connection and starts the reading thread.
    def start(self) -> None:
        if not self._port: return

        try:
            self._serial_connection = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                timeout=1.0
            )

        except Exception as e:
            alert(f"Failed to open serial port {self._port} @ {self._baudrate}: {e}")
            return

        self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()


    # Sends data through the serial connection if it is open.
    def write(self, data: bytes) -> None:
        if not self._serial_connection or not self._serial_connection.is_open:
            raise RuntimeError("Serial port is not open")

        self._serial_connection.write(data)


    # Stops the reading loop and cleans up resources.
    def stop(self) -> None:
        self._running = False
        if self._thread: self._thread.join(timeout=2.0)

        self._cleanup()

