import platform
import subprocess
import time
import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# File to store IPs and machine names
IP_STORE = "ip_list.json"

def load_ips():
    if not os.path.exists(IP_STORE):
        return []

    with open(IP_STORE, 'r') as f:
        data = json.load(f)

    # Auto-upgrade from list of strings to list of dicts
    if isinstance(data, list) and all(isinstance(item, str) for item in data):
        upgraded = [{'ip': item, 'machine': 'Unknown'} for item in data]
        save_ips(upgraded)
        print("Old format detected. Data has been upgraded.")
        return upgraded

    return data

def save_ips(ips):
    with open(IP_STORE, 'w') as f:
        json.dump(ips, f, indent=2)

def add_ip():
    while True:
        print("\n--- Add IP Entry (type 'b' to go back) ---")
        ip = input("Enter IP address to monitor: ").strip()
        if ip.lower() == 'b':
            return
        machine = input("Enter machine name: ").strip()
        if machine.lower() == 'b':
            return

        ips = load_ips()
        for entry in ips:
            if entry['ip'] == ip:
                print("IP already exists.")
                return
        ips.append({'ip': ip, 'machine': machine})
        save_ips(ips)
        print(f"{ip} ({machine}) added.")
        break

def view_ips():
    ips = load_ips()
    if not ips:
        print("No entries stored.")
    else:
        print("\nStored Entries:")
        for i, entry in enumerate(ips, 1):
            print(f"{i}. {entry['ip']} - {entry['machine']}")

def delete_ip():
    while True:
        ips = load_ips()
        if not ips:
            print("No entries to delete.")
            return
        view_ips()
        print("Enter entry number to delete or 'b' to go back.")
        choice = input("Your choice: ").strip()
        if choice.lower() == 'b':
            return
        try:
            index = int(choice) - 1
            if 0 <= index < len(ips):
                removed = ips.pop(index)
                save_ips(ips)
                print(f"Removed {removed['ip']} - {removed['machine']}")
                break
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")

def admin_menu():
    while True:
        print("\n--- Admin Panel ---")
        print("1. View Entries")
        print("2. Add Entry")
        print("3. Delete Entry")
        print("4. Start Monitoring")
        print("5. Exit")
        choice = input("Choose an option: ").strip()
        if choice == '1':
            view_ips()
        elif choice == '2':
            add_ip()
        elif choice == '3':
            delete_ip()
        elif choice == '4':
            start_monitoring()
        elif choice == '5':
            break
        else:
            print("Invalid choice.")

def ping_device(ip_address):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip_address]

    try:
        if platform.system().lower() == 'windows':
            result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return result.returncode == 0
    except Exception as e:
        print(f"Error pinging device: {e}")
        return False

def send_email(subject, body):
    sender_email = "soshantkumar1060@gmail.com"
    receiver_email = "sosant.kumar@jbmgroup.com"
    password = "qoyp emur fidb yxvi"  # Use Gmail App Password here

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def start_monitoring():
    entries = load_ips()
    if not entries:
        print("No entries to monitor. Please add IPs in admin panel first.")
        return

    print("\nStarting monitoring. Press Ctrl+C to stop.")
    status_dict = {entry['ip']: None for entry in entries}

    try:
        while True:
            for entry in entries:
                ip = entry['ip']
                machine = entry['machine']
                current_status = ping_device(ip)

                if current_status != status_dict[ip]:
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                    if current_status:
                        message = f"{timestamp} - {ip} ({machine}) is CONNECTED"
                    else:
                        message = f"{timestamp} - {ip} ({machine}) is DISCONNECTED"
                    print(message)
                    send_email(f"{machine} ({ip}) Status Change", message)
                    status_dict[ip] = current_status

            time.sleep(2)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    admin_menu()
