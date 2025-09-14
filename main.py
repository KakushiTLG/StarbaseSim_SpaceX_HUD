import socket
import json
import threading
import time
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from typing import Dict, List, Optional
from enum import IntEnum, auto
import math
import sys
import os
from overlay_app import TelemetryOverlay
from PyQt5.QtWidgets import QApplication
import threading


class GameCommand(IntEnum):
    NONE = 0
    SendDataTick = auto()
    SetWhoSendsData = auto()
    SetRocketSetting = auto()
    SpawnAtLocation = auto()
    Engines = auto()
    Raptor = auto()
    Throttle = auto()
    RCS = auto()
    Flaps = auto()
    FoldFlaps = auto()
    GridFins = auto()
    Gimbals = auto()
    SetRCSManual = auto()
    SetDragManual = auto()
    SetGimbalManual = auto()
    Propellant = auto()
    CryotankPressure = auto()
    HotStage = auto()
    DetachHSR = auto()
    FTS = auto()
    OuterGimbalEngines = auto()
    BoosterClamps = auto()
    ControllerAltitude = auto()
    ControllerEastNorth = auto()
    ControllerAttitude = auto()
    AttitudeTarget = auto()
    ChillValve = auto()
    DumpFuel = auto()
    PopEngine = auto()
    BigFlame = auto()
    Chopsticks = auto()
    PadADeluge = auto()
    PadASQDQuickRetract = auto()
    PadAOLMQuickRetract = auto()
    PadABQDQuickRetract = auto()
    MasseyDeluge = auto()

class RocketDataPacket:
    def __init__(self, objectname: str, location: List[float], rotation: List[float], 
                 velocity: List[float], fuelMass: float, oxidizerMass: float, 
                 enginesThatAreRunningBitmask: int):
        self.objectname = objectname
        self.location = location  # [X, Y, Z]
        self.rotation = rotation  # [x, y, z, w]
        self.velocity = velocity  # [X, Y, Z]
        self.fuelMass = fuelMass
        self.oxidizerMass = oxidizerMass
        self.enginesThatAreRunningBitmask = enginesThatAreRunningBitmask
        
    def to_dict(self):
        return {
            'objectname': self.objectname,
            'location': self.location,
            'rotation': self.rotation,
            'velocity': self.velocity,
            'speed': math.sqrt(sum(v*v for v in self.velocity)),
            'fuelMass': self.fuelMass,
            'oxidizerMass': self.oxidizerMass,
            'fuelMassTons': self.fuelMass / 1000,
            'oxidizerMassTons': self.oxidizerMass / 1000,
            'totalPropellant': self.fuelMass + self.oxidizerMass,
            'totalPropellantTons': (self.fuelMass + self.oxidizerMass) / 1000,
            'enginesThatAreRunningBitmask': self.enginesThatAreRunningBitmask,
            'runningEngines': self.get_running_engines(),
            'timestamp': time.time()
        }
    
    def get_running_engines(self) -> List[int]:
        running = []
        for i in range(33):
            if self.enginesThatAreRunningBitmask & (1 << i):
                running.append(i + 1)
        return running

