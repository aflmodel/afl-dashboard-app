from gmail_sender import send_email

# The recipient (can be your own Gmail for testing)
to = "themodel.patreon@gmail.com"

subject = "🔔 Test Email from The Model"
message = """
Hi there,

This is a test email sent from your AFL Dashboard using the Gmail API.

If you're seeing this, everything is working perfectly.

– The Model
"""

send_email(to, subject, message)
