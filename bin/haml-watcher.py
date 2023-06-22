#!/bin/env python

import sys
import time
import logging
import subprocess as SP
import os
import glob

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler

def haml_expand(file):
  logging.info(f"Expand {file}")
  ofile   = file.replace(".haml", ".html")
  try:
    command = f"set -x; haml render {file} > {ofile}"
    SP.run(command, shell=True, check=True)
  except SP.CalledProcessError:
    if os.path.exists(ofile):
      os.remove(ofile)
    logging.error(f"Error generating {ofile}")
    return False
  logging.info(f"Generated {ofile}")
  return True

class HamlHandler(FileSystemEventHandler):
  def on_created(self, event):
    if not event.is_directory and event.src_path.endswith('.haml'):
      haml_expand(event.src_path)

  def modified(self, event):
    if not event.is_directory and event.src_path.endswith('.haml'):
      haml_expand(event.src_path)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'

    for file in glob.glob(f"{path}/*.haml"):
      haml_expand(file)

    event_handler = HamlHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
