#!/usr/bin/env python3
"""
QC SMS BLASTER v4
Automated batch SMS Blaster CLI tool for Quezon City Services SMS API.
Supports automatic recipient chunking, configurable batch sizes, real-time progress,
and end-of-blast summary reporting.
"""

import sys
import os
import time
import argparse
from typing import Optional, List

from phone_utils import ExtractionResult, chunk_recipients
from excel_processor import load_excel_numbers
from sms_client import send_sms_blast, build_payload, DEFAULT_COOKIE
from ui_reporter import (
    print_banner,
    print_test_banner,
    print_prod_banner,
    print_extraction_summary,
    print_payload_preview,
    print_sql_hint,
    print_batch_plan,
    print_batch_progress,
    print_batch_total_summary,
    G, Y, R, W, B, C, M, BOLD
)

# Default Test Receivers fallback if in TEST mode
DEFAULT_TEST_RECEIVERS = "09676775035,09172711188,09691821832,09989609017,09154838444,09985713193,09655569756,09052665419,09154839882,09153093518,09494385108,09763394168"
DEFAULT_BATCH_SIZE = 200
DEFAULT_DELAY_SECONDS = 2.0

def parse_args():
    parser = argparse.ArgumentParser(description="QC SMS Blaster v4 - Automated bulk SMS via QCEServices API")
    parser.add_argument("--excel", type=str, default="1.xlsx", help="Path to Excel file (default: 1.xlsx)")
    parser.add_argument("--col", default=6, help="Excel column index (1-based, default 6) or header name")
    parser.add_argument("--sheet", default=0, help="Excel sheet index or sheet name (default: 0)")
    parser.add_argument("--msg", type=str, default="msg.txt", help="Path to message text file (default: msg.txt)")
    parser.add_argument("--mode", choices=["1", "2", "test", "prod"], help="Execution mode: 1/test or 2/prod")
    parser.add_argument("--test-receivers", type=str, default=DEFAULT_TEST_RECEIVERS, help="Comma-separated test phone numbers")
    parser.add_argument("--batch-size", "-b", type=int, default=None, help=f"Number of recipients per request batch (default: {DEFAULT_BATCH_SIZE})")
    parser.add_argument("--delay", "-d", type=float, default=DEFAULT_DELAY_SECONDS, help=f"Delay in seconds between batch requests (default: {DEFAULT_DELAY_SECONDS})")
    parser.add_argument("--dry-run", action="store_true", help="Simulate payload and statistics without calling the live API")
    parser.add_argument("--yes", "-y", action="store_true", help="Auto-confirm execution prompt")
    return parser.parse_args()

def read_message_file(msg_file_path: str) -> str:
    if not os.path.exists(msg_file_path):
        print(f"{R}{BOLD}[!] Error: Message file '{msg_file_path}' not found!{W}")
        sys.exit(1)
    
    print(f"{G}[~] Message File Path: {C}{msg_file_path}{W}")
    print(f"{G}[~] Please wait while processing... \n{W}")

    with open(msg_file_path, "r", encoding="utf-8") as f:
        msg = f.read()
    
    return msg

