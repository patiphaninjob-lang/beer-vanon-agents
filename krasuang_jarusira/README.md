# Krasuang Jarusira Facebook Scraper

This folder is separate from the Bert Manit scraper.

## Local setup

```powershell
python -m pip install -r requirements_krasuang_jarusira.txt
python -m playwright install chromium
```

Create `.env` in the project root:

```env
FB_EMAIL=your_facebook_email
FB_PASSWORD=your_facebook_password

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
REPORT_EMAIL_FROM=your_email@gmail.com
REPORT_EMAIL_TO=destination_email@gmail.com
```

First run should be visible so Facebook can ask for verification if needed:

```powershell
python scrape_krasuang_jarusira.py
```

After the session is saved to `krasuang_jarusira/fb_storage_state.json`, scheduled/headless runs can use:

```powershell
python scrape_krasuang_jarusira.py --headless
```

## Running while your PC is off

A local script cannot run when the PC is powered off. Use a VPS, cloud VM, or GitHub Actions runner. Put the same environment variables on that machine, install the requirements, and schedule:

```powershell
python scrape_krasuang_jarusira.py --headless --email-every-minutes 30
```

Outputs:

- `krasuang_jarusira/krasuang_jarusira_page_data.json`
- `krasuang_jarusira/krasuang_jarusira_page_data.md`
