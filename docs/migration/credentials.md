# Credentials Restore Note

## Security Action Taken
During migration to version control, the `.credentials.json` file was removed for security reasons as it contained live API tokens:
- Claude AI OAuth access token
- Claude AI OAuth refresh token

## File Location
The original file was located at:
```
.claude/.credentials.json
```

## Restoration Instructions
If you need to restore Claude authentication credentials for local development:

1. **DO NOT** commit the credentials file to git
2. Place credentials in your local `.claude/.credentials.json` file
3. The file is already added to `.gitignore` to prevent accidental commits
4. Consider using environment variables instead for better security

## Alternative Authentication
Consider using these more secure authentication methods:
- Environment variables: `CLAUDE_API_KEY`
- Local settings in `settings.local.json` (already gitignored)
- System keychain/credential manager

## Security Reminder
- ✅ Credentials removed from version control
- ✅ `.credentials.json` added to `.gitignore`
- ⚠️  Original tokens should be rotated if they were exposed
- ⚠️  Never commit API keys, tokens, or secrets to any repository

Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Action: Credentials removed during claude directory migration