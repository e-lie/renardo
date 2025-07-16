#!/usr/bin/env python3
"""Test script for project, track, and FX chain operations with reaside."""

import sys
import os
import time

from renardo.reaper_backend import connect


reaper = connect()

print(reaper)

project = reaper.current_project

print(project.name)

print(project.tracks)

print(project.tracks[0].name)

