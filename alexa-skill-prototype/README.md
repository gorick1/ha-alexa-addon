# Music Assistant Alexa Skill Prototype Add-on

This add-on runs the Music Assistant Alexa Skill Prototype, enabling you to control Music Assistant playback through Amazon Alexa devices.

## Features

- Detects all Alexa devices linked to your Amazon account
- Control playback (play, pause) on Alexa devices
- Set and mute volume on Alexa devices
- Integrates seamlessly with Home Assistant and Music Assistant

## Installation

1. In Home Assistant, go to **Settings** → **Add-ons** → **Add-on Store**
2. Click the three-dot menu in the top-right corner
3. Select **Repositories**
4. Add this repository URL:
   ```
   https://github.com/garrettorick/ha-addons
   ```
5. Search for "Music Assistant Alexa Skill"
6. Click **Install**

## Configuration

Before starting the add-on, configure:

- **api_username**: API username for the skill (default: `musicassistant`)
- **api_password**: API password for the skill (default: auto-generated strong password)

## Setup Steps

After starting the add-on:

1. **Access the Setup UI**: Navigate to `https://home.garrettorick.com/setup`
2. **Authorize with Amazon**:
   - Click "Authenticate with Amazon"
   - Sign in with your Amazon account
   - Authorize the Alexa skill
3. **Verify Status**: Check `https://home.garrettorick.com/status`

## Integration with Music Assistant

1. Open Music Assistant
2. Go to **Settings** → **Providers**
3. Enable **Alexa** provider
4. Your Alexa devices should appear as playable devices in Music Assistant

## Troubleshooting

### Setup page not loading
- Verify HTTPS is working: `curl https://home.garrettorick.com/setup`
- Check add-on logs in Home Assistant
- Ensure SSL certificate is valid for home.garrettorick.com

### Devices not detecting
- Check Music Assistant is running and accessible
- Verify `MA_HOSTNAME` is correctly set to reach Music Assistant
- Review add-on logs for connection errors

### Amazon authentication fails
- Use a strong password for API credentials
- Ensure you have valid Amazon account with Alexa devices
- Try again after waiting a few minutes

## Support

For issues or questions:
- GitHub: https://github.com/alams154/music-assistant-alexa-skill-prototype
- Music Assistant: https://music-assistant.io/

## License

See repository for license information.