class StarbaseSimConnector:
    def __init__(self):
        self.client = None
        self.buffer = ""
        self.connected = False
        self.running = False
        self.latest_data: Dict[str, RocketDataPacket] = {}
        self.data_lock = threading.Lock()
        self.host = "localhost"
        self.port = 12345
        self.game_send_tick = 0.1
        self.reconnect_interval = 2.0
        
    def connect_to_server(self) -> bool:
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.host, self.port))
            self.client.settimeout(0.1)
            
            command = {
                "command": int(GameCommand.SendDataTick),
                "value": self.game_send_tick
            }
            self.client.send((json.dumps(command) + "\n").encode())
            
            self.connected = True
            print(f"Connected to StarbaseSim on {self.host}:{self.port}")
            print(f"Refresh rate: {self.game_send_tick} sec")
            return True
            
        except Exception as e:
            print(f"Connection error: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        if self.client:
            self.client.close()
            self.client = None
        self.connected = False
    
    def receive_data(self) -> List[RocketDataPacket]:
        rocket_data = []
        try:
            data = self.client.recv(4096).decode('utf-8')
            
            if not data:
                raise ConnectionResetError("Connection reset")
            
            self.buffer += data
            
            while '\n' in self.buffer:
                message, self.buffer = self.buffer.split('\n', 1)
                if message and message != "Client still there?":
                    try:
                        json_data = json.loads(message)
                        
                        # Извлечение данных телеметрии
                        objectname = json_data.get('objectname', '')
                        location = json_data.get('location', [])
                        rotation = json_data.get('rotation', [])
                        velocity = json_data.get('velocity', [])
                        fuelMass = json_data.get('fuelMass', 0)
                        oxidizerMass = json_data.get('oxidizerMass', 0)
                        enginesBitmask = json_data.get('enginesThatAreRunningBitmask', 0)
                        
                        # Валидация данных
                        if (isinstance(objectname, str) and 
                            isinstance(location, list) and len(location) == 3 and
                            isinstance(rotation, list) and len(rotation) == 4):
                            
                            packet = RocketDataPacket(
                                objectname, location, rotation, velocity,
                                fuelMass, oxidizerMass, enginesBitmask
                            )
                            rocket_data.append(packet)
                            
                    except json.JSONDecodeError as e:
                        print(f"Error JSON parse: {e}, Message: {message}")
                        
        except socket.timeout:
            pass
        except (ConnectionResetError, ConnectionAbortedError) as e:
            raise
        except Exception as e:
            print(f"Unexpected error in receive_data: {e}")
            
        return rocket_data
    
    def send_command(self, command_dict: dict):
        """One day I will touch it"""
        if self.client and self.connected:
            try:
                self.client.send((json.dumps(command_dict) + "\n").encode())
                return True
            except Exception as e:
                print(f"Error while sending command: {e}")
                return False
        return False
    
    def set_data_source(self, rocket_id: str):
        command = {
            "command": int(GameCommand.SetWhoSendsData),
            "target": rocket_id
        }
        return self.send_command(command)
    
    def start_data_thread(self):
        self.running = True
        thread = threading.Thread(target=self._data_loop, daemon=True)
        thread.start()
        return thread
    
    def stop_data_thread(self):
        self.running = False
    
    def _data_loop(self):
        while self.running:
            try:
                if not self.connected:
                    if self.connect_to_server():
                        self.buffer = ""
                    else:
                        time.sleep(self.reconnect_interval)
                        continue
                
                # Get data
                rocket_data = self.receive_data()
                
                # Updating data
                with self.data_lock:
                    for packet in rocket_data:
                        self.latest_data[packet.objectname] = packet
                
                time.sleep(0.01)
                
            except Exception as e:
                print(f"Error in _data_loop: {e}")
                self.disconnect()
                time.sleep(self.reconnect_interval)
    
    def get_latest_data(self) -> Dict[str, dict]:
        with self.data_lock:
            return {name: packet.to_dict() for name, packet in self.latest_data.items()}

connector = StarbaseSimConnector()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'starbasesim'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('telemetry_broadcast.html')

@app.route('/api/rockets')
def get_rockets():
    data = connector.get_latest_data()
    boosters = [name for name in data.keys() if name.startswith('B')]
    ships = [name for name in data.keys() if name.startswith('S')]
    return jsonify({
        'boosters': boosters,
        'ships': ships
    })

@app.route('/api/telemetry')
def get_telemetry():
    return jsonify(connector.get_latest_data())

@socketio.on('connect')
def handle_connect():
    print('Client connected to WebSocket')
    emit('status', {'connected': connector.connected})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected from WebSocket')

@socketio.on('set_data_source')
def handle_set_data_source(data):
    """ToDo Maybe in the future?"""
    rocket_id = data.get('rocket_id')
    if rocket_id:
        success = connector.set_data_source(rocket_id)
        emit('command_result', {'success': success, 'command': 'set_data_source', 'rocket_id': rocket_id})

def emit_telemetry_updates():
    """Telemetry update via WebSocket"""
    while True:
        if connector.connected:
            data = connector.get_latest_data()
            socketio.emit('telemetry_update', data)
        time.sleep(0.1)

def start_overlay():
    try:
        if not QApplication.instance():
            qt_app = QApplication(sys.argv)
        else:
            qt_app = QApplication.instance()

        overlay = TelemetryOverlay()
        overlay.show()

        print("Overlay is up! Show/Hide by pressing `")
        return qt_app, overlay

    except Exception as e:
        print(f"Overlay unavailable: {e}")
        return None, None

def old_startup():
    connector.start_data_thread()
    telemetry_thread = threading.Thread(target=emit_telemetry_updates, daemon=True)
    telemetry_thread.start()

    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    finally:
        connector.stop_data_thread()
        connector.disconnect()


if __name__ == '__main__':
    overlay_enabled = False
    if '--overlay' in sys.argv:
        overlay_enabled = True
    elif '--no-overlay' in sys.argv:
        overlay_enabled = False
    else:
        try:
            choice = input("Lauch with overlay? (y/N): ").lower().strip()
            overlay_enabled = choice == 'y'
        except (KeyboardInterrupt, EOFError):
            print("\nStarting without overlay...")
            overlay_enabled = False

    qt_app, overlay = None, None
    if overlay_enabled:
        qt_app, overlay = start_overlay()

    connector.start_data_thread()

    telemetry_thread = threading.Thread(target=emit_telemetry_updates, daemon=True)
    telemetry_thread.start()

    try:
        print(f"Server is starting at http://127.0.0.1:5000")
        if overlay:
            print("Overlay is starting: ` to show/hide")

        if qt_app and overlay:
            flask_thread = threading.Thread(
                target=lambda: socketio.run(app, host='127.0.0.1', port=5000, debug=False, use_reloader=False),
                daemon=True
            )
            flask_thread.start()

            qt_app.exec_()
        else:
            socketio.run(app, host='127.0.0.1', port=5000, debug=True, use_reloader=False)

    except KeyboardInterrupt:
        print("\nShutdown...")
    finally:
        connector.stop_data_thread()
        connector.disconnect()
        if qt_app:
            qt_app.quit()