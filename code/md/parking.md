# Challenge 1 & 2 – Parking Logic

This explains how parking works end-to-end in both challenges:
- **Challenge 1**: Determine FRONT vs BACK start using back-wall height at image center, drive laps, detect the "last corner" to localize position, execute a precise step-targeted move.
- **Challenge 2**: Complete 3 laps with obstacle avoidance, approach pink parking markers, execute a complex parallel parking maneuver.

## Challenge 1 Parking

### 1) Classify the start zone (FRONT vs BACK)

At startup, the robot scans the center columns of the polygon map and measures the first black (wall) row from the bottom. That "height" decides the start zone.

- Lower "first black" (closer wall) → BACK
- Higher "first black" (farther wall) → FRONT

Stored in context:
- [`ImageAlgorithms.get_starting_position`](code/XX_2025_package/classes/image_algoriths.py) calls [`ImageAlgorithms.get_back_wall_distance`](code/XX_2025_package/classes/image_algoriths.py),
- then [`ContextManager.set_start_position`](code/XX_2025_package/classes/context_manager.py).

Why this works: the start areas differ in how "close" the back wall appears in the image center.

### 2) Drive laps and slow down on the final approach

During navigation:
- [`LapTracker.process_image`](code/XX_2025_package/classes/lap_tracker.py) increments quarters using the center window of blue/orange.
- On the last quarter or once the lap goal is met, reduce speed for stability before parking:
  - [`ContextManager.is_last_quarter`](code/XX_2025_package/classes/context_manager.py)
  - [`ContextManager.has_completed_laps`](code/XX_2025_package/classes/context_manager.py)

### 3) Detect the "last corner" to localize position

Corner detection is derived from wall-following PD dynamics in
[`ImageAlgorithms.calculate_servo_angle_from_walls`](code/XX_2025_package/classes/image_algoriths.py):
- When the error delta `p_compare` is sharply negative (e.g., below −PIC_HEIGHT/2.5), `is_corner = True`.
- A 1s debounce is used to avoid early triggers.

Once the corner triggers, estimate if the last corner is visually Close or Far using the outer wall:
- [`ImageAlgorithms.check_last_corner_position`](code/XX_2025_package/classes/image_algoriths.py) calls `find_wall_to_follow(inverted=True)`,
- compares the outer wall's average y to `PIC_HEIGHT/2`, returning 'C' or 'F'.

### 4) Compute the final target distance

Pick a base distance in steps from the corner classification:
- 'C' (close) → 6400 steps
- 'F' (far)  → 3900 steps

Then add an offset if the run started in the FRONT zone:
- [`MOVE_TO_FRONT_ZONE`](code/XX_2025_package/main.py) = 3200

### 5) Execute the precise move and wait for completion

Send the target steps command and wait for the Arduino to acknowledge completion with "F".
The Arduino emits "F" in [code/arduino/src/main.cpp](code/arduino/src/main.cpp) when a target motion completes.

## Challenge 2 Parking

### 1) Complete 3 laps with obstacle avoidance

Challenge 2 begins with normal lap completion using wall following and obstacle avoidance, as described in the main navigation logic. The robot tracks laps via [`LapTracker.process_image`](code/XX_2025_package/classes/lap_tracker.py) and switches to parking mode after completing the required laps.

### 2) Approach the pink parking markers

After lap completion, the robot enters parking approach mode:

**Pink marker detection**: The robot uses [`ImageAlgorithms.find_pink_obstacle_angle`](code/XX_2025_package/classes/image_algoriths.py) to detect pink parking markers and calculate approach angles, similar to green/red obstacle detection.

**Direction-specific detection zones**: Based on the driving direction, the robot looks for pink markers in specific areas:
- LEFT direction: looks for pink near the right side (x > PIC_WIDTH - 150)
- RIGHT direction: looks for pink near the left side (x < 150)

**Obstacle priority**: When both regular obstacles and pink markers are detected, the robot prioritizes the pink marker if it appears closer (higher y-coordinate) than the regular obstacle.

**Approach termination**: The approach phase ends when a pink marker is detected close to the robot (y > PIC_HEIGHT - 100) in the appropriate side zone.

### 3) Enter parking area with forward movement

Once the pink marker is detected in the correct position:
- Stop current movement with `m86,0.` (straight, zero speed)
- Execute a small forward movement with `2000!` steps to position for parking
- Switch the driving direction (LEFT ↔ RIGHT) to prepare for the parking maneuver

### 4) Execute parallel parking maneuver

The parking sequence uses a combination of wall following and specific geometric movements:

**Phase 1 - Wall following into position**:
- Use [`ImageAlgorithms.calculate_servo_angle_from_walls`](code/XX_2025_package/classes/image_algoriths.py) with challenge 3 parameters for tight maneuvering
- Monitor for parking completion conditions:
  - RIGHT direction: detect wall directly ahead (polygon_image[140, center] == 0) and top line angle
  - LEFT direction: detect orange line in the center window

**Phase 2 - Reverse positioning**:
- Move backward with `-10000000!` while monitoring for a wall at a specific backward detection point
- Stop when the detection pixel turns black (wall detected)

**Phase 3 - Final positioning sequence**:
- Move forward 1750 steps (adjusted by ±50 based on direction)
- Execute a series of precise target movements (`t` commands) to achieve proper parking alignment:
  - Angled reverse movement (1300-1400 steps depending on last obstacle color)
  - Straight reverse (650 steps)  
  - Angled reverse in opposite direction (1275 steps)
- Final stop with `m85,0.`

### 5) Direction and obstacle-dependent fine-tuning

The final positioning takes into account:
- **Direction**: LEFT vs RIGHT affects angle calculations and step counts
- **Last obstacle color**: If the last detected obstacle was red and direction is LEFT, use 1400 steps instead of 1300 steps for the angled reverse

The parking angles use the formula: `86 ± direction.value * 38` where direction.value is -1 for LEFT and +1 for RIGHT.

## End-to-end flow comparison

### Challenge 1 Flow:
1. Determine direction from line lengths and classify start zone
2. Drive laps with pure wall following
3. Detect final corner and compute precise parking distance
4. Execute single forward movement to parking position

### Challenge 2 Flow:
1. Complete 3 laps with obstacle avoidance  
2. Approach pink parking markers using enhanced obstacle detection
3. Enter parking area with small forward movement
4. Execute complex parallel parking with multiple phases:
   - Wall-following approach
   - Reverse positioning  
   - Multi-step precise alignment sequence

Key differences:
- **Challenge 1**: Simple forward parking with distance calculation
- **Challenge 2**: Complex parallel parking with multiple movement phases
- **Detection**: Challenge 1 uses corner detection; Challenge 2 uses pink marker detection
- **Positioning**: Challenge 1 is single-move; Challenge 2 requires precise multi-step maneuvering
