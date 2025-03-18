# GitHub Automation Setup for 3&7 Training Platform

This document outlines the automated GitHub integration setup for the 3&7 Training Platform, focusing on security, compliance, and Indonesia-specific requirements.

## Configuration Files

The automation is configured through the following files:

- `.cursor/automation.json`: Main configuration for GitHub automation
- `.cursor/country-rules/id.ts`: Indonesia-specific rules and compliance settings

## Security Measures

The GitHub integration includes several security hardening measures:

1. **Deployment Keys with Limited Permissions**
   - Keys are restricted to specific branches only
   - Read-only access where possible
   - Regular key rotation

2. **Commit Signing**
   - All automated commits are signed
   - Verification required for GitHub branch protection

3. **Audit Logging**
   - All git operations are logged to `/var/log/cursor_git.log`
   - Logs are encrypted using LSN standards
   - Retention policy compliant with PDPA requirements

4. **Ephemeral Credentials**
   - 15-minute validity window
   - Automatic revocation after use

## Indonesia-Specific Compliance

The automation is configured to meet Indonesia's regulatory requirements:

1. **Data Residency**
   - Primary storage in Jakarta (jakarta-cdn-01)
   - Backup storage in Surabaya (surabaya-dr-02)
   - No data leaves Indonesian territory

2. **Commit Policy**
   - Restricted to business hours (08:00-17:00 WIB)
   - Holiday blackouts (including Independence Day)
   - Maximum 15 commits per hour to prevent abuse

3. **PDPA Compliance**
   - Pre-commit validation for personal data
   - Content filtering to prevent sensitive data exposure
   - Audit trail for Kominfo reporting

## Network Resilience

The system is designed to handle Indonesia's unique network conditions:

1. **Connection Throttling**
   - Automatic retry for unstable connections
   - Bandwidth optimization for Telkomsel/Smartfren networks
   - Graceful degradation during monsoon conditions

2. **Regional Overrides**
   - Higher failure thresholds for known unstable regions
   - Increased latency tolerance for remote areas

## Activation Commands

Enable the automated git integration:

```bash
cursor --enable-auto-git \
  --country=ID \
  --compliance=pdpa-2024 \
  --security-profile=high \
  --regional-server=jakarta-02.3n7.id
```

Monitor git synchronization:

```bash
cursor --monitor-git-sync \
  --webhook=https://api.status.3n7.id/git-events \
  --alert-thresholds=failed_attempts=3,latency=5000ms \
  --regional-overrides=IDN:failed_attempts=5,latency=8000ms
```

## Troubleshooting

If you encounter issues with the automated GitHub integration:

1. Check the Cursor logs: `~/.cursor/logs/git-automation.log`
2. Verify network connectivity to GitHub
3. Ensure deployment keys are properly configured
4. Check Indonesia-specific timeframe restrictions

For emergency manual override:

```bash
cursor --disable-auto-git --force
``` 