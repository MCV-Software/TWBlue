"""Utilities for obtaining a lightweight memory snapshot of TWBlue."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Optional

import psutil

_current_process: Optional[psutil.Process] = None


@dataclass(frozen=True)
class MemoryUsage:
    """Memory counters for a single process, expressed in bytes."""

    rss: int
    """Resident set size (physical RAM currently used by the process)."""

    vms: int
    """Virtual memory size reserved by the process."""

    private: Optional[int] = None
    """Private/unique memory when the operating system exposes it."""


@dataclass(frozen=True)
class ProcessUsage:
    """Runtime resource counters for a single process."""

    memory: MemoryUsage
    cpu_percent: float
    threads: int


def get_memory_usage(process: Optional[psutil.Process] = None) -> MemoryUsage:
    """Return a point-in-time memory snapshot for the current process.

    RSS is the primary value to compare when evaluating TWBlue's RAM footprint.
    Private memory is included when psutil can obtain it; its exact field varies
    by operating system.
    """
    process = process or psutil.Process(os.getpid())
    memory_info = process.memory_info()
    private_memory: Optional[int] = None

    try:
        full_memory_info = process.memory_full_info()
        private_memory = getattr(
            full_memory_info,
            "uss",
            getattr(full_memory_info, "private", None),
        )
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        pass

    return MemoryUsage(
        rss=memory_info.rss,
        vms=memory_info.vms,
        private=private_memory,
    )


def get_process_usage(process: Optional[psutil.Process] = None) -> ProcessUsage:
    """Return memory, CPU usage and thread count for the current process.

    ``cpu_percent`` is non-blocking and measures usage since the previous call
    for the same process. Its first value is expected to be zero.
    """
    global _current_process
    if process is None:
        if _current_process is None or _current_process.pid != os.getpid():
            _current_process = psutil.Process(os.getpid())
        process = _current_process
    return ProcessUsage(
        memory=get_memory_usage(process),
        cpu_percent=process.cpu_percent(interval=None),
        threads=process.num_threads(),
    )


def format_memory_usage(usage: MemoryUsage) -> str:
    """Format a memory snapshot for logs or diagnostics screens."""
    parts = [
        "RSS: {:.2f} MiB".format(usage.rss / 1024**2),
        "VMS: {:.2f} MiB".format(usage.vms / 1024**2),
    ]
    if usage.private is not None:
        parts.append("Private: {:.2f} MiB".format(usage.private / 1024**2))
    return ", ".join(parts)


def log_memory_usage(context: str = "", logger: Optional[logging.Logger] = None) -> MemoryUsage:
    """Capture and log memory usage, returning the snapshot to the caller."""
    usage = get_memory_usage()
    logger = logger or logging.getLogger(__name__)
    prefix = " after {}".format(context) if context else ""
    logger.info("Memory usage%s: %s", prefix, format_memory_usage(usage))
    return usage
