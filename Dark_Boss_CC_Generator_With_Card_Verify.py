import random
import os
import webbrowser
import requests
import time
from datetime import datetime, timedelta

class AutoVerifiedDarkBossCCGenerator:
    def __init__(self):
        self.brands = {
            'Visa': ['4'],
            'Mastercard': ['51', '52', '53', '54', '55'],
            'Amex': ['34', '37'],
            'Discover': ['6011', '65']
        }
        self.verified_cards = []
        
    def luhn_check(self, card_number):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10 == 0

    def generate_expiry_date(self):
        current_year = datetime.now().year
        month = random.randint(1, 12)
        year = current_year + random.randint(1, 5)
        return f"{month:02d}/{year}"

    def generate_cvv(self, brand):
        if brand == 'Amex':
            return str(random.randint(1000, 9999))
        else:
            return str(random.randint(100, 999))

    def auto_verify_card(self, cc_data):
        """
        Simulate automatic card verification with different statuses
        In real scenario, this would connect to payment gateways
        """
        card_number = cc_data['number']
        
        # Simulate verification process
        time.sleep(0.5)  # Simulate API call delay
        
        # Enhanced verification logic based on card patterns
        verification_score = 0
        
        # Check Luhn algorithm
        if self.luhn_check(card_number):
            verification_score += 40
        
        # Check card brand recognition
        if cc_data['brand'] != 'Unknown':
            verification_score += 20
        
        # Check expiry date (not expired)
        current_date = datetime.now()
        expiry_month, expiry_year = map(int, cc_data['expiry'].split('/'))
        expiry_date = datetime(expiry_year, expiry_month, 1) + timedelta(days=32)
        expiry_date = expiry_date.replace(day=1) - timedelta(days=1)
        
        if expiry_date > current_date:
            verification_score += 20
        else:
            verification_score -= 30
        
        # Check CVV length based on brand
        if cc_data['brand'] == 'Amex' and len(cc_data['cvv']) == 4:
            verification_score += 10
        elif cc_data['brand'] != 'Amex' and len(cc_data['cvv']) == 3:
            verification_score += 10
        
        # Random factor to simulate real-world verification
        verification_score += random.randint(-10, 20)
        
        # Determine verification status
        if verification_score >= 80:
            status = "VERIFIED"
            status_color = "green"
            balance = f"${random.randint(100, 5000):,}"
        elif verification_score >= 60:
            status = "LIVE"
            status_color = "lightgreen"
            balance = f"${random.randint(50, 1000):,}"
        elif verification_score >= 40:
            status = "UNVERIFIED"
            status_color = "yellow"
            balance = "N/A"
        else:
            status = "DEAD"
            status_color = "red"
            balance = "$0"
        
        # Add verification data to card
        cc_data.update({
            'status': status,
            'status_color': status_color,
            'balance': balance,
            'verification_score': verification_score,
            'verified_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        return cc_data

    def identify_brand(self, bin_number):
        for brand, bins in self.brands.items():
            for b in bins:
                if bin_number.startswith(b):
                    return brand
        return 'Unknown'

    def generate_cc(self, bin_number=None):
        if bin_number is None:
            brand = random.choice(list(self.brands.keys()))
            bin_number = random.choice(self.brands[brand])
        else:
            brand = self.identify_brand(bin_number)
        
        cc_number = bin_number
        while len(cc_number) < 15:
            cc_number += str(random.randint(0, 9))
        
        for check_digit in range(10):
            test_cc = cc_number + str(check_digit)
            if self.luhn_check(test_cc):
                expiry = self.generate_expiry_date()
                cvv = self.generate_cvv(brand)
                return {
                    'number': test_cc,
                    'expiry': expiry,
                    'cvv': cvv,
                    'brand': brand
                }
        return None

    def generate_and_verify_single_cc(self):
        print("\n[+] Generating and Verifying Single CC...")
        cc_data = self.generate_cc()
        if cc_data:
            verified_data = self.auto_verify_card(cc_data)
            self.verified_cards.append(verified_data)
            self.display_card_info(verified_data)
            return verified_data
        else:
            print("[-] Failed to generate valid CC")
            return None

    def generate_and_verify_bulk_cc(self, count=10):
        print(f"\n[+] Generating and Verifying {count} CCs...")
        successful_verifications = 0
        
        for i in range(count):
            print(f"\r[+] Verifying cards... {i+1}/{count}", end="", flush=True)
            cc_data = self.generate_cc()
            if cc_data:
                verified_data = self.auto_verify_card(cc_data)
                self.verified_cards.append(verified_data)
                if verified_data['status'] in ['VERIFIED', 'LIVE']:
                    successful_verifications += 1
        
        print(f"\n[+] Verification completed!")
        print(f"[+] Successfully verified: {successful_verifications}/{count} cards")
        return self.verified_cards[-count:]

    def display_card_info(self, cc_data):
        status_color = {
            'VERIFIED': '🟢',
            'LIVE': '🟡', 
            'UNVERIFIED': '🟠',
            'DEAD': '🔴'
        }
        
        print(f"\n{status_color.get(cc_data['status'], '⚫')} Card Information:")
        print(f"   Number: {cc_data['number']}")
        print(f"   Expiry: {cc_data['expiry']}")
        print(f"   CVV: {cc_data['cvv']}")
        print(f"   Brand: {cc_data['brand']}")
        print(f"   Status: {cc_data['status']}")
        print(f"   Balance: {cc_data['balance']}")
        print(f"   Score: {cc_data['verification_score']}%")

    def validate_single_cc(self, cc_number):
        print(f"\n[+] Validating CC: {cc_number}")
        if self.luhn_check(cc_number):
            brand = self.identify_brand(cc_number[:6])
            expiry = self.generate_expiry_date()
            cvv = self.generate_cvv(brand)
            
            cc_data = {
                'number': cc_number,
                'expiry': expiry,
                'cvv': cvv,
                'brand': brand
            }
            
            verified_data = self.auto_verify_card(cc_data)
            self.verified_cards.append(verified_data)
            self.display_card_info(verified_data)
            return verified_data
        else:
            print("[-] CC is INVALID")
            return None

    def generate_multi_bin(self, count=5):
        print(f"\n[+] Generating {count} BIN numbers...")
        bin_list = []
        for i in range(count):
            brand = random.choice(list(self.brands.keys()))
            bin_num = random.choice(self.brands[brand])
            while len(bin_num) < 6:
                bin_num += str(random.randint(0, 9))
            bin_list.append({'bin': bin_num, 'brand': brand})
            print(f"[{i+1}] {bin_num} ({brand})")
        return bin_list

    def generate_html_report(self, filename="darkboss_verified_cards.html"):
        if not self.verified_cards:
            print("[-] No verified cards to generate report")
            return None

        verified_count = len([c for c in self.verified_cards if c['status'] in ['VERIFIED', 'LIVE']])
        total_count = len(self.verified_cards)

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dark Boss Verified Cards Report</title>
            <style>
                body {{
                    font-family: 'Courier New', monospace;
                    background: linear-gradient(135deg, #0c0c0c, #1a1a2e);
                    color: #00ff00;
                    margin: 0;
                    padding: 20px;
                    min-height: 100vh;
                }}
                .container {{
                    max-width: 1400px;
                    margin: 0 auto;
                    background: rgba(0, 0, 0, 0.8);
                    border: 2px solid #00ff00;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 0 20px #00ff00;
                }}
                .header {{
                    text-align: center;
                    padding: 20px;
                    border-bottom: 2px solid #00ff00;
                    margin-bottom: 20px;
                }}
                .header h1 {{
                    color: #ff0000;
                    text-shadow: 0 0 10px #ff0000;
                    margin: 0;
                    font-size: 2.5em;
                }}
                .stats {{
                    display: flex;
                    justify-content: space-around;
                    margin: 20px 0;
                    padding: 15px;
                    background: rgba(0, 255, 0, 0.1);
                    border-radius: 5px;
                }}
                .stat-box {{
                    text-align: center;
                    padding: 10px;
                }}
                .stat-number {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #00ff00;
                }}
                .cc-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                .cc-table th {{
                    background: #006600;
                    color: #00ff00;
                    padding: 12px;
                    text-align: left;
                    border: 1px solid #00ff00;
                }}
                .cc-table td {{
                    padding: 12px;
                    border: 1px solid #00ff00;
                    background: rgba(0, 255, 0, 0.05);
                }}
                .status-verified {{ color: #00ff00; font-weight: bold; }}
                .status-live {{ color: #90ee90; font-weight: bold; }}
                .status-unverified {{ color: #ffff00; font-weight: bold; }}
                .status-dead {{ color: #ff0000; font-weight: bold; }}
                .brand-visa {{ color: #1a1f71; }}
                .brand-mastercard {{ color: #eb001b; }}
                .brand-amex {{ color: #2e77bc; }}
                .brand-discover {{ color: #ff6000; }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding: 20px;
                    border-top: 1px solid #00ff00;
                    color: #888;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🦊 DARK BOSS CC GENERATOR</h1>
                    <h2>Auto-Verified Cards Report | Powered by DARKBOSS1BD</h2>
                </div>
                
                <div class="stats">
                    <div class="stat-box">
                        <div class="stat-number">{total_count}</div>
                        <div>Total Cards</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{verified_count}</div>
                        <div>Verified Cards</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{verified_count/total_count*100:.1f}%</div>
                        <div>Success Rate</div>
                    </div>
                </div>

                <table class="cc-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Card Number</th>
                            <th>Expiry Date</th>
                            <th>CVV</th>
                            <th>Brand</th>
                            <th>Status</th>
                            <th>Balance</th>
                            <th>Score</th>
                            <th>Verified At</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for i, card in enumerate(self.verified_cards, 1):
            status_class = f"status-{card['status'].lower()}"
            brand_class = f"brand-{card['brand'].lower()}"
            
            html_content += f"""
                        <tr>
                            <td>{i}</td>
                            <td>{card['number']}</td>
                            <td>{card['expiry']}</td>
                            <td>{card['cvv']}</td>
                            <td class="{brand_class}">{card['brand']}</td>
                            <td class="{status_class}">{card['status']}</td>
                            <td>{card['balance']}</td>
                            <td>{card['verification_score']}%</td>
                            <td>{card['verified_at']}</td>
                        </tr>
            """
        
        html_content += f"""
                    </tbody>
                </table>
                
                <div class="footer">
                    <p><strong>Contact:</strong> 
                    <a href="https://t.me/darkvaiadmin" style="color: #00ff00;">Telegram</a> | 
                    <a href="https://t.me/windowspremiumkey" style="color: #00ff00;">Channel</a> | 
                    <a href="https://crackyworld.com/" style="color: #00ff00;">Website</a>
                    </p>
                    <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[+] HTML report generated: {filename}")
        return filename

def display_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║               DARK BOSS AUTO CC VERIFIER                     ║
    ║                   Powered by DARKBOSS1BD                     ║
    ║                                                              ║
    ║    ██████╗  █████╗ ██████╗ ██╗  ██╗██████╗  ██████╗ ███████╗║
    ║    ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝██╔══██╗██╔═══██╗██╔════╝║
    ║    ██║  ██║███████║██████╔╝█████╔╝ ██████╔╝██║   ██║███████╗║
    ║    ██║  ██║██╔══██║██╔══██╗██╔═██╗ ██╔══██╗██║   ██║╚════██║║
    ║    ██████╔╝██║  ██║██║  ██║██║  ██╗██║  ██║╚██████╔╝███████║║
    ║    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝║
    ║                                                              ║
    ║           AUTO VERIFICATION SYSTEM ACTIVATED                 ║
    ║      Telegram: https://t.me/darkvaiadmin                     ║
    ║     Channel: https://t.me/windowspremiumkey                  ║
    ║        Website: https://crackyworld.com/                     ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def main():
    generator = AutoVerifiedDarkBossCCGenerator()
    
    while True:
        display_banner()
        print("[x] 1) Generate & Verify Single CC")
        print("[x] 2) Bulk Generate & Verify CCs")
        print("[x] 3) Validate Existing CC")
        print("[x] 4) Generate Multi BIN Number")
        print("[x] 5) Generate HTML Report")
        print("[x] 6) Clear Verification History")
        print("[x] 7) Exit")
        
        choice = input("\n[A] Please Enter an option: ").strip()
        
        if choice == '1':
            generator.generate_and_verify_single_cc()
            input("\nPress Enter to continue...")
        
        elif choice == '2':
            try:
                count = int(input("[A] Enter number of CCs to generate and verify: "))
                cards = generator.generate_and_verify_bulk_cc(count)
                
                if cards and input("\nGenerate HTML report? (y/n): ").lower() == 'y':
                    filename = generator.generate_html_report()
                    if input("Open HTML report in browser? (y/n): ").lower() == 'y':
                        webbrowser.open(f'file://{os.path.abspath(filename)}')
            except ValueError:
                print("[-] Please enter a valid number")
            input("\nPress Enter to continue...")
        
        elif choice == '3':
            cc = input("[A] Enter CC number to validate: ").strip()
            generator.validate_single_cc(cc)
            input("\nPress Enter to continue...")
        
        elif choice == '4':
            try:
                count = int(input("[A] Enter number of BINs to generate: "))
                generator.generate_multi_bin(count)
            except ValueError:
                print("[-] Please enter a valid number")
            input("\nPress Enter to continue...")
        
        elif choice == '5':
            if generator.verified_cards:
                filename = generator.generate_html_report()
                if input("Open HTML report in browser? (y/n): ").lower() == 'y':
                    webbrowser.open(f'file://{os.path.abspath(filename)}')
            else:
                print("[-] No verified cards available for report")
            input("\nPress Enter to continue...")
        
        elif choice == '6':
            generator.verified_cards.clear()
            print("[+] Verification history cleared!")
            input("\nPress Enter to continue...")
        
        elif choice == '7':
            print("\n[+] Thank you for using Dark Boss Auto CC Verifier!")
            print("[+] Visit: https://crackyworld.com/")
            break
        
        else:
            print("[-] Invalid option! Please choose 1-7")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
