import os
import argparse
from dotenv import load_dotenv
from telethon import TelegramClient, functions, types
from telethon.errors import FloodWaitError, PhoneNumberInvalidError
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.progress import track
from rich.box import HEAVY, ROUNDED
import asyncio
import time

console = Console()

BANNER = """
████████╗███████╗██╗     ███████╗ ██████╗ ██████╗  █████╗ ██████╗    
╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝ ██╔══██╗██╔══██╗██╔══██╗   📱 A Telegram Phone Number Checker v1.0 
   ██║   █████╗  ██║     █████╗  ██║  ███╗██████╔╝███████║██████╔╝      Based on a 2024 Bellingcat tool
   ██║   ██╔══╝  ██║     ██╔══╝  ██║   ██║██╔══██╗██╔══██║██╔══██╗      Modified by @pearswick in 2025 
   ██║   ███████╗███████╗███████╗╚██████╔╝██║  ██║██║  ██║██████╔╝      Check README.md for instructions
   ╚═╝   ╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ 
"""

async def check_number(client, phone_number, debug=False):
    try:
        result = await client(functions.contacts.ImportContactsRequest([
            types.InputPhoneContact(
                client_id=0,
                phone=phone_number,
                first_name='',
                last_name=''
            )
        ]))
        
        if result.users:
            user = result.users[0]
            
            # Debug logging
            if debug:
                console.print(f"[cyan]Debug: Initial user data:[/cyan]")
                console.print(f"[cyan]{user.__dict__}[/cyan]")
            
            # Get full user info
            full_user = await client(functions.users.GetFullUserRequest(
                id=user.id
            ))
            
            # Debug logging
            if debug:
                console.print(f"[cyan]Debug: Full user data:[/cyan]")
                console.print(f"[cyan]{full_user.__dict__}[/cyan]")
            
            # Try to get username through ResolvePhone
            try:
                phone_resolve = await client(functions.contacts.ResolvePhoneRequest(
                    phone=phone_number
                ))
                if phone_resolve and phone_resolve.users:
                    user = phone_resolve.users[0]
                    # Debug logging
                    if debug:
                        console.print(f"[cyan]Debug: Phone resolve data:[/cyan]")
                        console.print(f"[cyan]{phone_resolve.__dict__}[/cyan]")
            except Exception as e:
                if debug:
                    console.print(f"[yellow]Could not resolve phone {phone_number}: {str(e)}[/yellow]")
            
            # Get last seen status
            last_seen = "Never"
            if hasattr(user.status, 'was_online'):
                last_seen = user.status.was_online.strftime('%Y-%m-%d %H:%M:%S')
            
            return {
                'username': getattr(user, 'username', None),
                'first_name': getattr(user, 'first_name', ''),
                'last_name': getattr(user, 'last_name', ''),
                'id': user.id,
                'bio': getattr(full_user.full_user, 'about', 'N/A'),
                'last_seen': last_seen,
                'is_bot': getattr(user, 'bot', False)
            }
        return None
        
    finally:
        # Clean up the test contact
        if result and result.users:
            await client(functions.contacts.DeleteContactsRequest(
                id=[result.users[0].id]
            ))

