from dotenv import load_dotenv
from .facebook.login import FacebookLogIn
from .facebook.account.account import AccountScraper
from .facebook.account.friends import FriendListScraper
from .facebook.account.place_recent import FacebookRecentPlaces
from .facebook.account.image import FacebookImageScraper
from .facebook.account.reels import FacebookReelsScraper
from .facebook.account.videos import FacebookVideoScraper
from .facebook.account.reviews import FacebookReviewsScraper
from typing import Optional
import typer
from src.cli.home import display_start_menu
from rich import print as rprint
from src.cli.version import return_version_info
import subprocess


load_dotenv()
app = typer.Typer()

""" Fastapi """


def server():
    """Run local server to browse scraped data"""
    try:
        build_command = ["docker-compose", "build"]
        subprocess.run(build_command, check=True)

        run_command = ["docker-compose", "up", "-d"]
        subprocess.run(run_command, check=True)

    except subprocess.CalledProcessError as e:
        rprint(f"An error occurred while building the server: {e}")


""" Project commands """


def home():
    """Display basic information about the project"""

    display_start_menu()


def version():
    """Display data about the project version"""

    return_version_info()


""" Log In commands """


def login_2_step():
    """Log in to facebook account with 2-step authentication"""

    facebook = FacebookLogIn()
    facebook.login_2_step_pipeline()

    if facebook.is_pipeline_successful:
        rprint("✅Logging successful✅")
    else:
        rprint("❌Logging failed❌")


def login():
    """Log in to facebook account without 2-step authentication"""

    facebook = FacebookLogIn()
    facebook.login_no_verification_pipeline()

    if facebook.is_pipeline_successful:
        rprint("✅Logging successful✅")
    else:
        rprint("❌Logging failed❌")


""" Account basic data commands """


def scrape_full_account(name: Optional[str] = None):
    """Scrape data from facebook account:
    - full name
    - places
    - family members
    - work and education
    """

    rprint(f"Start scraping all data from {name} account")
    scraper = AccountScraper(name)
    scraper.pipeline()

    if scraper.is_pipeline_successful:
        rprint("✅Scraping successful✅")
    else:
        rprint("❌Scraping failed❌")


def scrape_work_and_education(name: Optional[str] = None):
    """Scrape work and education history data"""

    rprint(f"Start scraping work and education data from {name} account")
    scraper = AccountScraper(name)
    scraper.work_and_education_pipeline()

    if scraper.is_pipeline_successful:
        rprint("✅Scraping successful✅")
    else:
        rprint("❌Scraping failed❌")


def scrape_localization(name: Optional[str] = None):
    """Scrape visited places"""

    rprint(f"Start scraping localization data from {name} account")
    scraper = AccountScraper(name)
    scraper.localization_pipeline()

    if scraper.is_pipeline_successful:
        rprint("✅Scraping successful✅")
    else:
        rprint("❌Scraping failed❌")


def scrape_family_member(name: Optional[str] = None):
    """Scrape family member data"""

    rprint(f"Start scraping family member data from {name} account")
    scraper = AccountScraper(name)
    scraper.family_member_pipeline()

    if scraper.is_pipeline_successful:
        rprint("✅Scraping successful✅")
    else:
        rprint("❌Scraping failed❌")


def scrape_full_name(name: Optional[str] = None):
    """Scrape full name from facebook account"""

    rprint(f"Start scraping full name data from {name} account")
    scraper = AccountScraper(name)
    scraper.full_name_pipeline()

    if scraper.is_pipeline_successful:
        rprint("✅Scraping successful✅")
    else:
        rprint("❌Scraping failed❌")


""" Friend list commands """


def scrape_friend_list(name: Optional[str] = None):
    """Scrape friend list from facebook account"""

    rprint(f"Start scraping friend list for {name}")
    scraper = FriendListScraper(name)
    scraper.pipeline()

    if scraper.is_pipeline_successful:
        rprint("✅Scraping successful✅")
    else:
        rprint("❌Scraping failed❌")


""" Image scraper commands """


def scrape_images(name: Optional[str] = None):
    """Scrape images from facebook account"""

    rprint(f"Start scraping images for {name}")
    scraper = FacebookImageScraper(name)
    scraper.pipeline()

    if scraper.is_pipeline_successful:
        rprint("✅Scraping successful✅")
    else:
        rprint("❌Scraping failed❌")


""" Recent place scraper commands """


def scrape_recent_places(name: Optional[str] = None):
    """Scrape recent places from facebook account"""

    rprint(f"Start scraping recent places for {name}")
    scraper = FacebookRecentPlaces(name)
    scraper.pipeline()

    if scraper.is_pipeline_successful:
        rprint("✅Scraping successful✅")
    else:
        rprint("❌Scraping failed❌")


""" Reels scraper commands """


def scrape_reels(name: Optional[str] = None):
    """Scrape reels urls from facebook account"""

    rprint(f"Start scraping reels for {name}")
    scraper = FacebookReelsScraper(name)
    scraper.pipeline()

    if scraper.is_pipeline_successful:
        rprint("✅Scraping successful✅")
    else:
        rprint("❌Scraping failed❌")


""" Reviews scraper commands """


def scrape_reviews(name: Optional[str] = None):
    """Scrape written reviews from facebook account"""

    rprint(f"Start scraping reviews for {name}")
    scraper = FacebookReviewsScraper(name)
    scraper.pipeline()

    if scraper.is_pipeline_successful:
        rprint("✅Scraping successful✅")
    else:
        rprint("❌Scraping failed❌")


""" Videos scraper commands """


def scrape_videos(name: Optional[str] = None):
    """Scrape videos urls from facebook account"""

    rprint(f"Start scraping reels for {name}")
    scraper = FacebookVideoScraper(name)
    scraper.pipeline()

    if scraper.is_pipeline_successful:
        rprint("✅Scraping successful✅")
    else:
        rprint("❌Scraping failed❌")
