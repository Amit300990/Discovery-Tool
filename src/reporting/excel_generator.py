import pandas as pd
import requests
from datetime import datetime, timedelta

HUB_URL = "http://localhost:8000"

def generate_report(output_file="Cryptographic_Asset_Inventory.xlsx"):
    print("Fetching data from Hub...")
    try:
        keys_data = requests.get(f"{HUB_URL}/keys").json()
        certs_data = requests.get(f"{HUB_URL}/certificates").json()
    except Exception as e:
        print(f"Error connecting to Hub: {e}")
        return

    print(f"Fetched {len(keys_data)} keys and {len(certs_data)} certificates.")

    # Create DataFrames
    df_keys = pd.DataFrame(keys_data)
    df_certs = pd.DataFrame(certs_data)

    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
    workbook = writer.book

    # Formats
    header_fmt = workbook.add_format({'bold': True, 'bg_color': '#1F497D', 'font_color': 'white'})
    date_fmt = workbook.add_format({'num_format': 'yyyy-mm-dd'})
    red_fmt = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
    orange_fmt = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C6500'})

    # --- Tab 1: Dashboard ---
    worksheet_dash = workbook.add_worksheet('Dashboard')
    worksheet_dash.write('A1', 'Cryptographic Asset Dashboard', header_fmt)
    
    # KPIs
    total_keys = len(df_keys)
    total_certs = len(df_certs)
    
    # Calculate expiring certs (mock logic if dates are string)
    expiring_soon = 0
    now = datetime.now()
    for c in certs_data:
        try:
            valid_to = datetime.fromisoformat(c['valid_to'].replace('Z', '+00:00'))
            if now < valid_to < now + timedelta(days=30):
                expiring_soon += 1
        except:
            pass

    worksheet_dash.write('A3', 'Total Keys', header_fmt)
    worksheet_dash.write('B3', total_keys)
    worksheet_dash.write('A4', 'Total Certificates', header_fmt)
    worksheet_dash.write('B4', total_certs)
    worksheet_dash.write('A5', 'Expiring < 30 Days', header_fmt)
    worksheet_dash.write('B5', expiring_soon, red_fmt if expiring_soon > 0 else None)

    # --- Tab 2: Keys Inventory ---
    if not df_keys.empty:
        df_keys.to_excel(writer, sheet_name='Keys Inventory', index=False)
        worksheet_keys = writer.sheets['Keys Inventory']
        
        # Apply conditional formatting
        # Example: Highlight weak algorithms (simplified check)
        worksheet_keys.conditional_format(1, 4, len(df_keys), 4, { # Column E is Algorithm
            'type': 'text',
            'criteria': 'containing',
            'value': 'RSA-1024',
            'format': red_fmt
        })
        
        # Auto-filter
        worksheet_keys.autofilter(0, 0, len(df_keys), len(df_keys.columns) - 1)

    # --- Tab 3: Certificates Inventory ---
    if not df_certs.empty:
        df_certs.to_excel(writer, sheet_name='Certificates Inventory', index=False)
        worksheet_certs = writer.sheets['Certificates Inventory']
        
        # Apply conditional formatting for expiry
        # Note: Excel conditional formatting on dates requires careful column index management
        # Here we just apply autofilter
        worksheet_certs.autofilter(0, 0, len(df_certs), len(df_certs.columns) - 1)

    writer.close()
    print(f"Report generated: {output_file}")

if __name__ == "__main__":
    generate_report()
