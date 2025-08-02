from utils.image_utils import ImageUtils
import numpy as np

MIDDLE_X = 320
THRESHOLD_Y_HEIGHT = 145
old_diff = 0

class ImageAlgorithms:

    def get_direction():
        return -1

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
        end_index = 0 if rotation == -1 else ImageUtils.PIC_WIDTH
        x_vals = []
        for y in row_range:
            for x in range(ImageUtils.PIC_WIDTH // 2, end_index, rotation):
                if img[y,x] == 0:
                    x_vals.append(x)
                    break
            else:
                x_vals.append(0)
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
    
    def find_angle_from_img2(img, nbr_cols = 10):
        global old_diff
        direction = ImageAlgorithms.get_direction()
        cols = range(0, nbr_cols) if direction == -1 else range(ImageUtils.PIC_WIDTH - nbr_cols, ImageUtils.PIC_WIDTH)
        rows = range(ImageUtils.PIC_HEIGHT - 3*nbr_cols, ImageUtils.PIC_HEIGHT - 2*nbr_cols)

        y_vals = ImageAlgorithms.find_black_from_bottom(img, cols)
        x_vals = ImageAlgorithms.find_black_sides(img, direction, rows)

        avg_y = np.mean(y_vals)
        avg_x = np.mean(x_vals)
        
        #Impose a min value
        #avg_left_y = max (160, avg_left_y)
        print("avg_y : ", avg_y)
        print("avg_x : ", avg_x)
        #angle = 88 - (int((avg_left_y - avg_right_y) * 0.14))
        diff = avg_y + avg_x - 400
        differential_adjust = (diff - old_diff) * 0.25
        angle =  88 - int((diff) * 0.2) - differential_adjust
        #angle =  88 - int(((avg_y) - 300) * 0.2)
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
        #print("avg_y = ", avg_y)
        if avg_y > 205:
            avg_x = (x0 + x1) / 2
            coeff = (avg_x - 110) * 0.2
        
            #print(-coeff)
            return -coeff
        else:
            return 0

    @staticmethod
    def calculate_angle(img):
        #coords = ImageUtils.get_top_line_coords(img)
        #angle = ImageAlgorithms.find_angle_from_img(img) + ImageAlgorithms.get_top_line_coeff(coords)
        #coords = ImageUtils.get_corner_line_coords(img)
        angle1 = ImageAlgorithms.find_angle_from_img2(img) 
        #angle2 = ImageAlgorithms.get_corner_line_coeff(coords)
        angle = angle1 #+ angle2
        #print(f"angle1 = {angle1}")#, angle2 = {angle2}")
        #print(f"angle: {angle}")

        if angle < 48:
            angle = 49
        elif angle > 128:
            angle = 127

        return int(angle)