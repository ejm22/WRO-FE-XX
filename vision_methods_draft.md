# Vision Methods and Decision Making

This document explains how the computer vision pipeline drives steering decisions for the robot:
- Wall following (how far up the image it sees black on both sides)
- Obstacle handling
- Inner/outer crash detection
- Arbitration (how actions are chosen)

Relevant code:
- Camera and processing: [code/XX_2025_package/classes/camera_manager.py](code/XX_2025_package/classes/camera_manager.py)
- Vision algorithms: [code/XX_2025_package/classes/image_algoriths.py](code/XX_2025_package/classes/image_algoriths.py)
- Main loop and serial control: [code/XX_2025_package/main.py](code/XX_2025_package/main.py)
- Transform utilities: [code/XX_2025_package/utils/image_transform_utils.py](code/XX_2025_package/utils/image_transform_utils.py)

Key symbols:
- [`ImageAlgorithms.calculate_servo_angle_from_walls`](code/XX_2025_package/classes/image_algoriths.py)
- [`ImageAlgorithms.find_wall_to_follow`](code/XX_2025_package/classes/image_algoriths.py)
- [`ImageAlgorithms.find_black_from_bottom`](code/XX_2025_package/classes/image_algoriths.py)
- [`ImageAlgorithms.find_black_sides`](code/XX_2025_package/classes/image_algoriths.py)
- [`ImageAlgorithms.find_obstacle_angle_and_draw_lines`](code/XX_2025_package/classes/image_algoriths.py)
- [`ImageAlgorithms.calculate_servo_angle_from_obstacle`](code/XX_2025_package/classes/image_algoriths.py)
- [`ImageAlgorithms.check_inner_wall_crash`](code/XX_2025_package/classes/image_algoriths.py)
- [`ImageAlgorithms.check_outer_wall_crash`](code/XX_2025_package/classes/image_algoriths.py)
- [`ImageAlgorithms.choose_output_angle`](code/XX_2025_package/classes/image_algoriths.py)
- [`ImageTransformUtils`](code/XX_2025_package/utils/image_transform_utils.py)

## 1) Image pipeline (inputs used by algorithms)

The camera pipeline produces these images used by the algorithms:
- polygon_image: binary map of the drivable corridor (walls are black=0, free space is white=255)
- display_image: BGR frame used for debug overlays (text, lines, circles)
- obstacle_image / pink_obstacle_image: binary masks for color obstacles
- hsv_image: HSV frame for color analysis

See [`CameraManager`](code/XX_2025_package/classes/camera_manager.py) and [`ImageTransformUtils`](code/XX_2025_package/utils/image_transform_utils.py).

## 2) Wall following calculations

Goal: steer so that the nearest wall is observed at a desired “depth” (how far up the image) and “lateral” position (how far from the side). The core steps:

- Sample how far upward we see black from the bottom on a band of columns near the side we follow.
- Sample how far inward we see black from the side on a band of rows near the bottom.
- Average those samples into (avg_x, avg_y).
- Compare (avg_x + avg_y) against a challenge-dependent threshold.
- Use a PD-like control to compute the steering angle.

Entry-point: [`ImageAlgorithms.calculate_servo_angle_from_walls`](code/XX_2025_package/classes/image_algoriths.py)

```python
# PD steering based on wall position
avg_x, avg_y = self.find_wall_to_follow()
threshold, kp, kd = self.calculate_wall_threshold_kp_kd(...)  # challenge-aware gains/threshold

# Error term: how far current measurement is from target sum
p_adjust = avg_y + avg_x - threshold

# Derivative term: change in error
p_compare = p_adjust - self.old_p_adjust
d_adjust = p_compare * kd

# Direction sign comes from context (LEFT or RIGHT)
angle = STRAIGHT_ANGLE + direction.value * (int(p_adjust * kp) + d_adjust)
# Clamp to servo range [MIN_ANGLE, MAX_ANGLE]
```

Sampling functions:
- Bottom-up scan: [`ImageAlgorithms.find_black_from_bottom`](code/XX_2025_package/classes/image_algoriths.py)
- Side-in scan: [`ImageAlgorithms.find_black_sides`](code/XX_2025_package/classes/image_algoriths.py)

Example implementations (simplified):

