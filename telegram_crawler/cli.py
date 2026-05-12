import argparse
import asyncio
import logging
from datetime import datetime

from rich.console import Console
from rich.table import Table

from telegram_crawler.client import login
from telegram_crawler.config import ensure_dirs, get_log_dir, get_log_level
from telegram_crawler.crawler import crawl_channel
from telegram_crawler.exporter import export_csv, export_json
from telegram_crawler.storage import Storage

console = Console()


def parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")


async def cmd_login(args: argparse.Namespace) -> None:
    await login()


async def cmd_crawl(args: argparse.Namespace) -> None:
    storage = Storage()
    await storage.init_db()

    date_from = parse_date(args.from_date) if args.from_date else None
    date_to = parse_date(args.to_date) if args.to_date else None

    total = 0
    for channel in args.channels:
        count = await crawl_channel(
            channel_username=channel,
            storage=storage,
            date_from=date_from,
            date_to=date_to,
        )
        total += count

    console.print(f"\n[bold green]Total: {total:,} messages crawled[/]")
    await storage.close()


async def cmd_export(args: argparse.Namespace) -> None:
    storage = Storage()
    await storage.init_db()

    channel = await storage.get_channel_by_username(args.channel)
    if not channel:
        console.print(f"[red]Channel '{args.channel}' not found. Crawl it first.[/]")
        await storage.close()
        return

    from pathlib import Path
    output = Path(args.output) if args.output else Path(f"{args.channel}.{args.format}")

    if args.format == "csv":
        await export_csv(channel.id, storage, output)
    else:
        await export_json(channel.id, storage, output)

    await storage.close()


async def cmd_list(args: argparse.Namespace) -> None:
    storage = Storage()
    await storage.init_db()

    channels = await storage.list_channels()
    if not channels:
        console.print("[yellow]No channels crawled yet.[/]")
        await storage.close()
        return

    table = Table(title="Crawled Channels")
    table.add_column("Username", style="cyan")
    table.add_column("Title")
    table.add_column("Messages", justify="right")
    table.add_column("Last Crawled")

    for ch in channels:
        count = await storage.get_message_count(ch.id)
        table.add_row(ch.username, ch.title, f"{count:,}", str(ch.updated_at))

    console.print(table)
    await storage.close()


async def cmd_stats(args: argparse.Namespace) -> None:
    storage = Storage()
    await storage.init_db()

    channel = await storage.get_channel_by_username(args.channel)
    if not channel:
        console.print(f"[red]Channel '{args.channel}' not found.[/]")
        await storage.close()
        return

    stats = await storage.get_stats(channel.id)
    console.print(f"\n[bold]Stats for {args.channel}[/]")
    console.print(f"  Messages:    {stats['message_count']:,}")
    console.print(f"  Reactions:   {stats['reaction_count']:,}")
    console.print(f"  Earliest:    {stats['earliest_date']}")
    console.print(f"  Latest:      {stats['latest_date']}")

    await storage.close()


def _setup_logging() -> None:
    ensure_dirs()
    log_dir = get_log_dir()
    log_level = get_log_level()
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"telegram-crawler-{today}.log"

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def main() -> None:
    _setup_logging()
    parser = argparse.ArgumentParser(prog="telegram-crawler", description="Crawl public Telegram channels")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # login
    subparsers.add_parser("login", help="Authenticate with Telegram")

    # crawl
    crawl_parser = subparsers.add_parser("crawl", help="Crawl messages from channels")
    crawl_parser.add_argument("channels", nargs="+", help="Channel usernames")
    crawl_parser.add_argument("--from", dest="from_date", help="Start date (YYYY-MM-DD)")
    crawl_parser.add_argument("--to", dest="to_date", help="End date (YYYY-MM-DD)")

    # export
    export_parser = subparsers.add_parser("export", help="Export channel data")
    export_parser.add_argument("channel", help="Channel username")
    export_parser.add_argument("--format", choices=["csv", "json"], default="csv")
    export_parser.add_argument("--output", "-o", help="Output file path")

    # list
    subparsers.add_parser("list", help="List crawled channels")

    # stats
    stats_parser = subparsers.add_parser("stats", help="Show channel statistics")
    stats_parser.add_argument("channel", help="Channel username")

    args = parser.parse_args()

    commands = {
        "login": cmd_login,
        "crawl": cmd_crawl,
        "export": cmd_export,
        "list": cmd_list,
        "stats": cmd_stats,
    }

    try:
        asyncio.run(commands[args.command](args))
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/]")


if __name__ == "__main__":
    main()