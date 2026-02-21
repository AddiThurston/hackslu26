import cv2 as cv
import numpy as np

class GeometricFitter:

    @staticmethod
    def __sort_points__(points):
        rectangle_coords = np.zeros((4,2), dtype="float32")

        sums = points.sum(axis=1)
        differences = np.diff(points, axis=1)

        rectangle_coords[0] = points[np.argmin(sums)] # Top left point
        rectangle_coords[2] = points[np.argmax(sums)] # Bottom right point

        rectangle_coords[1] = points[np.argmin(differences)] # Top right point
        rectangle_coords[3] = points[np.argmax(differences)] # Bottom left point

        return rectangle_coords

    @staticmethod
    def FitImage(image, hysteresis_low : int, hysterises_high : int):
        grayscale_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        ret, threshold = cv.threshold(grayscale_image, 127, 255, 0)

        contours, hierarchy = cv.findContours(threshold, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        cont = sorted(contours, key=cv.contourArea, reverse=True)

        for contour in cont:
            perimeter = cv.arcLength(contour, True)
            epsilon = 0.02 * perimeter
            approx = cv.approxPolyDP(contour, epsilon, True)

            if len(approx) == 4:
                pts = approx.reshape(4, 2)

                rect = GeometricFitter.__sort_points__(pts)

                # Letter paper aspect ratio
                heightPx = 550
                widthPx = 425

                # corrected_image = np.zeroes((1100,850), dtype="float32")
                cor_im_corners = np.array([[0,0], [widthPx - 1,0], [widthPx - 1,heightPx - 1], [0,heightPx - 1]], dtype="float32" )

                transformation_matrix = cv.getPerspectiveTransform(rect, cor_im_corners)

                corrected_image = cv.warpPerspective(image, transformation_matrix, (widthPx, heightPx))

                return corrected_image








        cv.imshow("Detected:", image)
        cv.waitKey(0)

        cv.destroyAllWindows()

if __name__ == "__main__":
    image = cv.imread("Canvas Helper test image.webp")

    fittedImage = GeometricFitter.FitImage(image, 50, 150);
    cv.imshow("image", fittedImage)
    cv.waitKey(0)
    cv.destroyAllWindows()



