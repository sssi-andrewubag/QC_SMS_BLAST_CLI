#!/usr/bin/env python3
"""
QC SMS BLASTER v3
Refactored, modular SMS Blaster CLI tool for Quezon City Services SMS API.
"""

import sys
import os
import argparse
from typing import Optional

from phone_utils import ExtractionResult
from excel_processor import load_excel_numbers
from sms_client import send_sms_blast, build_payload, DEFAULT_COOKIE
from ui_reporter import (
    print_banner,
    print_test_banner,
    print_prod_banner,
    print_extraction_summary,
    print_payload_preview,
    print_sql_hint,
    G, Y, R, W, B, C, M, BOLD
)

# Default Test Receivers fallback if in TEST mode
DEFAULT_TEST_RECEIVERS = "09676775035,09691821832,09989609017,09154838444,09985713193,09655569756,09052665419,09154839882,09153093518,09494385108,09763394168"

def parse_args():
    parser = argparse.ArgumentParser(description="QC SMS Blaster v3 - Send bulk SMS via QCEServices API")
    parser.add_argument("--excel", type=str, default="1.xlsx", help="Path to Excel file (default: 1.xlsx)")
    parser.add_argument("--col", default=6, help="Excel column index (1-based, default 6) or header name")
    parser.add_argument("--sheet", default=0, help="Excel sheet index or sheet name (default: 0)")
    parser.add_argument("--msg", type=str, default="msg.txt", help="Path to message text file (default: msg.txt)")
    parser.add_argument("--mode", choices=["1", "2", "test", "prod"], help="Execution mode: 1/test or 2/prod")
    parser.add_argument("--test-receivers", type=str, default=DEFAULT_TEST_RECEIVERS, help="Comma-separated test phone numbers")
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
        receivers = args.test_receivers
        limit = "5"
        mode_label = "TEST"
        target_count = len(receivers.split(","))
    elif mode in ("2", "prod"):
        print_prod_banner()
        receivers = extraction_result.joined_mobile_numbers
        limit = str(extraction_result.total_mobile_count)
        mode_label = "PROD"
        target_count = extraction_result.total_mobile_count
    else:
        print(f"{G}[!] Nothing happened!, Goodbye!!!{W}")
        sys.exit(0)

    if not receivers:
        print(f"{R}{BOLD}[!] ERROR: Receiver phone number list is empty! Cannot proceed.{W}")
        sys.exit(1)

    # Build payload preview
    payload_dict = build_payload(msg_text, receivers)
    payload_json = send_sms_blast(msg_text, receivers, dry_run=True)["payload"]
    headers = {"Content-Type": "application/json", "Cookie": DEFAULT_COOKIE}

    print_payload_preview(payload_json, headers)

    if args.dry_run:
        print(f"{G}{BOLD}[DRY-RUN MODE] Payload successfully created. Live call bypassed.{W}\n")
        print_extraction_summary(extraction_result)
        sys.exit(0)

    print(f"{R}{BOLD}\n[!] WARNING!!!:\n Please double check the PAYLOAD and HEADERS above before sending...{W}")
    
    if args.yes:
        confirm = "y"
    else:
        try:
            confirm = input(f"{G}\n[?] The PAYLOAD and HEADERS above\n will be sent to {BOLD}{target_count}{W}{G} receivers ({C}{mode_label}{W}{G} mode).\n Are you sure do you want to send it now? [y/N]: {W}").strip()
        except KeyboardInterrupt:
            print(f"\n{G}[!] Goodbye!!!{W}")
            sys.exit(0)

    if confirm.lower() == "y":
        print(f"{G}\n[~] Sandman SMS BLAST v3 is now sending the MESSAGE to all receivers.. ")
        print(f"{Y}[!] Please wait while sending...\n{W}")

        response_data = send_sms_blast(msg_text, receivers, dry_run=False)

        if response_data["success"]:
            print(f"{G}{BOLD}[~] SERVER RESPONSE:{W}")
            print(f"{G}{response_data['response_text']}{W}\n")
        else:
            print(f"{R}{BOLD}[!] SERVER RESPONSE ({response_data['status_code']}):{W}")
            print(f"{R}{response_data['response_text']}{W}\n")

        print_sql_hint(limit)
        print_extraction_summary(extraction_result)
    else:
        print(f"{G}[!] Nothing happened. Goodbye!!!{W}")
        sys.exit(0)

if __name__ == "__main__":
    main()
