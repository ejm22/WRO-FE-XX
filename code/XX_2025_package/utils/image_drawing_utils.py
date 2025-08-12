import cv2

class ImageDrawingUtils:

    @staticmethod
    def add_text_to_image(image, text, position=(50, 50), color=(255, 255, 255)):
        """
        Add text to an image.

        Parameters:
            image, text to add, position (tuple), color (rgb format).

        Returns:
            The image with the text added.
        """
        cv2.putText(image, text, position, cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        return image

if __name__ == "__main__":
    # Example usage
    img = cv2.imread("./local/img.webp")
    ImageDrawingUtils.add_text_to_image(img, "angle : 34.5", color=(0, 255, 0))
    cv2.imshow("Image", img)
    cv2.waitKey(0) 