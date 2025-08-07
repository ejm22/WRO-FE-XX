from XX_2025_package.utils.image_utils import ImageUtils
import numpy as np

MIDDLE_X = 320
THRESHOLD_Y_HEIGHT = 145
old_diff = 0
direction = 1
#threshold = 400

class ImageAlgorithms:
    @classmethod
    def get_direction(cls, camera_object):
        cls.direction = -1 if camera_object.length_blue > camera_object.length_orange else 1
        

    @classmethod
    def get_threshold(cls, elapsed):
        #cls.threshold = 250 if elapsed < 2.25 else 400
        cls.threshold = 400

    def find_black_from_bottom(img, col_range):
        y_vals = []
        for x in col_range:
            for y in reversed(range(ImageUtils.PIC_HEIGHT - 30)):
                if img[y,x] == 0:
                    y_vals.append(y)
                    break
            else:
                y_vals.append(0)
        return y_vals

    def find_black_sides(img, rotation, row_range):
        end_index = 0 if rotation == -1 else ImageUtils.PIC_WIDTH - 1
        x_vals = []
        for y in row_range:
            for x in range(ImageUtils.PIC_WIDTH // 2, end_index, rotation):
                if img[y,x] == 0:       
                    x_vals.append(x)
                    break
            else:
                x_vals.append(end_index)
        return x_vals
    
    def find_angle_from_img(img, nbr_cols = 10):
        left_cols = range(0, nbr_cols)
        right_cols = range(ImageUtils.PIC_WIDTH - nbr_cols, ImageUtils.PIC_WIDTH)

        left_y_vals = ImageAlgorithms.find_black_from_bottom(img, left_cols)
        right_y_vals = ImageAlgorithms.find_black_from_bottom(img, right_cols)

        avg_left_y = np.mean(left_y_vals)
        avg_right_y = np.mean(right_y_vals)

        angle = 88 - (int((avg_left_y - avg_right_y) * 0.14))
        #print(angle)
        return angle
    
    @staticmethod
    def find_angle_from_img2(img, nbr_cols = 10):
        global old_diff
        dir = ImageAlgorithms.direction
        cols = range(0, nbr_cols) if dir == -1 else range(ImageUtils.PIC_WIDTH - nbr_cols, ImageUtils.PIC_WIDTH)
        rows = range(ImageUtils.PIC_HEIGHT - 3*nbr_cols, ImageUtils.PIC_HEIGHT - 2*nbr_cols)

        y_vals = ImageAlgorithms.find_black_from_bottom(img, cols)
        x_vals = ImageAlgorithms.find_black_sides(img, dir, rows)

        avg_y = np.mean(y_vals)
        avg_x = np.mean(x_vals)
        
        if dir == 1 : avg_x = 640 - avg_x
        print("avg_y : ", avg_y)
        print("avg_x : ", avg_x)
        diff = avg_y + avg_x - 400 #ImageAlgorithms.threshold
        differential_adjust = (diff - old_diff) * 0.25
        angle =  88 + dir * (int((diff) * 0.2) + differential_adjust)
        old_diff = diff
        print("angle : ",angle)
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
        
        #print(-coeff)
        return -coeff
    
    def get_corner_line_coeff(corner_line_coords):
        if corner_line_coords is None : return 0

        y0 = corner_line_coords[0][1]
        y1 = corner_line_coords[1][1]
        x0 = corner_line_coords[0][0]
        x1 = corner_line_coords[1][0]

        avg_y = (y0 + y1) / 2
        if avg_y > 205:
            avg_x = (x0 + x1) / 2
            coeff = (avg_x - 110) * 0.2        
            return -coeff
        else:
            return 0

    @staticmethod
    def calculate_angle(img):
        angle1 = ImageAlgorithms.find_angle_from_img2(img)
        angle = angle1
        if angle < 48:
            angle = 49
        elif angle > 128:
            angle = 127

        return int(angle)