# carter
My personal discord bot

A docker image is a available for this bot, run it with the following command (replace the enviroment variables)

```bash
docker run -e BOT_TOKEN={YOUR_BOT_TOKEN} -e STREETVIEW_API_KEY{YOUR_GOOGLE_MAPS_KEY} ghcr.io/tylermg2/carter:main
```

You can create a discord bot token at (Discord Developers)[https://discord.com/developers/applications] and you can create a streetview API token at (Maps API)[https://console.cloud.google.com/google/maps-apis/].

The bot utilizes googles metadata api for fetching panorama ids which is completely free to use, you can read more (here)[https://developers.google.com/maps/documentation/streetview/metadata].
