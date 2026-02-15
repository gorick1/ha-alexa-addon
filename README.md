# Home Assistant Alexa Add-ons Repository

This repository contains Home Assistant add-ons for integrating Music Assistant with Amazon Alexa devices.

## Add-ons

### Music Assistant Alexa Skill

Enables Music Assistant playback control from Alexa devices and vice versa.

**Features:**
- Detect all Alexa devices linked to your Amazon account
- Control playback (play, pause) on Alexa devices
- Set and mute volume on Alexa devices
- Seamless integration with Music Assistant

**Installation:**

1. In Home Assistant, go to **Settings** → **Add-ons** → **Add-on Store**
2. Click the menu button (⋮) in the top-right corner
3. Select **Repositories**
4. Add this repository URL:
   ```
   https://github.com/garrettorick/ha-alexa-addon
   ```
5. Click **Add**
6. Search for "Music Assistant Alexa Skill"
7. Click **Install**
8. Configure the add-on options if needed
9. Click **Start**

## Configuration

The add-on requires:
- **SKILL_HOSTNAME**: Your external domain (e.g., `home.garrettorick.com`)
- **MA_HOSTNAME**: Music Assistant address (e.g., `127.0.0.1:8097`)
- **API Username & Password**: For the skill's internal API

## Setup

After installing:

1. Navigate to `https://your-domain/setup`
2. Click "Authenticate with Amazon"
3. Sign in with your Amazon account
4. Grant permissions for the Alexa skill
5. The skill will auto-configure itself

## Enable in Music Assistant

1. Open Music Assistant UI
2. Go to Settings → Providers
3. Enable the **Alexa** provider
4. Your Alexa devices will appear as playable speakers

## Troubleshooting

### Setup page won't load
- Ensure your domain has valid HTTPS certificate
- Check that ports are correctly forwarded from your router
- Verify the add-on is running (check logs in HA)

### Amazon authentication fails
- Ensure your Amazon account has Alexa devices linked
- Try again after waiting a few minutes
- Check the add-on logs for detailed error messages

### Alexa devices don't appear in Music Assistant
- Verify Music Assistant is running
- Enable the Alexa provider in Music Assistant settings
- Restart Music Assistant
- Check both add-on and Music Assistant logs

## Support

- **Alexa Skill Prototype**: https://github.com/alams154/music-assistant-alexa-skill-prototype
- **Music Assistant**: https://music-assistant.io/
- **Home Assistant Add-ons**: https://developers.home-assistant.io/docs/add-ons/

## License

This add-on follows the license of the upstream Alexa Skill Prototype repository.

---

**Repository URL**: `https://github.com/garrettorick/ha-alexa-addon`

Add this URL to your Home Assistant add-on repositories to install!
