import asyncio
import aiohttp
from dr import fetch_with_retries, save_data, load_existing_data, INDEX_FILE

BASE_URL = 'https://api.dr.dk/radio/v4/series/'

async def main():
    existing_data = load_existing_data(INDEX_FILE)
    
    headers = {
        'x-apikey': 'p0JzsEGfZtTEtP4hodkgI2eFKhrxj4X1',
        'Accept-Encoding': 'gzip',
        'Content-Type': 'application/json',
        'User-Agent': 'okhttp/4.12.0'
    }

    async with aiohttp.ClientSession() as session:
        i = 0
        for podcast in existing_data:
            if 'series_hash' in podcast:
                hash = podcast['series_hash']
                url = BASE_URL + hash
                result = await fetch_with_retries(session, url, headers)
                try:
                    image_url = None
                    image_assets = result['imageAssets']
                    for asset in image_assets:
                        if asset['target'] == 'Default' and asset['ratio'] == '1:1':
                            urn_id = asset.get('id')
                            image_url = f"https://asset.dr.dk/drlyd/images/{urn_id}"
                            break
                    if image_url:
                        podcast['image'] = image_url
                        print(podcast['name'] + " Updated")
                        i += 1
                    else:
                        raise TypeError("No '1:1' image found")
                        
                except (TypeError, KeyError) as e:
                    print(e)
                    print(f"Could not update image for: {podcast['name']} -> {hash}")
                    
    print(f'{i}/{len(existing_data)} podcasts updated.')
    save_data(INDEX_FILE, existing_data)          
            

if __name__ == "__main__":
    asyncio.run(main())