async def main():
    # Display banner
    console.print(f"[turquoise2]{BANNER}[/turquoise2]")
    
    load_dotenv()
    api_id = os.getenv('API_ID')
    api_hash = os.getenv('API_KEY')
    your_phone = os.getenv('YOUR_PHONE')

    if not all([api_id, api_hash, your_phone]):
        console.print("[red]Error: Missing environment variables. Please check your .env file.[/red]")
        return

    parser = create_parser()
    args = parser.parse_args()
    phone_numbers = get_phone_numbers(args)

    if not phone_numbers:
        console.print("[red]No phone numbers provided.[/red]")
        return

    # Create table structure
    table = Table(
        show_header=True,
        header_style="bold white",
        show_lines=True,
        box=ROUNDED,
        border_style="white",
        padding=(0, 1)
    )
    table.add_column("PHONE NUMBER", justify="center", style="white")
    table.add_column("STATUS", justify="center", style="white")
    table.add_column("FIRST NAME", justify="center", style="white")
    table.add_column("LAST NAME", justify="center", style="white")
    table.add_column("BIO", justify="center", style="white")
    table.add_column("USERNAME", justify="center", style="white")
    table.add_column("USER ID", justify="center", style="white")
    table.add_column("HUMAN?", justify="center", style="white")
    table.add_column("LAST SEEN", justify="center", style="white")

    # Use a permanent session name
    session_name = 'telegrab_session'
    client = TelegramClient(session_name, api_id, api_hash)
    
    try:
        # Connect to Telegram
        console.print("[green]Connecting to Telegram...[/green]")
        await client.connect()

        # Check if already authorized
        if not await client.is_user_authorized():
            # Send code request
            await client.send_code_request(your_phone)
            console.print("[yellow]Verification code sent to your Telegram account[/yellow]")
            
            while True:
                try:
                    verification_code = console.input("[bold]Enter the verification code: [/bold]")
                    await client.sign_in(your_phone, verification_code)
                    break
                except Exception as e:
                    console.print(f"[red]Invalid code. Please try again: {str(e)}[/red]")

        # Now proceed with status and number checking
        with console.status("[bold white]Processing...") as status:
            for phone in phone_numbers:
                status.update(f"[bold white]Checking number {phone}...")
                try:
                    # Add retry logic with exponential backoff
                    max_retries = 3
                    retry_delay = 2
                    
                    for attempt in range(max_retries):
                        try:
                            result = await check_number(client, phone, args.debug)
                            if result:
                                table.add_row(
                                    phone,
                                    "[green]Registered[/green]",
                                    result['first_name'] or 'N/A',
                                    result['last_name'] or 'N/A',
                                    result['bio'] or 'N/A',
                                    result['username'] or 'N/A',
                                    str(result['id']),
                                    "[green]Human[/green]" if not result['is_bot'] else "[red]Bot[/red]",
                                    result['last_seen']
                                )
                            else:
                                table.add_row(
                                    phone,
                                    "[red]Not Found[/red]",
                                    'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'
                                )
                            break  # Break the retry loop if successful
                            
                        except FloodWaitError as e:
                            if attempt < max_retries - 1:
                                wait_time = retry_delay * (2 ** attempt)
                                console.print(f"[yellow]Rate limited. Waiting {wait_time} seconds...[/yellow]")
                                await asyncio.sleep(wait_time)
                            else:
                                raise
                        
                    # Add delay between numbers to avoid rate limiting
                    await asyncio.sleep(3)
                    
                except Exception as e:
                    console.print(f"[red]Error processing {phone}: {str(e)}[/red]")
                    table.add_row(
                        phone,
                        "[red]Error[/red]",
                        'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
                        f"[red]{str(e)}[/red]"
                    )

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
    finally:
        await client.disconnect()

    # Print results
    console.print("\n[bold]Results:[/bold]")
    console.print(table)

def create_parser():
    """Create argument parser for CLI"""
    parser = argparse.ArgumentParser(description='Check Telegram phone numbers')
    parser.add_argument('-n', '--numbers', help='Comma-separated list of phone numbers')
    parser.add_argument('-f', '--file', help='File containing phone numbers (one per line)')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    return parser

def clean_phone_number(phone):
    """Clean phone number by removing spaces, dashes, parentheses and plus signs"""
    return ''.join(filter(str.isdigit, phone))

def get_phone_numbers(args):
    """Get phone numbers from arguments or prompt user"""
    if args.numbers:
        # Clean each number in the comma-separated list
        return [clean_phone_number(num.strip()) for num in args.numbers.split(',')]
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                # Clean each number from the file
                return [clean_phone_number(line.strip()) for line in f if line.strip()]
        except FileNotFoundError:
            console.print(f"[red]Error: File {args.file} not found.[/red]")
            return []
    else:
        # Prompt user for input and clean the number
        phone = input("Enter phone number (or comma-separated numbers): ")
        return [clean_phone_number(num.strip()) for num in phone.split(',')]

if __name__ == "__main__":
    asyncio.run(main())