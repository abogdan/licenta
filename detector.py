import cv2
import time


class Detector(object):
    def __init__(self, camera):
        self.camera = camera
        self.config = camera.config
        self.logger = camera.logger

        self.frontal = cv2.CascadeClassifier(self.config.fetch('frontface_alt'))
        self.profile = cv2.CascadeClassifier(self.config.fetch('profile'))

        self.face = [0, 0, 0, 0]
        self.face_center = [0, 0]
        self.last_face = 0

    def haar_detect(self, cascade, frame, size=(80, 80)):
        start_time = time.time()
        haar = (cv2.cv.CV_HAAR_DO_CANNY_PRUNING + cv2.cv.CV_HAAR_FIND_BIGGEST_OBJECT + cv2.cv.CV_HAAR_DO_ROUGH_SEARCH)
        res = getattr(cascade, 'detectMultiScale')(frame, 1.3, 4, haar, size)
        self.logger.error("Detect shapes took %s s" % (round((time.time() - start_time), 3)))
        return res

    def detect(self):

        found = False

        if not found:
            if self.last_face <= 1:
                frame = self.camera.get_frames(5)[-1]
                faces = self.haar_detect(self.frontal, frame, (80, 80))
                if faces != ():
                    self.last_face = 1
                    for f in faces:
                        found = True
                        self.face = f

        if not found:
            if self.last_face == 0 or self.last_face == 2:
                frame = self.camera.get_frames(5)[-1]
                faces = self.haar_detect(self.profile, frame, (80, 80))
                if faces != ():
                    self.last_face = 2
                    for f in faces:
                        found = True
                        self.face = f

        if not found:
            if self.last_face == 0 or self.last_face == 3:
                frame = self.camera.get_frames(5)[-1]
                cv2.flip(frame, 1, frame)
                faces = self.haar_detect(self.profile, frame, (80, 80))
                if faces != ():
                    self.last_face = 3
                    for f in faces:
                        found = True
                        self.face = f

        if not found:
            self.last_face = 0
            self.face = [0, 0, 0, 0]

        x, y, w, h = self.face
        self.face_center = [(w/2+x), (h/2+y)]
        print '{0}, {1}'.format(self.face_center[0], self.face_center[1])

        if self.face_center[0] != 0:
            if self.face_center[0] > 180:
                self.camera.left(2, 1)
            if self.face_center[0] > 190:
                self.camera.left(2, 2)
            if self.face_center[0] > 200:
                self.camera.left(2, 3)

            if self.face_center[0] < 140:
                self.camera.right(2, 1)
            if self.face_center[0] < 130:
                self.camera.right(2, 2)
            if self.face_center[0] < 120:
                self.camera.right(2, 3)

            if self.face_center[1] > 140:
                self.camera.down(2, 1)
            if self.face_center[1] > 150:
                self.camera.down(2, 2)
            if self.face_center[1] > 160:
                self.camera.down(2, 3)

            if self.face_center[1] < 100:
                self.camera.up(2, 3)
            if self.face_center[1] < 90:
                self.camera.up(2, 2)
            if self.face_center[1] < 80:
                self.camera.up(2, 3)
