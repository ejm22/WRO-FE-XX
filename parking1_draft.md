# Challenge 1 – Parking Logic

This explains how parking works end-to-end in Challenge 1:
- Determine FRONT vs BACK start using back-wall height at image center.
- Drive laps; on the last quarter, slow down.
- Detect the “last corner” to localize position.
- Execute a precise, step-targeted move to the correct stop zone.


## 1) Classify the start zone (FRONT vs BACK)

At startup, the robot scans the center columns of the polygon map and measures the first black (wall) row from the bottom. That “height” decides the start zone.

- Lower “first black” (closer wall) → BACK
- Higher “first black” (farther wall) → FRONT

Stored in context:
- [`ImageAlgorithms.get_starting_position`](code/XX_2025_package/classes/image_algoriths.py) calls [`ImageAlgorithms.get_back_wall_distance`](code/XX_2025_package/classes/image_algoriths.py),
- then [`ContextManager.set_start_position`](code/XX_2025_package/classes/context_manager.py).

Example (simplified):

```python
# Decide FRONT/BACK using center scan of polygon_image
start_position = image_algorithms.get_starting_position()  # uses center pixels bottom-up
context_manager.set_start_position(start_position)
```

Why this works: the start areas differ in how “close” the back wall appears in the image center.

## 2) Drive laps and slow down on the final approach

During navigation:
- [`LapTracker.process_image`](code/XX_2025_package/classes/lap_tracker.py) increments quarters using the center window of blue/orange.
- On the last quarter or once the lap goal is met, reduce speed for stability before parking:
  - [`ContextManager.is_last_quarter`](code/XX_2025_package/classes/context_manager.py)
  - [`ContextManager.has_completed_laps`](code/XX_2025_package/classes/context_manager.py)

```python
# Regular wall-following
angle, is_corner = image_algorithms.calculate_servo_angle_from_walls()
arduino.write(f"m{angle},{speed}.".encode())

# Slow down at final approach
if context_manager.is_last_quarter() or context_manager.has_completed_laps():
    speed = 4000
```

## 3) Detect the “last corner” to localize position

Corner detection is derived from wall-following PD dynamics in
[`ImageAlgorithms.calculate_servo_angle_from_walls`](code/XX_2025_package/classes/image_algoriths.py):
- When the error delta `p_compare` is sharply negative (e.g., below −PIC_HEIGHT/2.5), `is_corner = True`.
- A 1s debounce is used to avoid early triggers.

Once the corner triggers, estimate if the last corner is visually Close or Far using the outer wall:
- [`ImageAlgorithms.check_last_corner_position`](code/XX_2025_package/classes/image_algoriths.py) calls `find_wall_to_follow(inverted=True)`,
- compares the outer wall’s average y to `PIC_HEIGHT/2`, returning 'C' or 'F'.

```python
# Debounced corner event
if (time.time() - start_time >= 1) and is_corner and not check_corner_flag:
    check_corner_flag = True
    final_corner_position = image_algorithms.check_last_corner_position()  # 'C' or 'F'
```

## 4) Compute the final target distance

Pick a base distance in steps from the corner classification:
- 'C' (close) → 6400 steps
- 'F' (far)  → 3900 steps

Then add an offset if the run started in the FRONT zone:
- [`MOVE_TO_FRONT_ZONE`](code/XX_2025_package/main.py) = 3200

```python
extra_move = MOVE_TO_FRONT_ZONE if context_manager.get_start_position() == StartPosition.FRONT else 0
steps = (6400 if final_corner_position == 'C' else 3900) + extra_move
```

## 5) Execute the precise move and wait for completion

Send the target steps command and wait for the Arduino to acknowledge completion with “F”.
The Arduino emits “F” in [code/arduino/src/main.cpp](code/arduino/src/main.cpp) when a target motion completes.

```python
# Commit the final straight move
arduino.write(f"{steps}!".encode())
speed = 1500  # slow final approach

# Block until firmware finishes (prints 'F')
while arduino.read().decode('utf-8') != 'F':
    time.sleep(0.005)
```

## 6) End-to-end flow (reference)

```python
# 1) Determine direction and start zone
image_algorithms.get_direction_from_lines()
start_position = image_algorithms.get_starting_position()
context_manager.set_start_position(start_position)

# 2) Drive laps with wall following
while True:
    camera_manager.capture_image()
    camera_manager.transform_image()
    lap_tracker.process_image(camera_manager.cnt_blueline, camera_manager.cnt_orangeline)

    angle, is_corner = image_algorithms.calculate_servo_angle_from_walls()
    arduino.write(f"m{angle},{speed}.".encode())

    # 3) Final approach slow-down and corner detection
    if context_manager.is_last_quarter() or context_manager.has_completed_laps():
        speed = 4000
        if start_time == 0:
            start_time = time.time()
        if (time.time() - start_time >= 1) and is_corner and not check_corner_flag:
            check_corner_flag = True
            final_corner_position = image_algorithms.check_last_corner_position()

            # 4) Compute and 5) Execute precise move
            extra_move = MOVE_TO_FRONT_ZONE if context_manager.get_start_position() == StartPosition.FRONT else 0
            steps = (6400 if final_corner_position == 'C' else 3900) + extra_move
            arduino.write(f"{steps}!".encode())

    # Exit after Arduino reports completion on the final move
    if arduino.in_waiting > 0 and context_manager.has_completed_laps():
        if arduino.read().decode('utf-8') == 'F':
            break
```

This yields a deterministic parking stop tailored by:
- Start zone (FRONT/BACK from back-wall height),
- Corner proximity (Close/Far from outer-wall height),
- A precise, step-based final move.