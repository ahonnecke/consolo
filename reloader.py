#!/usr/bin/env python3
import json
import logging
import os
import shutil
import time
import zipfile
from functools import cached_property
from pathlib import Path
from typing import TypeVar

import boto3
import requests
from boto3.session import Session
from botocore.exceptions import ClientError
from watchdog.events import (FileCreatedEvent, FileModifiedEvent,
                             FileSystemEventHandler)
from watchdog.observers import Observer

logger = logging.getLogger(__name__)

UploadableEvent = TypeVar("T", FileCreatedEvent, FileModifiedEvent)

class Watcher:
    """Watch a directory for file events."""

    def __init__(self, dirpath, handler) -> None:
        """Init and set dirpath to watch and handler to fire."""
        self.observer = Observer()
        self.dirpath = dirpath
        self.event_handler = handler

    def run(self) -> None:
        """Start watching self.dirpath."""
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
    """Filter and handlelfile system events."""

    def __init__(self, on_create, on_modify) -> None:
        """Init and set handler."""
        self.on_modify = on_modify
        self.on_create = on_create

    def on_any_event(self, event: UploadableEvent) -> None:
        """Handle file event."""
        if event.is_directory:
            return None

        if isinstance(event, FileCreatedEvent):
            # Take any action here when a file is first created.
            logger.info(f"Received created event - {event.src_path}.")

            # TODO: perform AST check
            return self.on_create(event)

        elif isinstance(event, FileModifiedEvent):
            # Taken any action here when a file is modified.
            logger.info(f"Received modified event - {event.src_path}.")

            # TODO: perform AST check
            return self.on_modify(event)


class LambdaWrapper:
    """Generic lambda object."""

    def __init__(self, profile_name: str, function_name: str, local_root: str) -> None:
        """Set AWS profile, AWS function name and local path to src."""
        self.profile_name = profile_name
        self.function_name = function_name
        self.local_root = Path(local_root)

    @cached_property
    def session(self) -> Session:
        """Get the boto session for a given profile."""
        return boto3.Session(profile_name=self.profile_name)

    @cached_property
    def lambda_client(self):
        """Get the lambda client for the current session."""
        return self.session.client("lambda")


class LambdaReloader(LambdaWrapper):
    """Map an AWS function onto a local dir."""

    @property
    def archive_dir(self) -> Path:
        """Location for building archive of function."""
        return Path("/tmp")

    @property
    def archive(self) -> Path:
        """Get the archive filename."""
        return self.archive_dir.joinpath(".".join([self.function_name, "zip"]))

    def validate_root(self) -> bool:
        """Raise if destination directory does not exist."""
        if not os.path.isdir(self.local_root):
            raise RuntimeError(f"Local dir {self.local_root} does not exist.")

        return True

    def download_function_code(self) -> None:
        """Download and extract all lambda files to local, overwriting existing."""
        response = self.lambda_client.get_function(FunctionName=self.function_name)
        zip_url = response["Code"]["Location"]

        r = requests.get(zip_url, allow_redirects=True)
        open(self.archive, "wb").write(r.content)

    def read_manifest(self):
        """Read the local list of files in the lambda."""
        self.zip = zipfile.ZipFile(self.archive)
        self.manifest = self.zip.namelist()
        self.write_manifest()
        return self.manifest

    @property
    def manifest_path(self) -> Path:
        """Path to the local manifest file."""
        return self.archive_dir.joinpath(f".consolo.{self.function_name}.json")

    def write_manifest(self) -> None:
        """Write the in memory list of files to local storate."""
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            return json.dump(self.manifest, f, ensure_ascii=False, indent=4)

    def expand_function_code(self) -> None:
        """Unpack the archive."""
        shutil.unpack_archive(self.archive, self.local_root)

    def clobber_local(self) -> None:
        """Download AWS lambda onto local directory.

        TODO: delete existing files?
        """
        self.download_function_code()
        self.read_manifest()
        self.expand_function_code()

    def extract_relative_event_path(self, event) -> str:
        """Extract relative path from event."""
        path = str(event.src_path)
        prefix = str(self.local_root) + "/"

        if prefix and path.startswith(prefix):
            return path[len(prefix) :]

        raise RuntimeError("Prefix was not in path")

    def event_file_is_in_manifest(self, event) -> bool:
        """Determine if the given path is in the manfest."""
        self.read_manifest()

        # TODO: cache manifest?
        return self.extract_relative_event_path(event) in self.manifest

    def handle_create(self, event: FileCreatedEvent) -> None:
        """Handle a file event."""
        self.read_manifest()

        if not self.event_file_is_in_manifest(event):
            # This should always fire, new file should not be in the manifest.
            self.add_event_file_to_manifest(event)

        self.update_function_code()

    def add_event_file_to_manifest(self, event) -> None:
        """Add file path from event to manifest."""
        self.manifest.append(self.extract_relative_event_path(event))
        self.write_manifest()

    def handle_modify(self, event: FileModifiedEvent) -> None:
        """Handle a file event."""
        if not self.event_file_is_in_manifest(event):
            logger.debug(self.extract_relative_event_path(event))
            logger.debug("File is not in manifest")
            return

        self.update_function_code()

    def update_function_code(self) -> None:
        """
        Compress and upload local code.

        Updates the code for a Lambda function by submitting a .zip archive that contains
        the code for the function.

        :return: Data about the update, including the status.
        """
        logger.debug("compressing")
        deployment_package = self.make_archive(self.function_name)
        logger.debug(f"compressed {deployment_package}")

        try:
            response = self.lambda_client.update_function_code(
                FunctionName=self.function_name, ZipFile=self.read_archive()
            )
        except ClientError as err:
            if err.response["Error"]["Code"] == "ResourceConflictException":
                # TODO: suppress this
                logger.debug("Tried to upload while uploading.")
                return

            logger.error(
                "Couldn't update function %s. Here's why: %s: %s",
                self.function_name,
                err.response["Error"]["Code"],
                err.response["Error"]["Message"],
            )
            raise
        else:
            logger.info("Finished uploading.")
            return response

    def make_archive_all(self, name) -> None:
        """Create zipfile of function_name directory and upload to function_name."""
        # TODO: Don't hardcode directory name
        # TODO: Support exsiting directory name
        shutil.make_archive(name, "zip", name)

    def read_archive(self) -> bytes:
        """Open archive and return bytes for upload."""
        with open(self.archive, "rb") as file_data:
            return file_data.read()

    def make_archive(self, name) -> str:
        """Create archive of all files in the manifest."""
        # Open a zip file at the given filepath. If it doesn't exist, create one.
        # If the directory does not exist, it fails with FileNotFoundError
        with zipfile.ZipFile(self.archive, "w") as zipf:
            for file in self.manifest:
                # Add a file located at the source_path to the destination within the zip
                # file. It will overwrite existing files if the names collide, but it
                # will give a warning
                source_path = self.local_root.joinpath(file)
                zipf.write(source_path, file)

        return str(self.local_root.joinpath(self.archive))

    def watch(self) -> None:
        """Start the directory watching daemon."""
        w = Watcher(
            self.local_root,
            Handler(on_create=self.handle_create, on_modify=self.handle_modify),
        )
        w.run()
