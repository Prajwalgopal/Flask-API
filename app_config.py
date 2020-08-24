import os

CLIENT_ID = "4fa1fef0-b295-46b3-b384-4f5fedda4588" # Application (client) ID of app registration

CLIENT_SECRET = "10dKSnx-H.neqF_6-W_XDb5-.l5S8T5vr." # Placeholder - for use ONLY during testing.
# In a production app, we recommend you use a more secure method of storing your secret,
# like Azure Key Vault. Or, use an environment variable as described in Flask's documentation:
# https://flask.palletsprojects.com/en/1.1.x/config/#configuring-from-environment-variables
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# if not CLIENT_SECRET:
#     raise ValueError("Need to define CLIENT_SECRET environment variable")

AUTHORITY = "https://login.microsoftonline.com/common"  # For multi-tenant app
# AUTHORITY = "https://login.microsoftonline.com/Enter_the_Tenant_Name_Here"

REDIRECT_PATH = "/getToken"  # Used for forming an absolute URL to your redirect URI.
                              # The absolute URL must match the redirect URI you set
                              # in the app's registration in the Azure portal.

# You can find more Microsoft Graph API endpoints from Graph Explorer
# https://developer.microsoft.com/en-us/graph/graph-explorer
EVENT_ENDPOINT = 'https://graph.microsoft.com/v1.0/me/events'  # This resource requires no admin consent
DRIVE_ENDPOINT = 'https://graph.microsoft.com/v1.0/me/drive'
EMAIL_ENDPOINT = 'https://graph.microsoft.com/v1.0/me/messages'
USER_ENDPOINT = 'https://graph.microsoft.com/v1.0/me'
# You can find the proper permission names from this document
# https://docs.microsoft.com/en-us/graph/permissions-reference
SCOPE = ["User.ReadBasic.All", "Calendars.ReadWrite", "Files.ReadWrite.All", "Mail.ReadWrite"]

SESSION_TYPE = "filesystem"  # Specifies the token cache should be stored in server-side session
