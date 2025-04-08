# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of DoliaAI seriously. If you believe you've found a security vulnerability, please follow these steps:

1. **Do Not** disclose the vulnerability publicly until it has been addressed by our team.

2. **Do** submit your findings by emailing security@nahvine.com or by creating a private security advisory on GitHub.

3. **Do** provide detailed information about the vulnerability:
   - Type of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fixes (if any)

4. **Do** give us a reasonable time to respond before taking any further action.

5. **Do** make a good faith effort to avoid privacy violations, destruction of data, and interruption or degradation of our service.

## Security Best Practices

When using DoliaAI, please follow these security best practices:

1. **API Keys**
   - Never commit API keys to version control
   - Use environment variables or secure configuration files
   - Rotate keys regularly

2. **Permissions**
   - Run with minimum required permissions
   - Use principle of least privilege
   - Regularly audit access rights

3. **Updates**
   - Keep DoliaAI and dependencies up to date
   - Monitor security advisories
   - Apply security patches promptly

4. **Monitoring**
   - Enable logging
   - Monitor for suspicious activities
   - Set up alerts for security events

## Security Features

DoliaAI includes several security features:

1. **Input Validation**
   - Sanitizes all user inputs
   - Validates file paths
   - Checks command parameters

2. **Error Handling**
   - Secure error messages
   - No sensitive information in logs
   - Graceful failure handling

3. **Access Control**
   - Permission-based execution
   - Resource usage limits
   - Action timeouts

4. **Data Protection**
   - Secure configuration storage
   - Encrypted API communications
   - Safe file operations 