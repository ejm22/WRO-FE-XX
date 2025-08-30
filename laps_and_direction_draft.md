# Direction Determination (Challenge 1 and 2) and Lap Tracking

This section explains:
- How the robot picks its driving direction at the start of Challenge 1 and Challenge 2
- How laps are tracked using a simple, debounced state machine

## Challenge 1: Direction from Blue vs Orange Line Length

At the start of Challenge 1, the robot decides whether to follow the left or right wall by comparing the detected lengths of the blue and orange lines. The decision is made in [`ImageAlgorithms.get_direction_from_lines`](code/XX_2025_package/classes/image_algoriths.py):
- If the blue line is longer than the orange line → follow LEFT
- Otherwise → follow RIGHT

Internally it reads per-frame measurements prepared by the camera pipeline (for example: `camera_manager.length_blue` and `camera_manager.length_orange`) and sets the direction in context.

Example (simplified):

```python
# Decide direction using line lengths (Challenge 1)
def get_direction_from_lines(self):
    # length_blue / length_orange are computed in the camera pipeline
    direction = Direction.LEFT if self.camera_manager.length_blue > self.camera_manager.length_orange else Direction.RIGHT
    self.context_manager.set_direction(direction)
```

Where it’s called in the main flow:
- See Challenge 1 setup in [code/XX_2025_package/main.py](code/XX_2025_package/main.py).

## Challenge 2: Direction from Free-Space (Left vs Right Half)

In Challenge 2, the robot decides the initial direction by comparing how much free space (white pixels) exists on the left half vs the right half of the drivable mask (`polygon_image`). This logic is in [`ImageAlgorithms.get_direction_from_parking`](code/XX_2025_package/classes/image_algoriths.py):
- Count white pixels in left half and right half of the binary polygon image
- If left has more white → LEFT, else → RIGHT

Example (simplified):

```python
# Decide direction from how open each half is (Challenge 2)
def get_direction_from_parking(self, camera_object):
    left_white = np.sum(camera_object.polygon_image[:, :ImageTransformUtils.PIC_WIDTH // 2] == 255)
    right_white = np.sum(camera_object.polygon_image[:, ImageTransformUtils.PIC_WIDTH // 2:] == 255)
    direction = Direction.LEFT if left_white > right_white else Direction.RIGHT
    self.context_manager.set_direction(direction)
```

Where it’s called in the main flow:
- See Challenge 2 setup in [code/XX_2025_package/main.py](code/XX_2025_package/main.py).

## Lap Tracking: Windowed Color Detection + State Machine

Laps are tracked by watching a small window near the center-bottom of the frame and advancing a state machine when the expected color appears. The sequence depends on the driving direction:
- Direction LEFT: expect BLUE then ORANGE
- Direction RIGHT: expect ORANGE then BLUE
- After detecting the pair, wait (debounce) before looking for the next pair

Window used for detection in [`LapTracker.process_image`](code/XX_2025_package/classes/lap_tracker.py):
- Rows: PIC_HEIGHT − 130 to PIC_HEIGHT − 30
- Columns: ±20 pixels around the center x

```python
def process_image(self, blue_img, orange_img):
    if self.context_manager.get_direction() is not None:
        h0, h1 = ImageTransformUtils.PIC_HEIGHT - 130, ImageTransformUtils.PIC_HEIGHT - 30
        w0, w1 = ImageTransformUtils.PIC_WIDTH // 2 - 20, ImageTransformUtils.PIC_WIDTH // 2 + 20
        finds_blue = np.any(blue_img[h0:h1, w0:w1])
        finds_orange = np.any(orange_img[h0:h1, w0:w1])

        if self.context_manager.get_direction() == Direction.LEFT:
            self._process_left_direction(Color.BLUE if finds_blue else (Color.ORANGE if finds_orange else None))
        else:
            self._process_right_direction(Color.ORANGE if finds_orange else (Color.BLUE if finds_blue else None))
```

State machine (LEFT direction) in [`LapTracker._process_left_direction`](code/XX_2025_package/classes/lap_tracker.py):
- INITIAL_STATE → LOOKING_FOR_BLUE
- LOOKING_FOR_BLUE: if BLUE seen → LOOKING_FOR_ORANGE
- LOOKING_FOR_ORANGE: if ORANGE seen → increment quarter, go to WAITING_STATE
- WAITING_STATE: after ~0.5s debounce → LOOKING_FOR_BLUE

```python
def _process_left_direction(self, detected_color):
    # INITIAL → LOOKING_FOR_BLUE
    # WAITING → after 0.5s → LOOKING_FOR_BLUE
    # LOOKING_FOR_BLUE + BLUE → LOOKING_FOR_ORANGE
    # LOOKING_FOR_ORANGE + ORANGE → increment quarter → WAITING
    if self._state == LapState.INITIAL_STATE:
        self._state = LapState.LOOKING_FOR_BLUE

    if self._state == LapState.WAITING_STATE:
        if self.time_stamp == 0:
            self.time_stamp = time.time()
        if time.time() - self.time_stamp >= 0.5:
            self._state = LapState.LOOKING_FOR_BLUE
            self.time_stamp = time.time()

    elif self._state == LapState.LOOKING_FOR_BLUE and detected_color == Color.BLUE:
        self._state = LapState.LOOKING_FOR_ORANGE

    elif self._state == LapState.LOOKING_FOR_ORANGE and detected_color == Color.ORANGE:
        self.context_manager.increment_quarter_lap_count()
        self._state = LapState.WAITING_STATE
```

State machine (RIGHT direction) in [`LapTracker._process_right_direction`](code/XX_2025_package/classes/lap_tracker.py) mirrors the logic:
- INITIAL_STATE → LOOKING_FOR_ORANGE
- LOOKING_FOR_ORANGE: if ORANGE seen → LOOKING_FOR_BLUE
- LOOKING_FOR_BLUE: if BLUE seen → increment quarter, go to WAITING_STATE
- WAITING_STATE: after ~0.5s → LOOKING_FOR_ORANGE

Quarter and lap accounting:
- Every time the color pair completes, [`ContextManager.increment_quarter_lap_count`](code/XX_2025_package/classes/context_manager.py) is called.
- The context tracks quarter count and laps; when enough quarters have been seen, the lap count increases.
- [`ContextManager.is_last_quarter`](code/XX_2025_package/classes/context_manager.py) and [`ContextManager.has_completed_laps`](code/XX_2025_package/classes/context_manager.py) are used to slow down or stop after the goal.

## End-to-End Usage Snippet

In the main loop ([code/XX_2025_package/main.py](code/XX_2025_package/main.py)):

```python
# Challenge 1: direction from lines
image_algorithms.get_direction_from_lines()

# Challenge 2: direction from free-space split
image_algorithms.get_direction_from_parking(camera_manager)

# While driving: update lap tracking from the window
lap_tracker.process_image(camera_manager.cnt_blueline, camera_manager.cnt_orangeline)

# Example of reacting to final quarter
if context_manager.is_last_quarter():
    speed = 4000  # slow down on final approach
```

This approach gives a robust start-direction choice for both challenges and a simple, debounced lap tracker.