def get_batch_size(cli_batch_size: Optional[int], total_recipients: int, auto_yes: bool = False) -> int:
    if cli_batch_size is not None and cli_batch_size > 0:
        if cli_batch_size > DEFAULT_BATCH_SIZE:
            print(f"{Y}[!] Warning: Batch size ({cli_batch_size}) exceeds recommended {DEFAULT_BATCH_SIZE}. Batches > 200 may exceed the 1-minute API timeout and trigger false errors.{W}")
        return cli_batch_size

    if auto_yes:
        return DEFAULT_BATCH_SIZE

    try:
        print(f"{C}[i] Recommended batch size is {DEFAULT_BATCH_SIZE} recipients.{W}")
        print(f"{Y}[!] Note: The API timeout is set to 1 minute. Batches larger than 200 recipients may exceed this limit, causing the API to return a false error.{W}")
        print(f"{C}[i] Press [Enter] to use the recommended value ({DEFAULT_BATCH_SIZE}).{W}")
        raw_input = input(
            f"{G}[~] Enter batch size (recipients per request) [Press Enter for {DEFAULT_BATCH_SIZE}]: {Y}"
        ).strip()
        print(W, end="")
        if not raw_input:
            return DEFAULT_BATCH_SIZE
        if raw_input.lower() in ("all", "0"):
            chosen = total_recipients if total_recipients > 0 else DEFAULT_BATCH_SIZE
            if chosen > DEFAULT_BATCH_SIZE:
                print(f"{Y}[!] Warning: Sending all {chosen} recipients in 1 batch exceeds 200 and may trigger a 1-minute API timeout.{W}")
            return chosen
        parsed = int(raw_input)
        if parsed <= 0:
            print(f"{Y}[!] Invalid batch size '{raw_input}'. Using default {DEFAULT_BATCH_SIZE}.{W}")
            return DEFAULT_BATCH_SIZE
        if parsed > DEFAULT_BATCH_SIZE:
            print(f"{Y}[!] Warning: Batch size ({parsed}) exceeds recommended {DEFAULT_BATCH_SIZE}. Risk of 1-minute API timeout.{W}")
        return parsed
    except ValueError:
        print(f"{Y}[!] Invalid input. Using default batch size {DEFAULT_BATCH_SIZE}.{W}")
        return DEFAULT_BATCH_SIZE
    except KeyboardInterrupt:
        print(f"\n{G}[!] Goodbye!!!{W}")
        sys.exit(0)

