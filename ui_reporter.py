import sys
from typing import Dict, Any, List, Optional
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
            "[bold cyan]Sandman SMS BLAST v4[/bold cyan]\n[bold yellow]# Coded By Andrew Ubag - Automated Batching v4[/bold yellow]",
            title="[bold green]QC SMS BLASTER[/bold green]",
            border_style="cyan",
            expand=False
        ))
    else:
        print(f"{C}{BOLD}====================================================\n               {G}Sandman SMS BLAST v4{C}\n       {Y}# Coded By Andrew Ubag - Automated Batching v4{C}\n===================================================={W}")

def print_test_banner():
    if USE_RICH:
        console.print(Panel(
            "[bold yellow]*** NO LIVE PRODUCTION SMS WILL BE SENT ***[/bold yellow]\n[bold cyan]# Sandman SMS BLAST v4 - TEST MODE[/bold cyan]",
            title="[bold yellow]TEST MODE ONLY[/bold yellow]",
            border_style="yellow",
            expand=False
        ))
    else:
        print(f"{Y}{BOLD}====================================================\n                [ TEST MODE ONLY ]\n   *** NO LIVE PRODUCTION SMS WILL BE SENT ***\n===================================================={W}\n{C}{BOLD}                # Sandman SMS BLAST v4 - TEST MODE{W}")

def print_prod_banner():
    if USE_RICH:
        console.print(Panel(
            "[bold red]*** LIVE SMS WILL BE SENT TO REAL RECEIVERS ***[/bold red]\n[bold red]# Sandman SMS BLAST v4 - PRODUCTION MODE[/bold red]",
            title="[bold red]PRODUCTION MODE ACTIVE[/bold red]",
            border_style="red",
            expand=False
        ))
    else:
        print(f"{R}{BOLD}====================================================\n             [ PRODUCTION MODE ACTIVE ]\n   *** LIVE SMS WILL BE SENT TO REAL RECEIVERS ***\n===================================================={W}\n{R}{BOLD}             # Sandman SMS BLAST v4 - PRODUCTION MODE{W}")

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

def print_batch_plan(batch_size: int, total_batches: int, total_recipients: int, delay_seconds: float):
    if USE_RICH:
        table = Table(title="Batch Execution Plan", border_style="cyan", header_style="bold magenta")
        table.add_column("Parameter", style="bold white")
        table.add_column("Value", justify="right")
        table.add_row("Total Recipients", f"[bold green]{total_recipients}[/bold green]")
        table.add_row("Batch Size", f"[bold cyan]{batch_size}[/bold cyan]")
        table.add_row("Total Batches", f"[bold yellow]{total_batches}[/bold yellow]")
        table.add_row("Inter-Batch Delay", f"{delay_seconds:.1f}s")
        console.print(table)
        console.print()
    else:
        print(f"{C}{BOLD}--- BATCH EXECUTION PLAN ---{W}")
        print(f"  Total Recipients:  {G}{BOLD}{total_recipients}{W}")
        print(f"  Batch Size:        {C}{BOLD}{batch_size}{W}")
        print(f"  Total Batches:     {Y}{BOLD}{total_batches}{W}")
        print(f"  Inter-Batch Delay: {W}{delay_seconds:.1f}s")
        print(f"{C}{BOLD}----------------------------{W}\n")

def print_batch_progress(batch_num: int, total_batches: int, batch_count: int, start_idx: int, end_idx: int, total_recipients: int):
    if USE_RICH:
        console.print(f"[bold cyan]>>> [Batch {batch_num}/{total_batches}][/bold cyan] Sending [bold green]{batch_count}[/bold green] recipient(s) (indices [yellow]{start_idx}-{end_idx}[/yellow] of [bold white]{total_recipients}[/bold white])...")
    else:
        print(f"{C}{BOLD}>>> [Batch {batch_num}/{total_batches}]{W} Sending {G}{BOLD}{batch_count}{W} recipient(s) (indices {Y}{start_idx}-{end_idx}{W} of {total_recipients})...")

def print_batch_total_summary(
    total_batches: int,
    successful_batches: int,
    failed_batches: int,
    total_recipients_sent: int,
    total_recipients_target: int,
    failed_batches_info: Optional[List[Dict[str, Any]]] = None
):
    if USE_RICH:
        table = Table(title="Batch Execution Summary", border_style="green" if failed_batches == 0 else "red", header_style="bold magenta")
        table.add_column("Metric", style="bold white")
        table.add_column("Result", justify="right")
        
        status_text = "[bold green]ALL BATCHES SENT SUCCESSFULLY[/bold green]" if failed_batches == 0 else "[bold red]COMPLETED WITH ERRORS[/bold red]"
        table.add_row("Overall Status", status_text)
        table.add_row("Total Batches Processed", f"{total_batches}")
        table.add_row("Successful Batches", f"[bold green]{successful_batches}[/bold green]")
        table.add_row("Failed Batches", f"[bold red]{failed_batches}[/bold red]" if failed_batches > 0 else f"[green]0[/green]")
        table.add_row("Total SMS Sent", f"[bold green]{total_recipients_sent}[/bold green] / {total_recipients_target}")
        
        console.print(table)
        if failed_batches_info:
            console.print(f"[bold red]Failed Batches Detail:[/bold red]")
            for item in failed_batches_info:
                console.print(f"  [red]• Batch {item.get('batch_num')}: {item.get('error')}[/red]")
        console.print()
    else:
        print(f"\n{C}{BOLD}====================================================\n             BATCH EXECUTION SUMMARY\n===================================================={W}")
        if failed_batches == 0:
            print(f"  Overall Status:        {G}{BOLD}ALL BATCHES SENT SUCCESSFULLY{W}")
        else:
            print(f"  Overall Status:        {R}{BOLD}COMPLETED WITH ERRORS{W}")
        print(f"  Total Batches:         {total_batches}")
        print(f"  Successful Batches:    {G}{successful_batches}{W}")
        print(f"  Failed Batches:        {R if failed_batches > 0 else G}{failed_batches}{W}")
        print(f"  Total SMS Sent:        {G}{BOLD}{total_recipients_sent}{W} / {total_recipients_target}")
        if failed_batches_info:
            print(f"  {R}Failed Batches Detail:{W}")
            for item in failed_batches_info:
                print(f"    {R}• Batch {item.get('batch_num')}: {item.get('error')}{W}")
        print(f"{C}{BOLD}===================================================={W}\n")
