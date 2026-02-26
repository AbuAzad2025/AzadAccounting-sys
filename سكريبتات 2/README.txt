
==================================================
🚀 Garage Manager - Tenant Initialization Guide
==================================================

This folder contains scripts to initialize the system for a new tenant (client).

Files:
1. seed_accounts.py: 
   - Restores the standard Chart of Accounts (GL Accounts).
   - Run this if the accounts table is empty.

2. initialize_tenant.py:
   - Interactive wizard to set up:
     - Company Name, Phone, Address
     - VAT Tax Rate
     - Main Warehouse
     - Opening Cash Capital
     - Admin Password Reset

Usage Instructions:
-------------------
1. Ensure you are in the project root directory.
2. Activate the virtual environment.
3. Run the scripts in order:

   # Step 1: Seed Accounts (if needed)
   python "سكريبتات 2/seed_accounts.py"

   # Step 2: Initialize Tenant Settings
   python "سكريبتات 2/initialize_tenant.py"

4. Follow the on-screen prompts.

Notes:
------
- These scripts DO NOT delete data. They only add/update settings.
- If you need to wipe the database first, ensure you have run the cleaning process (clean_for_new_tenant.py) BEFORE running these.
