import base64
import random
import requests
from seleniumbase import SB


def get_geo_data():
    try:
        data = requests.get("http://ip-api.com/json/", timeout=5).json()
        return {
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "timezone": data.get("timezone"),
            "lang": data.get("countryCode", "").lower(),
        }
    except Exception:
        return {"lat": None, "lon": None, "timezone": "UTC", "lang": "en"}


def decode_name(encoded):
    try:
        return base64.b64decode(encoded).decode("utf-8")
    except Exception:
        return encoded


def click_if_present(driver, selector, timeout=4):
    if driver.is_element_present(selector):
        driver.cdp.click(selector, timeout=timeout)


def open_stream(driver, url, timezone, geoloc):
    driver.activate_cdp_mode(url, tzone=timezone, geoloc=geoloc)
    driver.sleep(3)

    click_if_present(driver, 'button:contains("Accept")')
    driver.sleep(3)

    driver.sleep(6)
    click_if_present(driver, 'button:contains("Start Watching")')
    driver.sleep(3)
    click_if_present(driver, 'button:contains("Accept")')


def main():
    geo = get_geo_data()
    latitude = geo["lat"]
    longitude = geo["lon"]
    timezone_id = geo["timezone"]

    proxy_str = False

    encoded_name = "YnJ1dGFsbGVz"
    full_name = decode_name(encoded_name)

    url = f"https://www.twitch.tv/{full_name}"

    while True:
        with SB(
            uc=True,
            locale="en",
            ad_block=True,
            chromium_arg="--disable-webgl",
            proxy=proxy_str
        ) as driver:

            rnd = random.randint(450, 800)

            open_stream(driver, url, timezone_id, (latitude, longitude))

            # If stream is live
            if driver.is_element_present("#live-channel-stream-information"):

                click_if_present(driver, 'button:contains("Accept")')

                # Spawn second viewer
                viewer2 = driver.get_new_driver(undetectable=True)
                viewer2.activate_cdp_mode(url, tzone=timezone_id, geoloc=(latitude, longitude))
                viewer2.sleep(13)

                click_if_present(viewer2, 'button:contains("Start Watching")')
                viewer2.sleep(4)
                click_if_present(viewer2, 'button:contains("Accept")')

                driver.sleep(rnd)

            else:
                break


if __name__ == "__main__":
    main()
