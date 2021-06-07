#!/usr/bin/env python
# encoding: utf-8
"""
custom_logger.py

Created by Patrick Shaner 2021-04-21

Copyright (c) 2021 Patrick Shaner, All rights reserved
THE INFORMATION CONTAINED HEREIN IS PROPRIETARY AND CONFIDENTIAL


Custom logging module created for easy consistent initialization across multiple modules.
This file is not tightly coupled requires no extra modules / libraries other
than what is built into python 3.6+

Enhancement off original version reads for an environmental variable to define the sns topic for subscribers to
listen to events generated from logging prcess

Version 2021-04-21:
    Created for custom logging.
"""
import os
import subprocess
import logging
import logging.config
import inspect
from logging import Logger

class LoggerException(Exception):
    pass


class CustomLogger:
    """
    Custom logging functionality for data lake class methods created as a factory class.

    Usage
    ------
        from utility.logging import CustomLogger
        log = CustomLogger.log(name=__file__)
        log.debug("Debug Message")
        log.info("Info Message")
        log.warning("Warning Message")
        log.error("Error Message")
        log.critical("Critical Message")
        log.exception("Exception Raised")

    Constructors
    ------------
    log(kwargs)
        :name : str
            This is the logging module or name of class initializing the logging.
        :configuration: str
            Allows caller to pass in configuration file.
            ::Notes::
                If configuration is set overwrites other arguments
        :sys_out: bool
            Defines if logging should be written to system.out.  Default = True
        :system_level: str
            The logging level type to set what messages will be displayed to system.out, Default = DEBUG
        :stream_format: str
            Format of the logging output for system.out.  Can be defined by caller but not recommended
                %(asctime)s [-%(levelname)s-] [%(name)s] %(message)s
        : log_file: str
            File path including the file name to write logs to. Default = None
        :file_level: str
            The logging level type to write to the log file.  Default = DEBUG
        :file_format: str
            Format of the logging output for log file. Can be defined by caller but not recommended
                %(asctime)s [-%(levelname)s-] [%(name)s] %(message)s

        Creates a new instance of python logging with the name of either variable passed in the name
        argument of the calling module.

        Sample output:
        04-01-2020 10:30:09 [WARNING] [test_default_logging_without_name] Test Warning
        04-01-2020 10:30:09 [ERROR] [test_default_logging_without_name] Test Exception

    dev_log(kwargs)
        :name : str
            This is the logging module or name of class initializing the logging.
        :configuration: str
            Allows caller to pass in configuration file.
            ::Notes::
                If configuration is set overwrites other arguments
        :sys_out: bool
            Defines if logging should be written to system.out.  Default = True
        :system_level: str
            The logging level type to set what messages will be displayed to system.out, Default = DEBUG
        :stream_format: str
            Format of the logging output for system.out.  Can be defined by caller but not recommended
                %(asctime)s [%(levelname)s] [%(name)s] [%(thread)d-%(module)s-%(funcName)s] %(message)s
        : log_file: str
            File path including the file name to write logs to. Default = None
        :file_level: str
            The logging level type to write to the log file.  Default = DEBUG
        :file_format: str
            Format of the logging output for log file. Can be defined by caller but not recommended
                %(asctime)s [%(levelname)s] [%(name)s] [%(thread)d-%(module)s-%(funcName)s] %(message)s

        Creates a new instance of python logging with the name of either variable passed in the name
        argument of the calling module.

        Created to give more detail during the development process for each message sent to logging.

        Sample output (Lines are returned for line length return character is not in message):
        04-01-2020 10:30:09 [CRITICAL] [test_development_logging_without_name]
            [12504-test_logging-test_development_logging_without_name] Test Critical
        04-01-2020 10:30:09 [WARNING] [test_development_logging_without_name]
            [12504-test_logging-test_development_logging_without_name] Test Warning

    ::Notes::
    Configuration of the logging format for both file and system out can be defined by caller but is recommended.
    Date time format is not changeable by a caller.

    ::Formatting Values::
        %(name)s            Name of the custom_logger (logging channel)
        %(levelno)s         Numeric logging level for the message (DEBUG, INFO,
                            WARNING, ERROR, CRITICAL)
        %(levelname)s       Text logging level for the message ("DEBUG", "INFO",
                            "WARNING", "ERROR", "CRITICAL")
        %(pathname)s        Full pathname of the source file where the logging
                            call was issued (if available)
        %(filename)s        Filename portion of pathname
        %(module)s          Module (name portion of filename)
        %(lineno)d          Source line number where the logging call was issued
                            (if available)
        %(funcName)s        Function name
        %(created)f         Time when the LogRecord was created (time.time()
                            return value)
        %(asctime)s         Textual time when the LogRecord was created
        %(msecs)d           Millisecond portion of the creation time
        %(relativeCreated)d Time in milliseconds when the LogRecord was created,
                            relative to the time the logging module was loaded
                            (typically at application startup time)
        %(thread)d          Thread ID (if available)
        %(threadName)s      Thread name (if available)
        %(process)d         Process ID (if available)
        %(message)s         The result of record.getMessage(), computed just as the record is emitted
    """

    date_format = '%m-%d-%Y %H:%M:%S'
    _custom_levels = None
    _logging = None
    _format = None
    _kwargs = None
    _configuration = None

    def __init__(self, **kwargs) -> None:
        """
        Initialize the class, takes in kwargs assigning to the class variable.
        :name : str
            This is the logging module or name of class initializing the logging.
        :configuration: str
            Allows caller to pass in configuration file.
            ::Notes::
                If configuration is set overwrites other arguments
        :sys_out: bool
            Defines if logging should be written to system.out.  Default = True
        :system_level: str
            The logging level type to set what messages will be displayed to system.out, Default = DEBUG
        :stream_format: str
            Format of the logging output for system.out.  Can be defined by caller but not recommended
                %(asctime)s [-%(levelname)s-] [%(name)s] %(message)s
        : log_file: str
            File path including the file name to write logs to. Default = None
        :file_level: str
            The logging level type to write to the log file.  Default = DEBUG
        :file_format: str
            Format of the logging output for log file. Can be defined by caller but not recommended
                %(asctime)s [-%(levelname)s-] [%(name)s] %(message)s

        ::Sample output::
        04-01-2020 10:30:09 [WARNING] [test_default_logging_without_name] Test Warning
        04-01-2020 10:30:09 [ERROR] [test_default_logging_without_name] Test Exception

        ::Notes::
        This is not intended as the entry point for class.  Instead leverage the class methods:
            logging
            development_logging
        """
        self._kwargs = kwargs
        self._initialize_custom_levels()
        config = self._has_configuration_value()
        self._set_logging()
        super.__init__()
        if not config:
            self._set_stream_handler()
            self._set_file_handler()

    @classmethod
    def log(cls, **kwargs) -> logging:
        """
        Default logging initialization for data lake functionality.
        :name : str
            This is the logging module or name of class initializing the logging.
        :configuration: str
            Allows caller to pass in configuration file.
            ::Notes::
                If configuration is set overwrites other arguments
        :sys_out: bool
            Defines if logging should be written to system.out.  Default = True
        :system_level: str
            The logging level type to set what messages will be displayed to system.out, Default = DEBUG
        :stream_format: str
            Format of the logging output for system.out.  Can be defined by caller but not recommended
                %(asctime)s [%(levelname)s] [%(name)s] [%(thread)d-%(module)s-%(funcName)s] %(message)s
        : log_file: str
            File path including the file name to write logs to. Default = None
        :file_level: str
            The logging level type to write to the log file.  Default = DEBUG
        :file_format: str
            Format of the logging output for log file. Can be defined by caller but not recommended
                %(asctime)s [%(levelname)s] [%(name)s] [%(thread)d-%(module)s-%(funcName)s] %(message)s

        :return: logging

        :: Notes::
        Will write to system.out by default logging to file is not enabled by default
        kwargs added for future support of other logging configuration settings
        """
        default_format = "%(asctime)s [-%(levelname)s-] [%(name)s] %(message)s"
        if not kwargs.get("stream_format", None):
            kwargs["stream_format"] = default_format
        if not kwargs.get("file_format", None):
            kwargs["file_format"] = default_format
        log = CustomLogger(**kwargs)
        return log.logging

    @classmethod
    def dev_log(cls, **kwargs) -> logging:
        """
        Logging utility created to give the initializer more contextual information about where the logs are
        from.  This would usually be used for development where the thread, module and function name information
        will be helpful.

        :name : str
            This is the logging module or name of class initializing the logging.
        :configuration: str
            Allows caller to pass in configuration file.
            ::Notes::
                If configuration is set overwrites other arguments
        :sys_out: bool
            Defines if logging should be written to system.out.  Default = True
        :system_level: str
            The logging level type to set what messages will be displayed to system.out, Default = DEBUG
        :stream_format: str
            Format of the logging output for system.out.  Can be defined by caller but not recommended
                %(asctime)s [%(levelname)s] [%(name)s] [%(thread)d-%(module)s-%(funcName)s] %(message)s
        : log_file: str
            File path including the file name to write logs to. Default = None
        :file_level: str
            The logging level type to write to the log file.  Default = DEBUG
        :file_format: str
            Format of the logging output for log file. Can be defined by caller but not recommended
                %(asctime)s [%(levelname)s] [%(name)s] [%(thread)d-%(module)s-%(funcName)s] %(message)s

        :return logging

        :: Notes::
        Will write to system.out by default logging to file is not enabled by default
        kwargs added for future support of other logging configuration settings
        """
        default_format = "%(asctime)s [%(levelname)s] [%(name)s] [%(thread)d-%(module)s-%(funcName)s] %(message)s"
        if not kwargs.get("stream_format", None):
            kwargs["stream_format"] = default_format
        if not kwargs.get("file_format", None):
            kwargs["file_format"] = default_format
        log = CustomLogger(**kwargs)
        return log.logging

    @property
    def logging(self):
        return self._logging

    def exception(self, msg, *args, exc_info=True, **kwargs):
        """
        Log a message with severity 'ERROR' on the root logger, with exception
        information. If the logger has no handlers, basicConfig() is called to add
        a console handler with a pre-defined format.
        """
        self._logging.exception()


    def _set_logging(self) -> None:
        """
        Sets the logging object based of the file name, if file name is not defined leverages stack
        inspect to determine the caller module
        :return: None
        """
        name = self._kwargs.get("name", None)
        if name:
            self._logging = logging.getLogger(name)
        else:
            name = inspect.stack()[1][3]
            self._logging = logging.getLogger(name)

    def _set_level(self, name="DEBUG") -> int:
        """
        Takes in a logging level name, searches for that value in either custom levels or default levels and gets the
        INT value for that logging name.

        If name does not exist then will return 10, value for DEBUG.

        :param name: string value to search for
        :return: None

        ::Notes::
        Used to support both system out and file out having different logging levels.
        """
        _level = 10
        _d_levels = {"DEBUG": 10, "INFO": 20, "WARNING": 30,
                     "ERROR": 40, "CRITICAL": 50}

        _d_levels.update(self._custom_levels.keys())
        if name:
            if name.upper() in _d_levels.keys():
                _level = _d_levels.get(name.upper())

        return _level

    def _initialize_custom_levels(self) -> None:
        """
        Created as the logical process for adding custom logging levels.
        :return: None

        :: Notes::
        Function is created as a place holder for future enhancements not currently utilized
        """
        self._custom_levels = dict()

    def _set_stream_handler(self) -> None:
        """
        Adds the streaming handler to _logging object if stream_format key has value in class variable kwargs.
        :return: None
        """
        _std_out = self._kwargs.get("std_out", True)
        _format = self._kwargs.get("stream_format", None)
        _level = self._set_level(name=self._kwargs.get("system_level", None))
        if _format and _std_out:
            sh = logging.StreamHandler()
            formatter = logging.Formatter(_format, datefmt=self.date_format)
            sh.setFormatter(formatter)
            sh.setLevel(_level)
            self._logging.addHandler(sh)

    def _set_file_handler(self) -> None:
        """
        Adds the file handler to the logging object.  Will add the handler if file log_file is
        set.  If log_file is set then message formats will be formatted using the file_format value
        :return: None
        """
        _file_path = self._kwargs.get("log_file", None)
        _format = self._kwargs.get("file_format", None)
        _level = self._set_level(name=self._kwargs.get("file_level", None))
        if _file_path:
            directory, _ = os.path.split(_file_path)
            self._validate_path_exist(file_path=directory)
            fh = logging.FileHandler(_file_path)
            formatter = logging.Formatter(_format, datefmt=self.date_format)
            fh.setFormatter(formatter)
            fh.setLevel(_level)
            self._logging.addHandler(fh)

    def _has_configuration_value(self) -> bool:
        """
        If configuration argument is set.  Then will enable logging from the configuration file.
        :return: bool
        """
        f_name = self._kwargs.get("configuration", None)
        if f_name:
            logging.config.fileConfig(f_name, disable_existing_loggers=False)
            return True
        else:
            return False

    @staticmethod
    def _validate_path_exist(file_path):
        """
        Created to validate that a directory exist and is writable for the log file to be written into.
        :param file_path: path to create
        :return: None

        ::Notes::
        Unit testing for some functionality of this code is not available because leverages linux commands
        """
        try:
            # -----------------------------------------------
            # Create directory using either subprocess or make dirs subprocess will fail on Windows
            # -----------------------------------------------
            if not os.path.exists(file_path):
                try:
                    os.makedirs(file_path)
                except Exception as a:
                    print("Failed to use make dirs, running sudo mkdir command, error {}".format(a))
                    cmd = "sudo mkdir -p -m 777 {}".format(file_path)
                    subprocess.Popen(cmd, shell=True)

            if not os.path.exists(file_path):
                raise AssertionError("{} failed to be created".format(file_path))

            # -----------------------------------------------
            # Test if file is writeable, if not changes permission
            # -----------------------------------------------
            if not os.access(file_path, os.W_OK):
                file_cmd = "sudo chmod -R 777 {}".format(file_path)
                subprocess.check_call(file_cmd, shell=True)

            if not os.access(file_path, os.W_OK):
                raise LoggerException(f"{file_path} is not writable")

            print(f"{file_path} exist and is writeable")

        except AssertionError as asert_error:
            raise LoggerException(f"Raised an assertion error {asert_error}")

        except Exception as e:
            raise LoggerException(f"Failed to create directory error {e}")
