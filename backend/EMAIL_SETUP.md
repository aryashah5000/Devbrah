# 📧 Email Setup Guide

## Setting up email for devbrah

The newsletter will be sent to the user's email address when they generate a newsletter.

## Option 1: Gmail (Recommended for Hackathon)

### Step 1: Enable 2-Factor Authentication
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification if not already enabled

### Step 2: Generate App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other (Custom name)"
3. Name it "devbrah"
4. Copy the 16-character password (no spaces)

### Step 3: Update .env file
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
FROM_EMAIL=your-email@gmail.com
FROM_NAME=devbrah
```

## Option 2: Outlook/Hotmail

### Update .env file
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
FROM_EMAIL=your-email@outlook.com
FROM_NAME=devbrah
```

## Option 3: Other SMTP Providers

### Common SMTP Settings:
- **Yahoo**: smtp.mail.yahoo.com, port 587
- **SendGrid**: smtp.sendgrid.net, port 587 (requires API key)
- **Mailgun**: smtp.mailgun.org, port 587

## Testing Email

Once configured, the newsletter will automatically be sent when a user generates it from the dashboard.

To test without generating a full newsletter, you can check the backend logs - it will show:
- ✅ "Newsletter sent successfully to [email]" if successful
- ❌ Error message if there's an issue

## Troubleshooting

1. **"Authentication failed"**: Check your SMTP credentials
2. **"Connection refused"**: Check SMTP server and port
3. **Gmail "Less secure app" error**: Use App Password (not regular password)
4. **Email not received**: Check spam folder

## For Hackathon Demo

If you don't want to set up email right now, the app will still work - it just won't send emails. The newsletter will still be generated and viewable in the web interface.