```python
def find_wall_to_follow(self, inverted=False):
    direction = self.context_manager.get_direction()

    # Choose columns near the followed wall, and rows near the bottom
    if direction == Direction.LEFT:
        cols = range(0, NBR_COLS)
    else:
        cols = range(ImageTransformUtils.PIC_WIDTH - NBR_COLS, ImageTransformUtils.PIC_WIDTH)

    rows = range(ImageTransformUtils.PIC_HEIGHT - 3*NBR_COLS,
                 ImageTransformUtils.PIC_HEIGHT - 2*NBR_COLS)

    y_vals = ImageAlgorithms.find_black_from_bottom(self.camera_manager.polygon_image, cols)
    x_vals = ImageAlgorithms.find_black_sides(self.camera_manager.polygon_image, direction, rows)

    avg_y = np.mean(y_vals)  # how far up (depth) we see wall
    avg_x = np.mean(x_vals)  # how far inward from side

    # Draw current measurement vs. target for debugging
    ImageDrawingUtils.draw_circle(self.camera_manager.display_image, (int(avg_x), int(avg_y)), 7, (0, 255, 255))
    return avg_x, avg_y
```

```python
@staticmethod
def find_black_from_bottom(img, col_range):
    y_vals = []
    H = ImageTransformUtils.PIC_HEIGHT
    for x in col_range:
        hit = 0
        for y in range(H - 1, 0, -1):
            if img[y, x] == 0:  # black pixel = wall
                hit = y
                break
        y_vals.append(hit)
    return y_vals
```

```python
@staticmethod
def find_black_sides(img, direction, row_range):
    x_vals = []
    W = ImageTransformUtils.PIC_WIDTH
    step = -1 if direction == Direction.LEFT else 1
    start = W // 2
    stop = 0 if direction == Direction.LEFT else W - 1

    for y in row_range:
        hit = stop
        for x in range(start, stop, step):
            if img[y, x] == 0:  # black pixel = wall
                hit = x
                break
        x_vals.append(hit)
    return x_vals
```

Challenge-aware threshold and gains come from a config and lap-based offsets:
- [`CHALLENGE_CONFIG`](code/XX_2025_package/classes/image_algoriths.py)
- [`ImageAlgorithms.calculate_wall_threshold_kp_kd`](code/XX_2025_package/classes/image_algoriths.py)

This lets the same logic adapt between challenges and laps.


## 3) Obstacle handling calculations

When an obstacle is present (color block), the robot computes an avoidance “object line” then maps it to a servo angle.

Entry-point: [`ImageAlgorithms.find_obstacle_angle_and_draw_lines`](code/XX_2025_package/classes/image_algoriths.py)

Steps:
1) Safety first: check outer crash risk via [`check_outer_wall_crash`](code/XX_2025_package/classes/image_algoriths.py). If true, return an extreme avoidance command.
2) Detect the largest obstacle rectangle in obstacle_image or pink_obstacle_image (color masks).
3) Determine color (green/red/pink) from HSV in the rectangle.
4) Draw a guidance line from the obstacle toward a safe target x on the floor (left or right-side threshold).
5) Compute the geometric angle of that line relative to the bottom-center.
6) Convert that to a servo angle using [`calculate_servo_angle_from_obstacle`](code/XX_2025_package/classes/image_algoriths.py), with color-specific offsets.

Example logic (abridged):

```python
def find_obstacle_angle_and_draw_lines(self):
    # High-priority safety
    if self.check_outer_wall_crash():
        # Force an emergency turn away from the outer wall
        return (1000 if self.context_manager.get_direction() == Direction.RIGHT else -1000), None, None, None

    rect = self._find_largest_obstacle_rect()  # find in obstacle_image
    if rect is None:
        return None, None, None, None

    x_center, y_center = rect[0]
    is_green = ImageColorUtils.is_rect_green(self.camera_manager.hsv_image, rect)

    # Aim line toward a side threshold depending on color
    left_x = 40
    right_x = ImageTransformUtils.PIC_WIDTH - 40
    target_x = right_x if is_green else left_x  # example: green -> pass on right

    ImageDrawingUtils.draw_line(self.camera_manager.display_image,
                                (x_center, y_center), (target_x, ImageTransformUtils.PIC_HEIGHT),
                                color=(0, 255, 0) if is_green else (0, 0, 255))

    # Compute object-line angle (deg) relative to bottom
    dy = y_center - ImageTransformUtils.PIC_HEIGHT
    dx = x_center - target_x
    object_angle = 90 + math.degrees(math.atan2(dy, dx))

    return object_angle, is_green, x_center, y_center
```

