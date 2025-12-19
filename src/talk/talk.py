
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

    def __init__(self):
        self.signals = TalkSignals()

        self._port: str = ""
        self._baudrate: int = 115200  # default rate

        self._serial_connection: Optional[serial.Serial] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False


    #- Getter/Setter -------------------------------------------------------------------------------

    @property
    def port(self) -> str: return self._port

    @port.setter
    def port(self, port: str) -> None:
        self._cleanup() # safely close the existing connection

        if port in all_ports():
            self._port = port
            self._restart_connection()  # restart the connection
            return

        alert(f"Invalid port selected: {port}")

    @property
    def baudrate(self) -> int: return self._baudrate

    @baudrate.setter
    def baudrate(self, rate: str) -> None:
        self._cleanup()

        if rate in BAUDRATES:
            self._baudrate = int(rate)
            self._restart_connection() # restart the connection
            return

        alert(f"Invalid baudrate selected: {rate}")


    #- Private Methods -----------------------------------------------------------------------------

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



    def _cleanup(self):
        if self._serial_connection:
            try: 
                if self._serial_connection.is_open: self._serial_connection.close()

            except Exception: pass

            self._serial_connection = None


    def _restart_connection(self):
        # stop read loop and wait
        self._running = False
        if self._thread: self._thread.join(timeout=1.0)

        # start the system again
        self.start()


    #- Public Methods ------------------------------------------------------------------------------

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


    def write(self, data: bytes) -> None:
        if not self._serial_connection or not self._serial_connection.is_open:
            raise RuntimeError("Serial port is not open")

        self._serial_connection.write(data)


    def stop(self) -> None:
        self._running = False
        if self._thread: self._thread.join(timeout=2.0)

        self._cleanup()


#===================================================================================================
#===================================================================================================
#===================================================================================================


if __name__ == "__main__":
    import time
    def handle_single(single_byte: bytes): print(single_byte, end="")
    def handle_line(byte_array: bytes): alert(byte_array)

    reader = Talk(handle_line, handle_single)
    try:
        reader.start()
        #reader.port = "/dev/cu.notvalid"
        #time.sleep(2)

        #reader.port = "/dev/cu.againnotvalid"
        #time.sleep(2)

        reader.port = "/dev/cu.usbmodem11201" # valid
        #time.sleep(5)

        #reader.port = "/dev/cu.usbem11201"
        while True: time.sleep(10)

    except KeyboardInterrupt:
        print("Stopping...")

    finally:
        reader.stop()
