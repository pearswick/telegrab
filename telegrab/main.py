import os
import argparse
from dotenv import load_dotenv
from telethon import TelegramClient, functions, types
from telethon.errors import FloodWaitError, PhoneNumberInvalidError
from rich.console import Console
from rich.table import Table
from rich.box import ROUNDED
import asyncio
import phonenumbers
from phonenumbers.phonenumberutil import region_code_for_country_code
from typing import List
from telegrab.version import __version__  # Add this for version support

console = Console()

BANNER = f"""
████████╗███████╗██║     ███████╗ ██████╗ ██████╗  █████╗ ██████╗    
╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝ ██╔══██╗██╔══██╗██╔══██╗   📱 Welcome to telegrab v{__version__}
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
            elif hasattr(user.status, 'expires'):
                # Handle different status types
                if isinstance(user.status, types.UserStatusOnline):
                    last_seen = "Online"
                elif isinstance(user.status, types.UserStatusRecently):
                    last_seen = "Last seen recently"
                elif isinstance(user.status, types.UserStatusLastWeek):
                    last_seen = "Last seen in the last week"
                elif isinstance(user.status, types.UserStatusLastMonth):
                    last_seen = "Last seen in the last month"
                else:
                    last_seen = "Last seen a long time ago"
            
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
    table.add_column("PHONE NUMBER", justify="left", style="white")
    table.add_column("FLAG", justify="center", style="white")
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
                    verification_code = console.input("[bold white]Enter the verification code: [/bold white]")
                    await client.sign_in(your_phone, verification_code)
                    break
                except Exception as e:
                    console.print(f"[red]Invalid code. Please try again: {str(e)}[/red]")

        # Now proceed with status and number checking
        with console.status("[bold white]Processing...") as status:
            for phone in phone_numbers:
                status.update(f"[white]Checking number {phone}...[/white]")
                try:
                    # Add retry logic with exponential backoff
                    max_retries = 3
                    retry_delay = 2
                    
                    for attempt in range(max_retries):
                        try:
                            result = await check_number(client, phone, args.debug)
                            if result:
                                table.add_row(
                                    str(phone),
                                    get_country_flag(phone),
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
                                    str(phone),
                                    get_country_flag(phone),
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
                        str(phone),
                        get_country_flag(phone),
                        "[red]Error[/red]",
                        'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',
                        f"[red]{str(e)}[/red]"
                    )

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
    finally:
        await client.disconnect()

    # Print results
    console.print("\n[bold white]Results:[/bold white]")
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
        # Clean and validate each number in the comma-separated list
        return process_phone_numbers(args.numbers)
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                # Clean and validate each number from the file
                return process_phone_numbers(','.join(line.strip() for line in f if line.strip()))
        except FileNotFoundError:
            console.print(f"[red]Error: File {args.file} not found.[/red]")
            return []
    else:
        # Prompt user for input
        while True:
            phone = console.input("[bold white]Enter phone number (or comma-separated numbers): [/bold white]")
            valid_numbers = process_phone_numbers(phone)
            if valid_numbers:
                return valid_numbers
            else:
                console.print("[red]Error: Please enter valid phone numbers (digits only, minimum 7 digits)[/red]")
                continue

def get_country_flag(phone: str) -> str:
    """Get country ISO code for phone number"""
    try:
        # Parse the phone number
        parsed = phonenumbers.parse('+' + phone)
        # Get the country code
        country_code = region_code_for_country_code(parsed.country_code)
        return country_code if country_code else "??"
    except:
        return "??"

def format_phone_with_flag(phone: str) -> str:
    """Format phone number with country code if present"""
    # Remove any spaces or special characters
    phone = ''.join(filter(str.isdigit, phone))
    
    try:
        # Parse the phone number
        parsed = phonenumbers.parse('+' + phone)
        # Get the country code
        country_code = region_code_for_country_code(parsed.country_code)
        if country_code:
            return f"({country_code}) {phone}"
    except:
        pass
    
    return f"(--) {phone}"

def validate_phone_number(phone: str) -> bool:
    """Validate phone number contains only digits after cleaning"""
    # Remove any spaces, plus signs, or hyphens
    cleaned = ''.join(filter(str.isdigit, phone))
    # Check if we have any digits and if all remaining chars are digits
    return bool(cleaned) and len(cleaned) >= 7
    
def process_phone_numbers(numbers_input: str) -> List[str]:
    """Process and validate phone numbers from input string"""
    # Split by comma and strip whitespace
    numbers = [n.strip() for n in numbers_input.split(',')]
    valid_numbers = []
    
    for number in numbers:
        if validate_phone_number(number):
            # Keep only the digits
            cleaned = ''.join(filter(str.isdigit, number))
            valid_numbers.append(cleaned)
        else:
            print(f"Invalid phone number format: {number}")
            
    return valid_numbers

def display_welcome():
    """Display welcome message"""
    console.print(f"\n[bold blue]Welcome to telegrab v{__version__}[/bold blue]")
    console.print("[dim]A Telegram Phone Number Checker[/dim]\n")

if __name__ == "__main__":
    asyncio.run(main())