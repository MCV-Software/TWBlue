from mysc.memory_utils import MemoryUsage, ProcessUsage, format_memory_usage, get_process_usage


def test_format_memory_usage_includes_all_available_counters():
    usage = MemoryUsage(rss=2 * 1024**2, vms=3 * 1024**2, private=1024**2)

    assert format_memory_usage(usage) == "RSS: 2.00 MiB, VMS: 3.00 MiB, Private: 1.00 MiB"


def test_format_memory_usage_omits_private_when_unavailable():
    usage = MemoryUsage(rss=2 * 1024**2, vms=3 * 1024**2)

    assert format_memory_usage(usage) == "RSS: 2.00 MiB, VMS: 3.00 MiB"


def test_process_usage_keeps_memory_cpu_and_thread_counters_together():
    memory = MemoryUsage(rss=2 * 1024**2, vms=3 * 1024**2)
    usage = ProcessUsage(memory=memory, cpu_percent=12.5, threads=8)

    assert usage.memory is memory
    assert usage.cpu_percent == 12.5
    assert usage.threads == 8


def test_get_process_usage_collects_cpu_threads_and_memory_from_process():
    class FakeProcess:
        def memory_info(self):
            return type("MemoryInfo", (), {"rss": 2 * 1024**2, "vms": 3 * 1024**2})()

        def memory_full_info(self):
            return type("FullMemoryInfo", (), {"uss": 1024**2})()

        def cpu_percent(self, interval):
            assert interval is None
            return 12.5

        def num_threads(self):
            return 8

    usage = get_process_usage(FakeProcess())

    assert usage == ProcessUsage(
        memory=MemoryUsage(rss=2 * 1024**2, vms=3 * 1024**2, private=1024**2),
        cpu_percent=12.5,
        threads=8,
    )
