"""
An Instagram Top 9 generator that doesn't require connecting your account
to an untrustworthy 3rd party Instagram app.

Install the requirements with `pip3 install igramscraper Pillow click`
then run `python3 top9.py`

When done, you will have a YOURUSERNAME-top9.jpg in your working directory.
"""
from datetime import datetime

from igramscraper.instagram import Instagram
from PIL import Image
import click
import requests

instagram = Instagram()


@click.command()
@click.option(
    "--user",
    prompt="Your Instagram account (without @)",
    help="The instagram username to create a top 9 for",
)
@click.option(
    "--login-user",
    help="The instagram username to login with. Doesn't log in if omitted.",
)
@click.option(
    "--tfa",
    help="Use two factor auth during login",
)
def top9(user, tfa=False, login_user=None):
    if login_user:
        password = click.prompt("Your Instagram password")
        instagram.with_credentials(login_user, password)
        instagram.login(two_step_verificator=tfa)
    now = datetime.utcnow()
    if now.month > 7:
        this_year = now.year
    else:
        this_year = now.year - 1

    posts = None
    count = 0
    prev = None
    while (
        posts is None
        or datetime.fromtimestamp(posts[-1].created_time).year >= this_year
    ):
        count += 50
        posts = instagram.get_medias(user, count)
        last = datetime.fromtimestamp(posts[-1].created_time)
        if prev == last:
            break
        prev = last

    this_year_photos = [
        post
        for post in posts
        if datetime.fromtimestamp(post.created_time).year == this_year
        and post.type in (post.TYPE_IMAGE, post.TYPE_SIDECAR)
    ]

    top9 = sorted(this_year_photos, key=lambda post: -post.likes_count)[:9]

    img = Image.new("RGB", (1080, 1080))
    for i, post in enumerate(top9):
        tile = Image.open(requests.get(post.image_high_resolution_url, stream=True).raw)
        if tile.size[0] > tile.size[1]:
            tile = tile.crop(
                (
                    (tile.size[0] - tile.size[1]) / 2,
                    0,
                    (tile.size[0] - tile.size[1]) / 2 + tile.size[1],
                    tile.size[1],
                )
            )
        elif tile.size[0] < tile.size[1]:
            tile = tile.crop(
                (
                    0,
                    (tile.size[1] - tile.size[0]) / 2,
                    tile.size[0],
                    (tile.size[1] - tile.size[0]) / 2 + tile.size[0],
                )
            )

        tile = tile.resize((360, 360), Image.ANTIALIAS)
        print(f"{post.likes_count} likes - {post.link}")
        img.paste(tile, (i % 3 * 360, i // 3 * 360))

    img.save(f"{user}-top9.jpg")


if __name__ == "__main__":
    top9()