Mapping to servo angle: [`ImageAlgorithms.calculate_servo_angle_from_obstacle`](code/XX_2025_package/classes/image_algoriths.py)

```python
@staticmethod
def calculate_servo_angle_from_obstacle(object_angle, is_green, pink=0):
    if object_angle is None:
        return None

    kp = 1.5
    offset = OBJECT_LINE_ANGLE_THRESHOLD
    # Example policy: green -> pass on right, red -> pass on left
    error = (object_angle + offset) if is_green else (object_angle - offset)
    servo_angle = STRAIGHT_ANGLE - (error * kp)

    # Clamp
    servo_angle = max(MIN_ANGLE, min(MAX_ANGLE, int(servo_angle)))
    return servo_angle
```

Inner-wall safety with obstacles:
- If an obstacle is short (small height) and the inner wall is very close at several detection points, prefer wall-following instead of cutting too tight around the obstacle.

[`ImageAlgorithms.check_inner_wall_crash`](code/XX_2025_package/classes/image_algoriths.py)

```python
def check_inner_wall_crash(self, object_height):
    if object_height is None:
        return True  # no object; do not force obstacle behavior

    # Pick detection points near the inner side depending on direction
    pts = self._inner_detection_points_for_direction(...)
    for (y, x) in pts:
        ImageDrawingUtils.draw_circle(self.camera_manager.display_image, (x, y), 3, (255, 0, 0))
        if (self.camera_manager.polygon_image[y, x] == 0 and
            object_height < ImageTransformUtils.PIC_HEIGHT - 170):
            return True
    return False
```

## 4) Crash detection

Two safety checks protect the robot:

- Outer wall crash: checks a point centered ahead of the robot; if black, the corridor closes in front, so we must turn away quickly.

[`ImageAlgorithms.check_outer_wall_crash`](code/XX_2025_package/classes/image_algoriths.py)

```python
def check_outer_wall_crash(self):
    cx = ImageTransformUtils.PIC_WIDTH // 2
    cy = ImageTransformUtils.PIC_HEIGHT - 160
    ImageDrawingUtils.draw_circle(self.camera_manager.display_image, (cx, cy), 3, (255, 0, 0))
    return self.camera_manager.polygon_image[cy, cx] == 0
```

- Inner wall crash: described above (multiple probing points along the inner side while dealing with obstacles).

These checks take priority in arbitration.

## 5) Arbitration: choosing the action

The main loop typically computes both:
- angle_walls from wall following
- angle_obstacles from obstacle handling (or None when no obstacle)

Then a simple policy selects the steering to send:

[`ImageAlgorithms.choose_output_angle`](code/XX_2025_package/classes/image_algoriths.py)

```python
@staticmethod
def choose_output_angle(angle_walls, angle_obstacles):
    if angle_obstacles is None:
        return angle_walls
    return angle_obstacles
```

Priority in practice:
1) Outer wall crash → override with extreme turn away (safety)
2) Obstacle present → obstacle angle
3) Inner wall too close while handling obstacle → ignore obstacle, use wall following
4) Otherwise → wall following

End-to-end usage in the main loop (see [code/XX_2025_package/main.py](code/XX_2025_package/main.py)):

```python
# Compute steering from walls
angle_walls, _ = image_algorithms.calculate_servo_angle_from_walls()

# Compute steering from obstacles
obj_angle, is_green, x0, y0 = image_algorithms.find_obstacle_angle_and_draw_lines()
angle_obstacles = image_algorithms.calculate_servo_angle_from_obstacle(obj_angle, is_green)

# Decide final command
servo_angle = image_algorithms.choose_output_angle(angle_walls, angle_obstacles)

# Send to Arduino
command = f"m{servo_angle},{speed}.".encode()
arduino.write(command)
arduino.flush()
```

## 6) Tuning notes

- Threshold/kp/kd are challenge-aware via [`CHALLENGE_CONFIG`](code/XX_2025_package/classes/image_algoriths.py) and lap-based offsets.
- The balance between bottom-up (avg_y) and side-in (avg_x) is controlled by the threshold split in [`calculate_servo_angle_from_walls`](code/XX_2025_package/classes/image_algoriths.py), which accounts for direction.