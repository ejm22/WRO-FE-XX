# Communication Protocol

## Pi-Arduino Communication

The Raspberry Pi and Arduino communicate via USB serial connection. The Pi sends formatted commands to control the robot's movement, while the Arduino sends status updates back to the Pi.

### Communication Setup
- **Connection**: USB serial between Raspberry Pi and Arduino
- **Baud Rate**: 115200
- **Protocol**: Text-based commands with specific delimiters

### Command Format

#### Pi → Arduino (Movement Commands)
Commands for movement follow the format: `m{angle},{speed}.`
If there is a target distance: `t{angle},{speed},{target}`

| Command Format | Description | Example |
|---------------|-------------|---------|
| `m{angle},{speed}.` | Move command with steering angle and motor speed | `m90,5500.` |
| `t{angle},{speed},{target}.` | Move command with angle, motor speed and target | `t90,5500,3000` |
| `10000000!` | Set target command (10000000 means never stop moving) | `10000000!` |

**Parameters:**
- `angle`: Servo angle for steering (typically 30-150, where 90 is straight)
- `speed`: Motor speed value (0-6000+ range)
- `target`: Motor rotation target in steps (0.1559 mm per 1 step) 
- `.` : Move command terminator
- `!` : New target command terminator

#### Arduino → Pi (Status Updates)
| Message | Description |
|---------|-------------|
| `1` | Challenge 1 button pressed |
| `2` | Challenge 2 button pressed |
| `0` | Stop button pressed |
| `F` | Target reached after target movement command |

### Code Implementation

**Arduino Side** (`main.cpp`):
- Sends button press notifications to Pi
- Listens for serial commands
- Parses movement commands to extract angle and speed
- Controls servo and stepper motor accordingly
- Sends stop movement command after target reached

**Pi Side** (`main.py`):
- Listens for button press status from Arduino
- Handles challenge selection and stop commands
- Sends movement commands based on computer vision analysis