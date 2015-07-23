import time
from multiprocessing.dummy import Process
from camera import Camera
from detector import Detector


class Tracker(object):
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.camera = Camera(config, logger)
        self.detector = Detector(self.camera)
        self.logger.debug('Tracker started')

    def track(self):
        #Process(target=self.handle_pan, args=()).start()
        #Process(target=self.handle_tilt, args=()).start()

        while True:
            self.detector.detect()

    def handle_pan(self):
        self.process(self.camera.pan,
                     self.camera.pan_q_cur_pos,
                     self.camera.pan_q_des_pos,
                     self.camera.pan_q_speed,
                     'pan')

    def handle_tilt(self):
        self.process(self.camera.tilt,
                     self.camera.tilt_q_cur_pos,
                     self.camera.tilt_q_des_pos,
                     self.camera.tilt_q_speed,
                     'tilt')

    def process(self, servo, cur_queue, desired_queue, speed_queue, type):
        speed = 0.1
        cur_pos = int(self.config.fetch('{0}_start'.format(type)))
        desired_pos = cur_pos + 1
        self.log('Process for {0} direction started at position {1}'.format(type, cur_pos), type)
        while True:
            time.sleep(speed)
            if cur_queue.empty():
                self.log('Current position queue empty. Saving current position ({0}) in queue.'.format(cur_pos), type)
                cur_queue.put(cur_pos)
            if not desired_queue.empty():
                self.log('Desired position queue empty. Saving desired position ({0}) in queue.'.format(desired_pos), type)
                desired_pos = desired_queue.get()
            if not speed_queue.empty():
                _speed = speed_queue.get()
                speed = 0.1 / _speed
                self.log('Speed queue not empty. Found speed {0}, took current speed to {1}'.format(_speed, speed), type)
            if cur_pos < desired_pos:
                cur_pos += 1
                cur_queue.put(cur_pos)
                self.log(
                    'Current position smaller than desired position ({0}). '
                    'Incremented current position and moved servo to {1}'.format(desired_pos, cur_pos), type)
                servo.move(servo.assure_min(cur_pos))
                if not cur_queue.empty():
                    cur_queue.get()
            else:  # cur_pos > desired_pos
                self.log(
                    'Current position bigger than desired position ({0}). '
                    'Decremented current position and moved servo to {1}'.format(desired_pos, cur_pos), type)
                cur_pos -= 1
                cur_queue.put(cur_pos)
                servo.move(servo.assure_max(cur_pos))
                if not cur_queue.empty():
                    cur_queue.get()
            if cur_pos == desired_pos:
                speed = 1

    def log(self, message, direction):
        self.logger.debug('[{0}] {1}'.format(direction, message))
