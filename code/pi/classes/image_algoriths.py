from utils.image_utils import ImageUtils
import numpy as np

MIDDLE_X = 320
THRESHOLD_Y_HEIGHT = 145


class ImageAlgorithms:

    def find_black_from_bottom(img, col_range):
            y_vals = []
            for x in col_range:
                for y in reversed(range(ImageUtils.PIC_HEIGHT)):
                    if img[y,x] == 0:
                        y_vals.append(y)
                        break
                else:
                    y_vals.append(0)
            return y_vals
    
    def find_angle_from_img(img, nbr_cols = 10):
        left_cols = range(0, nbr_cols)
        right_cols = range(ImageUtils.PIC_WIDTH - nbr_cols, ImageUtils.PIC_WIDTH)

        left_y_vals = ImageAlgorithms.find_black_from_bottom(img, left_cols)
        right_y_vals = ImageAlgorithms.find_black_from_bottom(img, right_cols)

        avg_left_y = np.mean(left_y_vals)
        avg_right_y = np.mean(right_y_vals)

        angle = 88 - (int((avg_left_y - avg_right_y) * 0.14))
        print(angle)
        return angle
    
    def get_top_line_coeff(top_line_coords):
        if top_line_coords is None : return 0

        y0 = top_line_coords[0][1]
        y1 = top_line_coords[1][1]
        x0 = top_line_coords[0][0]
        x1 = top_line_coords[1][0]

        avg_y = (y0 + y1) / 2
        if avg_y < THRESHOLD_Y_HEIGHT : return 0

        avg_x = (x0 + x1) / 2
        coeff = (avg_x - MIDDLE_X) * 0.2
        
        print(-coeff)
        return -coeff

    @staticmethod
    def calculate_angle(img):
        coords = ImageUtils.get_top_line_coords(img)
        angle = ImageAlgorithms.find_angle_from_img(img) + ImageAlgorithms.get_top_line_coeff(coords)
        print(f"angle: {angle}")

        if angle < 48:
            angle = 49
        elif angle > 128:
            angle = 127

        return int(angle)