import sys
from typing import Dict, Any
from phone_utils import ExtractionResult

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt
    from rich.text import Text
    USE_RICH = True
    console = Console()
except ImportError:
    USE_RICH = False

# Color constants
G = '\033[92m'
Y = '\033[93m'
B = '\033[94m'
C = '\033[96m'
M = '\033[95m'
R = '\033[91m'
W = '\033[0m'
BOLD = '\033[1m'

def print_banner():
    if USE_RICH:
        console.print(Panel(
            "[bold cyan]Sandman SMS BLAST v3[/bold cyan]\n[bold yellow]# Coded By Andrew Ubag - Refactored v3[/bold yellow]",
            title="[bold green]QC SMS BLASTER[/bold green]",
            border_style="cyan",
            expand=False
        ))
    else:
        print(f"{C}{BOLD}====================================================\n               {G}Sandman SMS BLAST v3{C}\n       {Y}# Coded By Andrew Ubag - Refactored v3{C}\n===================================================={W}")

def print_test_banner():
    if USE_RICH:
        console.print(Panel(
            "[bold yellow]*** NO LIVE PRODUCTION SMS WILL BE SENT ***[/bold yellow]\n[bold cyan]# Sandman SMS BLAST v3 - TEST MODE[/bold cyan]",
            title="[bold yellow]TEST MODE ONLY[/bold yellow]",
            border_style="yellow",
            expand=False
        ))
    else:
        print(f"{Y}{BOLD}====================================================\n                [ TEST MODE ONLY ]\n   *** NO LIVE PRODUCTION SMS WILL BE SENT ***\n===================================================={W}\n{C}{BOLD}                # Sandman SMS BLAST v3 - TEST MODE{W}")

def print_prod_banner():
    if USE_RICH:
        console.print(Panel(
            "[bold red]*** LIVE SMS WILL BE SENT TO REAL RECEIVERS ***[/bold red]\n[bold red]# Sandman SMS BLAST v3 - PRODUCTION MODE[/bold red]",
            title="[bold red]PRODUCTION MODE ACTIVE[/bold red]",
            border_style="red",
            expand=False
        ))
    else:
        print(f"{R}{BOLD}====================================================\n             [ PRODUCTION MODE ACTIVE ]\n   *** LIVE SMS WILL BE SENT TO REAL RECEIVERS ***\n===================================================={W}\n{R}{BOLD}             # Sandman SMS BLAST v3 - PRODUCTION MODE{W}")

def print_extraction_summary(result: ExtractionResult, default_count: int = 0):
    if USE_RICH:
        table = Table(title="Extraction Statistics", border_style="cyan", header_style="bold magenta")
        table.add_column("Metric", style="bold white")
        table.add_column("Count", justify="right")

        table.add_row("#N/A Values", f"[bold red]{result.na_count}[/bold red]" if result.na_count > 0 else f"[green]{result.na_count}[/green]")
        table.add_row("Unknown Contact Numbers", f"[bold red]{len(result.unknown_numbers)}[/bold red]" if result.unknown_numbers else f"[green]0[/green]")
        table.add_row("Telephone Numbers (Landline)", f"[bold yellow]{len(result.tel_numbers)}[/bold yellow]" if result.tel_numbers else f"[green]0[/green]")
        table.add_row("Empty Values", f"[yellow]{result.empty_count}[/yellow]" if result.empty_count > 0 else f"[green]0[/green]")
        if default_count > 0:
            table.add_row("SMS Sent to Default CP", f"[bold green]{default_count}[/bold green]")
        table.add_row("Cellphone Numbers Extracted", f"[bold green]{result.total_mobile_count}[/bold green]")
        table.add_row("TOTAL SMS Targets", f"[bold green]{default_count + result.total_mobile_count}[/bold green]")

        console.print(table)
        if result.unknown_numbers:
            console.print(f"[bold red]Unknown Numbers:[/bold red] {result.unknown_numbers}")
        if result.tel_numbers:
            console.print(f"[bold yellow]Landline Numbers:[/bold yellow] {result.tel_numbers}")
        console.print()
    else:
        print(f"{C}{BOLD}--- EXTRACTION STATISTICS ---{W}")
        na_color = R if result.na_count > 0 else G
        unk_color = R if result.unknown_numbers else G
        tel_color = Y if result.tel_numbers else G
        empty_color = Y if result.empty_count > 0 else G
        print(f"  {na_color}{result.na_count}{W} #N/A Value(s)")
        print(f"  {unk_color}{len(result.unknown_numbers)}{W} Unknown Contact Number(s)")
        if result.unknown_numbers:
            print(f"    {R}-> {result.unknown_numbers}{W}")
        print(f"  {tel_color}{len(result.tel_numbers)}{W} Telephone Number(s)")
        if result.tel_numbers:
            print(f"    {Y}-> {result.tel_numbers}{W}")
        print(f"  {empty_color}{result.empty_count}{W} Empty Value(s)")
        if default_count > 0:
            print(f"  {G}{default_count}{W} SMS Sent to Default CP")
        print(f"  {G}{BOLD}{result.total_mobile_count}{W} Cellphone Number(s) Extracted")
        print(f"  {G}{BOLD}{default_count + result.total_mobile_count}{W} TOTAL SMS Target(s)")
        print(f"{C}{BOLD}----------------------------{W}\n")

def print_payload_preview(payload_json: str, headers: Dict[str, str]):
    if USE_RICH:
        console.print(Panel(payload_json, title="[bold green]Payload Preview[/bold green]", border_style="green", expand=False))
        header_str = "\n".join([f"[yellow]{k}[/yellow]: [cyan]{v}[/cyan]" for k, v in headers.items()])
        console.print(Panel(header_str, title="[bold green]Headers Preview[/bold green]", border_style="green", expand=False))
    else:
        print(f"{G}{BOLD}[~] Please check this PAYLOAD:{W}")
        print(f"{C}{payload_json}{W}")
        print(f"{G}{BOLD}[~] Please check this HEADERS:{W}")
        for k, v in headers.items():
            print(f"  {Y}{k}{W}: {C}{v}{W}")
        print(f"{W}")

def print_sql_hint(limit: str):
    sql = f"SELECT * FROM sms_responses_logs WHERE log_id >= (SELECT log_id FROM sms_responses_logs WHERE smsnumber = '9171591105' AND etimestamp > '2022-08-08') ORDER BY log_id DESC LIMIT {limit};"
    if USE_RICH:
        console.print(Panel(f"[yellow]{sql}[/yellow]\n\n[bold cyan]PROD qceservices | DATABASE qceservices[/bold cyan]", title="[bold green]Log Query Hint[/bold green]", border_style="cyan", expand=False))
    else:
        print(f"{G}[~] You should check the LOGs using this query:{W}")
        print(f"{Y}{sql}{W}")
        print(f"{C}[~] PROD qceservices | DATABASE qceservices{W}")
