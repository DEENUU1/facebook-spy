from time import sleep
from typing import List, Dict

from ...config import Config
from selenium.webdriver.common.by import By
from ..facebook_base import BaseFacebookScraper
from ...repository import person_repository, review_repository
from ...logs import Logs
from rich import print as rprint


logs = Logs()


class AccountReview(BaseFacebookScraper):
    """
    Scrape user's pictures
    """

    def __init__(self, user_id) -> None:
        super().__init__(
            user_id, base_url=f"https://www.facebook.com/{user_id}/reviews_written"
        )
        self.success = False

    def scroll_page(self) -> None:
        """
        Scrolls the page to load more friends from a list
        """
        try:
            last_height = self._driver.execute_script(
                "return document.body.scrollHeight"
            )
            consecutive_scrolls = 0

            while consecutive_scrolls < Config.MAX_CONSECUTIVE_SCROLLS:
                self._driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )

                sleep(Config.SCROLL_PAUSE_TIME)
                new_height = self._driver.execute_script(
                    "return document.body.scrollHeight"
                )

                if new_height == last_height:
                    consecutive_scrolls += 1
                else:
                    consecutive_scrolls = 0

                last_height = new_height

        except Exception as e:
            logs.log_error(f"Error occurred while scrolling: {e}")

    def extract_reviews(self) -> List[Dict[str, str]]:
        """
        Return data about recent places
        """
        extracted_reviews = []
        try:
            div_elements = self._driver.find_elements(
                By.CSS_SELECTOR,
                "div.x6s0dn4.x1lq5wgf.xgqcy7u.x30kzoy.x9jhf4c.x1olyfxc.x9f619.x78zum5.x1e56ztr.xyamay9.x1pi30zi.x1l90r2v.x1swvt13",
            )

            for div_element in div_elements:
                data = {}
                company_element = div_element.find_element(
                    By.CSS_SELECTOR,
                    "span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.xudqn12.x676frb.x1lkfr7t.x1lbecb7.x1s688f.xzsf02u",
                )
                data["company"] = company_element.text

                div_inside_elements = div_element.find_elements(
                    By.CSS_SELECTOR, "div.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x1vvkbs"
                )

                opinions = [
                    opinion_element.text for opinion_element in div_inside_elements
                ]
                data["opinions"] = opinions

                extracted_reviews.append(data)
        except Exception as e:
            logs.log_error(f"Error extracting image URLs: {e}")

        return extracted_reviews

    @property
    def is_pipeline_successful(self) -> bool:
        return self.success

    def pipeline(self) -> None:
        """
        Pipeline to run the scraper
        """
        try:
            rprint("[bold]Step 1 of 4 - Load cookies[/bold]")
            self._load_cookies()
            rprint("[bold]Step 2 of 4 - Refresh driver[/bold]")
            self._driver.refresh()
            rprint("[bold]Step 3 of 4 - Scrolling page[/bold]")
            self.scroll_page()
            rprint("[bold]Step 4 of 4 - Extract reviews[/bold]")
            reviews = self.extract_reviews()
            rprint(reviews)

            if not person.person_exists(self._user_id):
                person.create_person(self._user_id)

            person_id = person.get_person(self._user_id).id

            for review_data in reviews:
                opinion = "".join([data for data in review_data["opinions"]])
                if not review.review_exists(review_data["company"], opinion, person_id):
                    create_reviews(review_data["company"], opinion, person_id)

            self._driver.quit()
            self.success = True

        except Exception as e:
            logs.log_error(f"An error occurred: {e}")
            rprint(f"An error occurred {e}")