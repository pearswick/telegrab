import os
import argparse
from dotenv import load_dotenv
from telethon import TelegramClient, functions, types
from telethon.errors import FloodWaitError, PhoneNumberInvalidError
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.progress import track
from rich.box import HEAVY

console = Console()

BANNER = """
████████╗███████╗██╗     ███████╗ ██████╗ ██████╗  █████╗ ██████╗ 
╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝ ██╔══██╗██╔══██╗██╔══██╗
   ██║   █████╗  ██║     █████╗  ██║  ███╗██████╔╝███████║██████╔╝
   ██║   ██╔══╝  ██║     ██╔══╝  ██║   ██║██╔══██╗██╔══██║██╔══██╗
   ██║   ███████╗███████╗███████╗╚██████╔╝██║  ██║██║  ██║██████╔╝
   ╚═╝   ╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ 
                                                                    
              A Telegram Phone Number Checker v1.0
              Created by: Stichting Bellingcat, modified by @pearswick
              License: MIT
"""

async def check_number(client, phone_number):
    try:
        result = await client(functions.contacts.ImportContactsRequest([
            types.InputPhoneContact(
                client_id=0,
                phone=phone_number,
                first_name='__test__',
                last_name=''
            )
        ]))
        
        if result.users:
            user = result.users[0]
            return {
                'username': user.username,
                'first_name': getattr(user, 'first_name', ''),
                'last_name': getattr(user, 'last_name', ''),
                'id': user.id
            }
        return None
        
    finally:
        # Clean up the test contact
        await client(functions.contacts.DeleteContactsRequest(
            id=[result.users[0].id] if result.users else []
        ))

def create_parser():
    parser = argparse.ArgumentParser(
        description='Telegram Phone Number Checker',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '-n', '--numbers',
        help='Comma-separated list of phone numbers to check',
        type=str
    )
    parser.add_argument(
        '-f', '--file',
        help='File containing phone numbers (one per line)',
        type=str
    )
    parser.add_argument(
        '--no-color',
        help='Disable colored output',
        action='store_true'
    )
    return parser

async def main():
    # Display banner in turquoise2
    console.print(f"[turquoise2]{BANNER}[/turquoise2]")
    
    parser = create_parser()
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()
    
    # Get credentials
    api_id = os.getenv('API_ID')
    api_hash = os.getenv('API_KEY')
    your_phone = os.getenv('YOUR_PHONE')
    
    if not all([api_id, api_hash, your_phone]):
        console.print("[red]Error: Missing required environment variables.[/red]")
        console.print("Required variables: API_ID, API_KEY, YOUR_PHONE")
        return

    # Get phone numbers to check
    phone_numbers = []
    if args.numbers:
        phone_numbers.extend([num.strip() for num in args.numbers.split(',')])
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                phone_numbers.extend([line.strip() for line in f if line.strip()])
        except FileNotFoundError:
            console.print(f"[red]Error: File {args.file} not found[/red]")
            return
    else:
        console.print("[yellow]No phone numbers provided. Enter numbers interactively:[/yellow]")
        numbers_input = input("Enter phone numbers (comma-separated): ")
        phone_numbers.extend([num.strip() for num in numbers_input.split(',')])

    if not phone_numbers:
        console.print("[red]Error: No phone numbers to check[/red]")
        return

    # Create results table with white styling
    table = Table(
        show_header=True,
        header_style="bold white",
        show_lines=True,
        box=HEAVY,
        padding=(0, 1),
        style="white"
    )
    table.add_column("PHONE NUMBER", justify="center", style="white")
    table.add_column("USERNAME", justify="center", style="white")
    table.add_column("FIRST NAME", justify="center", style="white")
    table.add_column("LAST NAME", justify="center", style="white")
    table.add_column("USER ID", justify="center", style="white")
    table.add_column("STATUS", justify="center", style="white")

    with console.status("[bold white]Connecting to Telegram...") as status:
        client = TelegramClient('session_name', api_id, api_hash)
        try:
            await client.start(phone=your_phone)
            status.update("[bold white]Checking phone numbers...")

            for phone in track(phone_numbers, description="Checking numbers"):
                try:
                    result = await check_number(client, phone)
                    if result:
                        table.add_row(
                            phone,
                            result['username'] or 'N/A',
                            result['first_name'] or 'N/A',
                            result['last_name'] or 'N/A',
                            str(result['id']),
                            "[green]Registered[/green]"
                        )
                    else:
                        table.add_row(
                            phone,
                            'N/A',
                            'N/A',
                            'N/A',
                            'N/A',
                            "[red]Not Found[/red]"
                        )
                except FloodWaitError as e:
                    console.print(f"[red]Rate limit exceeded. Please wait {e.seconds} seconds[/red]")
                    break
                except PhoneNumberInvalidError:
                    table.add_row(
                        phone,
                        'N/A',
                        'N/A',
                        'N/A',
                        'N/A',
                        "[yellow]Invalid Format[/yellow]"
                    )
                except Exception as e:
                    table.add_row(
                        phone,
                        'N/A',
                        'N/A',
                        'N/A',
                        'N/A',
                        f"[red]Error: {str(e)}[/red]"
                    )

        except Exception as e:
            console.print(f"[red]Error initializing Telegram client: {str(e)}[/red]")
        finally:
            await client.disconnect()

    # Print results
    console.print("\n[bold]Results:[/bold]")
    console.print(table)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())