#!/usr/bin/python

import os
import sys
import traceback
import logging
from optparse import OptionParser
from config import Config
from logger import build_logger
from tracker import Tracker


if __name__ == '__main__':
    config = None
    logger = None

    try:
        parser = OptionParser(usage="usage: %prog [-c CONFIG]")
        parser.add_option(
            "-c",
            "--config",
            action="store",
            dest="config",
            type="str",
            help="Config file, default %default",
            default="./config.ini")

        options, args = parser.parse_args()

        if not os.path.isfile(options.config):
            raise RuntimeError('Given config file was not found')

        config = Config()
        config.read(options.config)
        logger = build_logger(config.fetch('logs_dir'), logging.DEBUG)

        app = Tracker(config, logger)
        app.track()

    except KeyboardInterrupt as e:
        if logger is not None:
            logger.info('Tracker stopped by user. PID: {0}'.format(os.getpid()))
        else:
            print 'Tracker stopped by user. PID: {0}'.format(os.getpid())
    except Exception as e:
        if logger is not None:
            logger.critical(e.message, exc_info=True)
        else:
            print traceback.format_exc()
