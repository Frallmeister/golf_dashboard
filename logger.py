import sys
import logging

formatter = logging.Formatter("%(levelname)s: %(asctime)s: %(filename)s: %(lineno)d: %(message)s")
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

filehandler = logging.FileHandler("logfile.log")
filehandler.setFormatter(formatter)

streamhandler = logging.StreamHandler(sys.stdout)
streamhandler.setFormatter(formatter)

log.addHandler(filehandler)
log.addHandler(streamhandler)