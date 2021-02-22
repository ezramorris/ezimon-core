# EziMon Core

EziMon is a project to create an **Ezi**-to-use, extensible realtime data 
**Mon**itor. Ultimately, the project will consist of two main parts:

* *EziMon GUI* (not started): a rich, cross-platform GUI application for 
  monitoring data streams in real-time
* *EziMon Core* (this repo): provides the fundamental functionality for EziMon,
  including a generic API to access hardware interfaces, as well as a rich
  protocol handling capability to pack and unpack data in realtime. This is 
  designed to be completely independent of EziMon GUI, being useful on its own
  as a library for other projects.
  
EziMon is in very early stages of development, so doesn't do a lot yet!

## Installation and usage

Requires Python 3.6 or newer.

This package is not yet available on PyPI. It can be installed along with all
dependencies either by cloning this repo locally then running from the repo
directory:

    pip install -e .

Or directly from the repo:

    pip install -e git+https://github.com/ezramorris/ezimon-core.git#egg=ezimon-core

## Goals

EziMon Core should be:

* Easy to use. All public interfaces of the library should be straightforward, 
  Pythonic, and obvious to use.
* Extensible. It should be possible to add additional hardware interfaces,
  types of protocols etc. to the system without interfering with other 
  components or major rework.
* Tested and documented. >80% unit test coverage, integration tests for common
  use cases, all public interfaces documented, examples written.
