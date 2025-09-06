# Vision Methods and Decision Making

This document explains how the computer vision pipeline drives steering decisions for the robot:
- Wall following (how far up the image it sees black on both sides)
- Obstacle handling
- Inner/outer crash detection
- Arbitration (how actions are chosen)

## 1) Image pipeline (inputs used by algorithms)

The camera pipeline produces these images used by the algorithms:
- polygon_image: binary map of the drivable corridor (walls are black=0, free space is white=255)
- display_image: BGR frame used for debug overlays (text, lines, circles)
- obstacle_image / pink_obstacle_image: binary masks for color obstacles
- blueline_image & orangeline_image: per-color masks for lap tracking

<table>
  <tr>
    <td align="center">
      <strong>Display Image Open Challenge</strong><br>
      <img src="https://github.com/user-attachments/assets/924e428f-c0ea-4ef4-959d-12420b2773ab" width="700">
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Display Image Obstacle Challenge</strong><br>
      <img src="https://github.com/user-attachments/assets/f61b0e58-9b93-4888-8548-6ec4ca5e9cb8" width="700">
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Polygon Image</strong><br>
      <img src="https://github.com/user-attachments/assets/c8e8c91d-449f-45dc-88c7-7d1e1df058a3" width="700">
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Obstacle Image</strong><br>
      <img src="https://github.com/user-attachments/assets/35c2a820-98f5-4030-97ef-c1d3fdaa19da" width="700">
    </td>
  </tr>
  <tr>
    <td align="center">
      <strong>Lines Image</strong><br>
      <img src="https://github.com/user-attachments/assets/186cd617-33ae-475b-ba15-ccbb2e6fb1e4" width="700">
    </td>
  </tr>
</table>

See [`CameraManager`](code/XX_2025_package/classes/camera_manager.py) and [`ImageTransformUtils`](code/XX_2025_package/utils/image_transform_utils.py).

## 2) Wall following calculations

Goal: steer so that the nearest wall is observed at a desired “depth” (how far up the image) and “lateral” position (how far from the side).

How it works:
- The robot scans for black (wall) pixels:
  - Bottom-up along a small band of columns near the followed side (“how far up” the wall appears).
  - Side-in from the image center toward the followed side along a small band of rows (“how far inward” the wall appears).
- These samples are averaged into (avg_x, avg_y) by [`ImageAlgorithms.find_wall_to_follow`](code/XX_2025_package/classes/image_algoriths.py).
- [`ImageAlgorithms.calculate_servo_angle_from_walls`](code/XX_2025_package/classes/image_algoriths.py) builds a PD-like controller:
  - Proportional term: error = (avg_x + avg_y) − threshold.
  - Derivative term: change of that error across frames.
  - Direction sign (LEFT/RIGHT) is taken from context to steer the correct side.
- Gains and the target threshold come from [`CHALLENGE_CONFIG`](code/XX_2025_package/classes/image_algoriths.py) via [`ImageAlgorithms.calculate_wall_threshold_kp_kd`](code/XX_2025_package/classes/image_algoriths.py), adapting behavior per challenge/lap.
- Corner detection: a large negative jump in the wall error derivative marks a “corner,” returned via the is_corner flag for higher-level logic.

Notes:
- “How far up it sees black on both sides” is embodied in the dual scans (bottom-up and side-in) that together capture corridor geometry.

## 3) Obstacle handling calculations

When an obstacle is present (green/red/pink block), the robot computes an avoidance “object line,” converts it to an angle, and arbitrates with wall following.

Process in [`ImageAlgorithms.find_obstacle_angle_and_draw_lines`](code/XX_2025_package/classes/image_algoriths.py):
- Safety first: [`ImageAlgorithms.check_outer_wall_crash`](code/XX_2025_package/classes/image_algoriths.py). If a frontal collision risk is detected, immediately force a sharp evasive turn.
- Find the largest obstacle rectangle on the color mask and classify its color using HSV.
- Draw a guidance line from the obstacle center to a safe floor target x:
  - Green → pass on the right; Red → pass on the left (policy).
- Convert that line’s geometry into an object angle, then map it to a servo angle with a color-specific offset in [`ImageAlgorithms.calculate_servo_angle_from_obstacle`](code/XX_2025_package/classes/image_algoriths.py).
- Inner safety: [`ImageAlgorithms.check_inner_wall_crash`](code/XX_2025_package/classes/image_algoriths.py) disables obstacle passing if the inner wall is too close (falls back to wall following).

What the “mapping” does:
- It shifts and scales the object angle around straight-ahead so the servo turns just enough to skirt the obstacle, clamped to safe servo limits.

## 4) Crash detection

Two safety checks override normal behavior:
- Outer wall crash: [`ImageAlgorithms.check_outer_wall_crash`](code/XX_2025_package/classes/image_algoriths.py) probes a fixed point ahead, and if it’s black in the polygon image, commands an emergency turn away from the outer wall.
- Inner wall crash: [`ImageAlgorithms.check_inner_wall_crash`](code/XX_2025_package/classes/image_algoriths.py) probes several points near the inner side; if too close (especially with a short obstacle), obstacle passing is suppressed.

## 5) Arbitration: choosing the action

Both proposals are produced:
- Wall-following angle from [`ImageAlgorithms.calculate_servo_angle_from_walls`](code/XX_2025_package/classes/image_algoriths.py)
- Obstacle angle from [`ImageAlgorithms.calculate_servo_angle_from_obstacle`](code/XX_2025_package/classes/image_algoriths.py) (or None if no obstacle)

Selection rule in [`ImageAlgorithms.choose_output_angle`](code/XX_2025_package/classes/image_algoriths.py):
- If there is a valid obstacle-avoidance angle, prefer it; otherwise, follow the wall.

Priority in practice:
1) Outer wall crash → emergency avoidance
2) Valid obstacle avoidance → use it
3) Inner wall too close while avoiding → fall back to wall following
4) Otherwise → wall following

## 6) Tuning notes

- Controller gains/thresholds are challenge-aware via [`CHALLENGE_CONFIG`](code/XX_2025_package/classes/image_algoriths.py) and refined per lap in [`ImageAlgorithms.calculate_wall_threshold_kp_kd`](code/XX_2025_package/classes/image_algoriths.py).
- The direction (LEFT/RIGHT) simply flips the sign of the control so one algorithm works for both sides.
- Corner detection from the wall controller’s derivative is used elsewhere (for example during parking) to trigger special maneuvers.