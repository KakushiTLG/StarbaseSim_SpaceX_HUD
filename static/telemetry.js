// WebSocket connection
        const socket = io();

        // Mission timer
        const missionStartTime = Date.now();

        function updateMissionTimer() {
            const missionDuration = 60; // секунды до старта
            const elapsed = Math.floor((Date.now() - missionStartTime) / 1000);
            const remaining = missionDuration - elapsed;

            let sign = '';
            let displayTime = remaining;

            if (remaining < 0) {
                displayTime = -remaining; // уже пошли положительные T+
                sign = '+';
            } else {
                sign = '-';
            }

            const hours = Math.floor(displayTime / 3600).toString().padStart(2, '0');
            const minutes = Math.floor((displayTime % 3600) / 60).toString().padStart(2, '0');
            const seconds = (displayTime % 60).toString().padStart(2, '0');

            document.getElementById('missionTimer').textContent = `T${sign}${hours}:${minutes}:${seconds}`;
        }

        // Connection status
        function updateConnectionStatus(connected) {
            const status = document.getElementById('connectionStatus');
            if (connected) {
                status.className = 'connection-status connected';
                status.textContent = 'CONNECTED TO WEBSOCKET';
            } else {
                status.className = 'connection-status disconnected';
                status.textContent = 'DISCONNECTED FROM WEBSOCKET';
            }
        }

        // Quaternion to Euler angles conversion
        function quaternionToEuler(x, y, z, w) {
            // Roll (x-axis rotation)
            const sinr_cosp = 2 * (w * x + y * z);
            const cosr_cosp = 1 - 2 * (x * x + y * y);
            const roll = Math.atan2(sinr_cosp, cosr_cosp);

            // Pitch (y-axis rotation)
            const sinp = 2 * (w * y - z * x);
            const pitch = Math.abs(sinp) >= 1 ? Math.sign(sinp) * Math.PI / 2 : Math.asin(sinp);

            // Yaw (z-axis rotation)
            const siny_cosp = 2 * (w * z + x * y);
            const cosy_cosp = 1 - 2 * (y * y + z * z);
            const yaw = Math.atan2(siny_cosp, cosy_cosp);

            return {
                roll: roll * 180 / Math.PI,
                pitch: pitch * 180 / Math.PI,
                yaw: yaw * 180 / Math.PI
            };
        }

        // Update attitude displays
        function updateAttitude(vehicleData) {
            if (vehicleData.rotation && vehicleData.rotation.length === 4) {
                const [x, y, z, w] = vehicleData.rotation;
                const euler = quaternionToEuler(x, y, z, w);
                
                const vehicleType = vehicleData.objectname.charAt(0); // 'B' or 'S'
                
                console.log(`${vehicleData.objectname} attitude: pitch=${euler.pitch.toFixed(2)}°, roll=${euler.roll.toFixed(2)}°, yaw=${euler.yaw.toFixed(2)}°`);
                
                if (vehicleType === 'B') {
                    // Update booster attitude - use inverted roll (X-axis rotation)
                    const boosterModel = document.getElementById('boosterModel');
                    
                    if (boosterModel) {
                        boosterModel.style.transform = `rotate(${-euler.roll}deg)`;
                        console.log(`Booster model rotated to ${-euler.roll.toFixed(2)}° (inverted X-axis)`);
                    } else {
                        console.log('Booster model element not found!');
                    }
                } else if (vehicleType === 'S') {
                    // Update ship attitude - use inverted roll (X-axis rotation)
                    const shipModel = document.getElementById('shipModel');
                    
                    if (shipModel) {
                        shipModel.style.transform = `rotate(${-euler.roll}deg)`;
                        console.log(`Ship model rotated to ${-euler.roll.toFixed(2)}° (inverted X-axis)`);
                    } else {
                        console.log('Ship model element not found!');
                    }
                }
            }
        }

        // Engine elements
        const boosterEngines = document.getElementById('boosterEngines');
        const shipEngines = document.getElementById('shipEngines');

        // Safe bit checking function for engines 1-33 using BigInt for large bits
        function isEngineBitSet(bitmask, engineNumber) {
            const bitPosition = engineNumber - 1;
            const bigMask = BigInt(bitmask);
            const bigBit = BigInt(1) << BigInt(bitPosition);
            return (bigMask & bigBit) !== BigInt(0);
        }

        // Initialize booster engines (33 engines)
        function initializeBoosterEngines() {
            const container = boosterEngines;
            container.innerHTML = '';

            const engineConfigs = [
                // Center ring - 3 engines
                ...Array.from({length: 3}, (_, i) => ({
                    angle: (i * 120) - 90,
                    radius: 15, // ближе друг к другу
                    number: i + 1,
                    size: 20
                })),
                // Inner ring - 10 engines
                ...Array.from({length: 10}, (_, i) => ({
                    angle: (i * 36) - 90,
                    radius: 50, // плотнее
                    number: i + 4,
                    size: 20
                })),
                // Outer ring - 20 engines
                ...Array.from({length: 20}, (_, i) => ({
                    angle: (i * 18) - 90,
                    radius: 80, // плотнее
                    number: i + 14,
                    size: 20
                }))
            ];

            engineConfigs.forEach(config => {
                const engine = document.createElement('div');
                engine.className = 'engine stopped';
                engine.dataset.engine = config.number;
                engine.style.width = `${config.size}px`;
                engine.style.height = `${config.size}px`;

                const x = Math.cos(config.angle * Math.PI / 180) * config.radius;
                const y = Math.sin(config.angle * Math.PI / 180) * config.radius;


                engine.style.left = `${140 + x - config.size/2}px`;
                engine.style.top  = `${140 + y - config.size/2}px`;

                container.appendChild(engine);
            });
        }

        // Initialize ship engines (6 engines) - with different sizes
        function initializeShipEngines() {
            const container = shipEngines;
            container.innerHTML = '';

            const engineConfigs = [
                // Центр – 3 маленьких двигателя
                ...Array.from({length: 3}, (_, i) => ({
                    angle: (i * 120) - 90, // оставляем как есть
                    radius: 18,            // компактные
                    number: i + 1,
                    size: 30
                })),
                // Внешнее кольцо – 3 больших двигателя
                ...Array.from({length: 3}, (_, i) => ({
                    angle: (i * 120) - 30, // сохраняем свое положение
                    radius: 65,            // уменьшили радиус, ближе к центру
                    number: i + 4,
                    size: 64
                }))
            ];



            engineConfigs.forEach(config => {
                const engine = document.createElement('div');
                engine.className = 'ship-engine stopped';
                engine.dataset.engine = config.number;
                engine.style.width = `${config.size}px`;
                engine.style.height = `${config.size}px`;

                const x = Math.cos(config.angle * Math.PI / 180) * config.radius;
                const y = Math.sin(config.angle * Math.PI / 180) * config.radius;

                engine.style.left = `${150 + x - config.size + (config.number > 3 ? 16 : 0)}px`;
                engine.style.top  = `${150 + y - config.size + (config.number > 3 ? 15 : 0)}px`;


                container.appendChild(engine);
            });
        }

        // Update booster engines
        function updateBoosterEngines(bitmask) {
            let runningCount = 0;
            const engines = boosterEngines.querySelectorAll('.engine');

            engines.forEach(engine => {
                const engineNum = parseInt(engine.dataset.engine);
                const isRunning = isEngineBitSet(bitmask, engineNum);

                if (isRunning) {
                    engine.classList.add('running');
                    engine.classList.remove('stopped');
                    runningCount++;
                } else {
                    engine.classList.add('stopped');
                    engine.classList.remove('running');
                }
            });
        }

        // Update ship engines
        function updateShipEngines(bitmask) {
            let runningCount = 0;
            const engines = shipEngines.querySelectorAll('.ship-engine');

            engines.forEach(engine => {
                const engineNum = parseInt(engine.dataset.engine);
                const isRunning = isEngineBitSet(bitmask, engineNum);

                if (isRunning) {
                    engine.classList.add('running');
                    engine.classList.remove('stopped');
                    runningCount++;
                } else {
                    engine.classList.add('stopped');
                    engine.classList.remove('running');
                }
            });
        }

        // Update telemetry data
        function updateTelemetry(data) {
            // Find booster and ship data
            const boosterData = Object.values(data).find(d => d.objectname && d.objectname.startsWith('B'));
            const shipData = Object.values(data).find(d => d.objectname && d.objectname.startsWith('S'));

            // Update booster
            if (boosterData) {
                const speedKmh = Math.round(boosterData.speed * 3.6);
                const altitudeKm = Math.floor(boosterData.location[2] / 1000);

                document.getElementById('boosterSpeed').textContent = speedKmh;
                document.getElementById('boosterAltitude').textContent = altitudeKm;

                // Fuel bars (maximum values for booster)
                const maxLox = 2660000; // kg
                const maxCh4 = 740000; // kg
                const loxPercent = Math.min((boosterData.oxidizerMass / maxLox) * 100, 100);
                const ch4Percent = Math.min((boosterData.fuelMass / maxCh4) * 100, 100);

                document.getElementById('boosterLoxBar').style.width = `${loxPercent}%`;
                document.getElementById('boosterCh4Bar').style.width = `${ch4Percent}%`;

                updateBoosterEngines(boosterData.enginesThatAreRunningBitmask);
                updateAttitude(boosterData); // Add attitude update
            }

            // Update ship
            if (shipData) {
                const speedKmh = Math.round(shipData.speed * 3.6);
                const altitudeKm = Math.floor(shipData.location[2] / 1000);

                document.getElementById('shipSpeed').textContent = speedKmh;
                updateAttitude(shipData); // Add attitude update
                document.getElementById('shipAltitude').textContent = altitudeKm;

                // Fuel bars (maximum values for ship)
                const maxLox = 1174000; // kg
                const maxCh4 = 327000; // kg
                const loxPercent = Math.min((shipData.oxidizerMass / maxLox) * 100, 100);
                const ch4Percent = Math.min((shipData.fuelMass / maxCh4) * 100, 100);

                document.getElementById('shipLoxBar').style.width = `${loxPercent}%`;
                document.getElementById('shipCh4Bar').style.width = `${ch4Percent}%`;

                updateShipEngines(shipData.enginesThatAreRunningBitmask);
            }
        }

        // WebSocket events
        socket.on('connect', function() {
            updateConnectionStatus(true);
        });

        socket.on('disconnect', function() {
            updateConnectionStatus(false);
        });

        socket.on('telemetry_update', function(data) {
            updateTelemetry(data);
        });

        // Initialize
        function initialize() {
            initializeBoosterEngines();
            initializeShipEngines();

            // Start mission timer
            setInterval(updateMissionTimer, 1000);

            // Initial data load
            fetch('/api/telemetry')
                .then(response => response.json())
                .then(data => updateTelemetry(data))
                .catch(error => console.error('Error loading telemetry:', error));
        }

        // Start when page loads
        document.addEventListener('DOMContentLoaded', initialize);