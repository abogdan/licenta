import cv2
from servo import Servo
from multiprocessing import Queue


class Camera(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, config, logger):
        controller = open(config.fetch('servo_controller'), 'w')
        self.tilt = Servo(
            config.fetch('tilt_gpio'),
            controller,
            (int(config.fetch('tilt_max')), int(config.fetch('tilt_min'))))
        self.tilt.cur_pos = config.fetch('tilt_start')

        self.pan = Servo(
            config.fetch('pan_gpio'),
            controller,
            (int(config.fetch('pan_max')), int(config.fetch('pan_min'))))
        self.pan.cur_pos = config.fetch('pan_start')

        self.tilt_q_cur_pos = Queue()
        self.tilt_q_des_pos = Queue()
        self.tilt_q_speed = Queue()
        self.pan_q_cur_pos = Queue()
        self.pan_q_des_pos = Queue()
        self.pan_q_speed = Queue()

        self.cam = cv2.VideoCapture(int(config.fetch('camera_id')))
        self.cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, float(config.fetch('frame_width')))
        self.cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, float(config.fetch('frame_height')))

        self.config = config
        self.logger = logger

    def get_frame(self):
        return self.cam.read()[1]

    def get_frames(self, count):
        frames = []
        for i in range(count):
            frames.append(self.get_frame())
        return frames

    def up(self, distance, speed):
        cur_pos = int(self.tilt.cur_pos)

        desired_pos = cur_pos - int(distance)
        self.logger.info('[UP] {0} -> {1}'.format(cur_pos, desired_pos))
        self.tilt.move(desired_pos)
        self.tilt.cur_pos = desired_pos
        return

        if not self.tilt_q_cur_pos.empty():
            cur_pos = self.tilt_q_cur_pos.get()
        desired_pos = self.tilt.assure_max(int(cur_pos) - int(distance))
        self.tilt_q_des_pos.put(desired_pos)
        self.tilt_q_speed.put(speed)

    def down(self, distance, speed):
        cur_pos = int(self.tilt.cur_pos)

        desired_pos = cur_pos + int(distance)
        self.logger.info('[DOWN] {0} -> {1}'.format(cur_pos, desired_pos))
        self.tilt.move(desired_pos)
        self.tilt.cur_pos = desired_pos
        return

        if not self.tilt_q_cur_pos.empty():
            cur_pos = self.tilt_q_cur_pos.get()
        desired_pos = self.tilt.assure_min(int(cur_pos) + int(distance))
        self.tilt_q_des_pos.put(desired_pos)
        self.tilt_q_speed.put(speed)

    def left(self, distance, speed):
        cur_pos = int(self.pan.cur_pos)

        desired_pos = cur_pos - int(distance)
        self.logger.info('[LEFT] {0} -> {1}'.format(cur_pos, desired_pos))
        self.pan.move(desired_pos)
        self.pan.cur_pos = int(desired_pos)
        return

        if not self.pan_q_cur_pos.empty():
            cur_pos = self.pan_q_cur_pos.get()
        desired_pos = self.pan.assure_max(int(cur_pos) - int(distance))
        self.pan_q_des_pos.put(desired_pos)
        self.pan_q_speed.put(speed)

    def right(self, distance, speed):
        cur_pos = int(self.pan.cur_pos)

        desired_pos = cur_pos + int(distance)
        self.logger.info('[RIGHT] {0} -> {1}'.format(cur_pos, desired_pos))
        self.pan.move(desired_pos)
        self.pan.cur_pos = desired_pos
        return

        if not self.pan_q_cur_pos.empty():
            cur_pos = self.pan_q_cur_pos.get()
        desired_pos = self.pan.assure_min(int(cur_pos) + int(distance))
        self.pan_q_des_pos.put(desired_pos)
        self.pan_q_speed.put(speed)