def main():
    args = parse_args()
    print_banner()

    # Determine Excel column identifier type (int or str)
    col_ident = args.col
    if isinstance(col_ident, str) and col_ident.isdigit():
        col_ident = int(col_ident)

    print(f"{R}{BOLD}[!] IMPORTANT NOTES!!!!:\n Always double check your EXCEL FILE\n and make sure that it is correct.\n Make sure that the Contact Numbers column is correct.{W}\n")
    print(f"{G}[~] Excel File Path: {C}{args.excel}{W}")
    print(f"{G}[~] Please wait while processing... \n{W}")

    # Load and process Excel phone numbers
    try:
        extraction_result = load_excel_numbers(
            file_path=args.excel,
            col_identifier=col_ident,
            sheet_name=args.sheet
        )
    except Exception as e:
        print(f"{R}{BOLD}[!] ERROR reading Excel file: {e}{W}")
        sys.exit(1)

    # Output stats
    print_extraction_summary(extraction_result)

    # Read SMS message text
    msg_text = read_message_file(args.msg)
    print(f"{C}{BOLD}--- MESSAGE PREVIEW ---{W}\n{Y}{msg_text}{W}\n{C}{BOLD}-----------------------{W}\n")

    # Mode selection
    mode = args.mode
    if not mode:
        try:
            mode = input(f"{G}[~] {BOLD}[1]TEST OR [2]PROD? (choose 1 or 2): {Y}").strip()
            print(W, end="")
        except KeyboardInterrupt:
            print(f"\n{G}[!] Goodbye!!!{W}")
            sys.exit(0)

    if mode in ("1", "test"):
        print_test_banner()
        receivers_list = [r.strip() for r in args.test_receivers.split(",") if r.strip()]
        mode_label = "TEST"
    elif mode in ("2", "prod"):
        print_prod_banner()
        receivers_list = extraction_result.mobile_numbers
        mode_label = "PROD"
    else:
        print(f"{G}[!] Nothing happened!, Goodbye!!!{W}")
        sys.exit(0)

    if not receivers_list:
        print(f"{R}{BOLD}[!] ERROR: Receiver phone number list is empty! Cannot proceed.{W}")
        sys.exit(1)

    total_targets = len(receivers_list)

    # Determine batch size
    batch_size = get_batch_size(args.batch_size, total_targets, auto_yes=args.yes)
    batches = chunk_recipients(receivers_list, batch_size)
    total_batches = len(batches)

    # Display batch plan
    print_batch_plan(batch_size, total_batches, total_targets, args.delay)

    # Build payload preview using the first batch
    batch_1_receivers_str = ",".join(batches[0])
    payload_preview = send_sms_blast(msg_text, batch_1_receivers_str, dry_run=True)["payload"]
    headers = {"Content-Type": "application/json", "Cookie": DEFAULT_COOKIE}

    print_payload_preview(payload_preview, headers)

    if args.dry_run:
        print(f"{G}{BOLD}[DRY-RUN MODE] Simulating execution of {total_batches} batch(es) for {total_targets} recipient(s)...{W}\n")
        successful_batches = 0
        total_sent = 0
        for idx, batch in enumerate(batches, start=1):
            start_idx = (idx - 1) * batch_size + 1
            end_idx = start_idx + len(batch) - 1
            print_batch_progress(idx, total_batches, len(batch), start_idx, end_idx, total_targets)
            resp = send_sms_blast(msg_text, ",".join(batch), dry_run=True)
            print(f"{G}{BOLD}[~] SERVER RESPONSE (DRY-RUN):{W}")
            print(f"{G}{resp['response_text']}{W}\n")
            successful_batches += 1
            total_sent += len(batch)

        print_batch_total_summary(total_batches, successful_batches, 0, total_sent, total_targets)
        print_sql_hint(str(total_targets))
        print_extraction_summary(extraction_result)
        sys.exit(0)

    print(f"{R}{BOLD}\n[!] WARNING!!!:\n Please double check the PAYLOAD and HEADERS above before sending...{W}")

    if args.yes:
        confirm = "y"
    else:
        try:
            confirm = input(
                f"{G}\n[?] The message above will be sent in {BOLD}{total_batches}{W}{G} batch(es) to {BOLD}{total_targets}{W}{G} receivers ({C}{mode_label}{W}{G} mode).\n Are you sure do you want to send it now? [y/N]: {W}"
            ).strip()
        except KeyboardInterrupt:
            print(f"\n{G}[!] Goodbye!!!{W}")
            sys.exit(0)

    if confirm.lower() == "y":
        print(f"{G}\n[~] Sandman SMS BLAST v4 is now sending the MESSAGE to all receivers in batches.. ")
        print(f"{Y}[!] Processing {total_batches} batch(es). Please wait while sending...\n{W}")

        successful_batches = 0
        failed_batches = 0
        total_recipients_sent = 0
        failed_batches_info = []

        for idx, batch in enumerate(batches, start=1):
            batch_receivers_str = ",".join(batch)
            start_idx = (idx - 1) * batch_size + 1
            end_idx = start_idx + len(batch) - 1

            print_batch_progress(idx, total_batches, len(batch), start_idx, end_idx, total_targets)
            print(f"{Y}[~] Dispatching batch {idx}/{total_batches}...{W}")

            response_data = send_sms_blast(msg_text, batch_receivers_str, dry_run=False)

            if response_data["success"]:
                successful_batches += 1
                total_recipients_sent += len(batch)
                print(f"{G}{BOLD}[~] SERVER RESPONSE:{W}")
                print(f"{G}{response_data['response_text']}{W}\n")
            else:
                failed_batches += 1
                error_snippet = response_data['response_text'][:150]
                print(f"{R}{BOLD}[!] SERVER RESPONSE ({response_data['status_code']}):{W}")
                print(f"{R}{response_data['response_text']}{W}\n")
                failed_batches_info.append({
                    "batch_num": idx,
                    "error": f"Status {response_data['status_code']}: {error_snippet}"
                })

            # Wait before sending the next batch if there are remaining batches and delay > 0
            if idx < total_batches and args.delay > 0:
                print(f"{C}[~] Waiting {args.delay:.1f}s before sending next batch...{W}\n")
                time.sleep(args.delay)

        # End of all batches: summarize total, show SQL query hint, and print extraction summary
        print_batch_total_summary(
            total_batches=total_batches,
            successful_batches=successful_batches,
            failed_batches=failed_batches,
            total_recipients_sent=total_recipients_sent,
            total_recipients_target=total_targets,
            failed_batches_info=failed_batches_info
        )
        print_sql_hint(str(total_targets))
        print_extraction_summary(extraction_result)

    else:
        print(f"{G}[!] Nothing happened. Goodbye!!!{W}")
        sys.exit(0)

if __name__ == "__main__":
    main()
