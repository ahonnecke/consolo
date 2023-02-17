#!/usr/bin/env python3
import json
import logging
import os
import shutil
import time
import zipfile
from functools import cached_property
from pathlib import Path

import boto3
import requests
from argdantic import ArgParser
from botocore.exceptions import ClientError
from watchdog.events import (FileCreatedEvent, FileModifiedEvent,
                             FileSystemEventHandler)
from watchdog.observers import Observer

logger = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))

logging.getLogger('boto').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)

class Watcher:
    def __init__(self, dirpath, handler):
        self.observer = Observer()
        self.dirpath = dirpath
        self.event_handler = handler

    def run(self):
        self.observer.schedule(self.event_handler, self.dirpath, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            logger.error("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):
    def __init__(self, onchange):
        self.onchange = onchange

    def on_any_event(self, event):
        if event.is_directory:
            return None

        if isinstance(event, FileCreatedEvent):
            # Take any action here when a file is first created.
            logger.info(f"Received created event - {event.src_path}.")
            self.onchange(event)

        elif isinstance(event, FileModifiedEvent):
            # Taken any action here when a file is modified.
            logger.info(f"Received modified event - {event.src_path}.")
            self.onchange(event)




class LambdaWrapper:
    def __init__(self, profile_name, function_name, local_root):
        self.profile_name = profile_name
        self.function_name = function_name
        self.local_root = local_root

    @cached_property
    def session(self):
        return boto3.Session(profile_name=self.profile_name)

    @cached_property
    def lambda_client(self):
        return self.session.client("lambda")


class LambdaReloader(LambdaWrapper):
    @property
    def archive(self):
        return ".".join([self.function_name, "zip"])

    def is_downloaded(self):
        return os.path.isdir(self.function_name)

    def download_function_code(self):
        response = self.lambda_client.get_function(FunctionName=self.function_name)
        zip_url = response["Code"]["Location"]

        r = requests.get(zip_url, allow_redirects=True)
        open(self.archive, "wb").write(r.content)

    def read_manifest(self):
        self.zip = zipfile.ZipFile(self.archive)
        self.manifest = self.zip.namelist()
        # TODO deal with CWD
        with open(".consolo.json", "w", encoding="utf-8") as f:
            json.dump(self.manifest, f, ensure_ascii=False, indent=4)

    def expand_function_code(self):
        shutil.unpack_archive(self.archive, self.function_name)

    def clone(self):
        self.download_function_code()
        self.read_manifest()
        self.expand_function_code()

    def path_is_in_manifest(self, relative_path) -> bool:
        self.read_manifest()
        # TODO: cache manifest?
        return (relative_path in self.manifest)

    def handle_event(self, event: FileModifiedEvent):
        path = event.src_path
        relative_path=path.lstrip(str(self.local_root))

        if self.path_is_in_manifest(relative_path):
            self.update_function_code()

    def update_function_code(self):
        """
        Updates the code for a Lambda function by submitting a .zip archive that contains
        the code for the function.

        :param deployment_package: The function code to update, packaged as bytes in
                                   .zip format.
        :return: Data about the update, including the status.
        """
        logger.debug("compressing")
        deployment_package = self.make_archive(self.function_name)
        logger.debug("compressed")

        try:
            response = self.lambda_client.update_function_code(
                FunctionName=self.function_name, ZipFile=deployment_package
            )
        except ClientError as err:
            logger.error(
                "Couldn't update function %s. Here's why: %s: %s",
                self.function_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            return response

    def make_archive(self, name):
        shutil.make_archive(name, "zip", name)
        with open(self.archive, "rb") as file_data:
            return file_data.read()


parser = ArgParser()


@parser.command()
def main(
    profile_name: str,
    function_name: str,
    hot_reload: bool = False,
):
    """Entrypoint for AWS lambda hot reloader, CLI args in signature."""
    ROOT = Path.cwd()
    PROFILE = profile_name

    reloader = LambdaReloader(PROFILE, function_name, ROOT)

    # TODO: perform the download and compare
    if not reloader.is_downloaded():
        # If there no code, then the user likely wants to download the lambda
        reloader.clone()

    if hot_reload:
        # # If there IS code, then the user likely wants to upload the lambda
        project = ROOT.joinpath(function_name)
        w = Watcher(project, Handler(onchange=reloader.handle_event))
        w.run()
    elif reloader.is_downloaded():
        #TODO don't check is downloaded a second time?
        reloader.update_function_code()


if __name__ == "__main__":
    parser()
