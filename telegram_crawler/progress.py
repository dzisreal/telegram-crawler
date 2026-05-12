import time

from rich.console import Console

console = Console()


class ProgressReporter:
    def __init__(self, channel_name: str) -> None:
        self.channel_name = channel_name
        self.count = 0
        self.start_time = time.monotonic()

    def update(self, batch_count: int) -> None:
        self.count += batch_count
        elapsed = time.monotonic() - self.start_time
        rate = self.count / elapsed if elapsed > 0 else 0
        console.print(
            f"  [{self.channel_name}] {self.count:,} messages "
            f"| {rate:.0f} msg/s | {elapsed:.1f}s elapsed"
        )

    def finish(self) -> None:
        elapsed = time.monotonic() - self.start_time
        rate = self.count / elapsed if elapsed > 0 else 0
        console.print(
            f"[bold green]✓[/] [{self.channel_name}] "
            f"Crawled {self.count:,} messages in {elapsed:.1f}s "
            f"({rate:.0f} msg/s)"
        )

    def start(self) -> None:
        console.print(f"[bold blue]⏳[/] Crawling [cyan]{self.channel_name}[/]...")