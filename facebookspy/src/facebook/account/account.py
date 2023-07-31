import logging
from typing import List, Dict
from ...config import Config
from selenium.webdriver.common.by import By
from ..facebook_base import BaseFacebookScraper
from rich import print as rprint
from ...repository import (
    person_exists,
    create_person,
    create_places,
    create_work_and_education,
    create_family_member,
    get_person,
)


# Logging setup
logging.basicConfig(
    filename=Config.LOG_FILE_PATH,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class AccountScraper(BaseFacebookScraper):
    """
    Scrape user's personal information
    """

    def __init__(self, user_id) -> None:
        super().__init__(user_id, base_url=f"https://www.facebook.com/{user_id}")
        self.success = False

    def extract_full_name(self) -> str | None:
        """Extract full name from homepage"""
        data = None
        try:
            self._driver.get(self._base_url)
            fullname_element = self._driver.find_element(
                By.CSS_SELECTOR, "h1.x1heor9g.x1qlqyl8.x1pd3egz.x1a2a7pz"
            )
            data = fullname_element.text.strip()

        except Exception as e:
            logging.error(f"Error occurred while extracting full name: {e}")

        return data

    def extract_work_and_education(self) -> List[Dict[str, str]]:
        """Return employment and education history"""

        extracted_work_data = []
        try:
            self._driver.get(f"{self._base_url}/{Config.WORK_AND_EDUCATION_URL}")

            work_entries = self._driver.find_elements(
                By.CSS_SELECTOR,
                "div.x9f619.x1n2onr6.x1ja2u2z.x78zum5.x1nhvcw1.x1qjc9v5.xozqiw3.x1q0g3np.xexx8yu.xykv574.xbmpl8g.x4cne27.xifccgj.xs83m0k",
            )
            for entry in work_entries:
                owner_element = entry.find_element(By.XPATH, ".//span[@dir='auto']")
                owner = owner_element.text.strip()

                if owner.startswith("http") or owner.startswith("www"):
                    work_entry_data = {"name": owner}
                else:
                    work_entry_data = {"name": owner}

                extracted_work_data.append(work_entry_data)

        except Exception as e:
            logging.error(f"Error extracting work data: {e}")

        return extracted_work_data

    def extract_places(self) -> List[Dict[str, str]]:
        """Return history of places"""
        places = []
        try:
            self._driver.get(f"{self._base_url}/{Config.PLACES_URL}")

            div_elements = self._driver.find_elements(
                By.CSS_SELECTOR, "div.x13faqbe.x78zum5"
            )

            for div_element in div_elements:
                name_element = div_element.find_element(
                    By.CSS_SELECTOR, "a[class*='x1i10hfl']"
                )
                name = name_element.text.strip()

                date_element = div_element.find_element(
                    By.CSS_SELECTOR, "div span[class*='xi81zsa']"
                )
                date = date_element.text.strip()

                places.append({"name": name, "date": date})

        except Exception as e:
            logging.error(f"Error extracting localization data: {e}")

        return places

    def extract_family(self) -> List[Dict[str, str]]:
        """Return family members"""
        data = []
        try:
            self._driver.get(f"{self._base_url}/{Config.FAMILY_URL}")

            elements = self._driver.find_elements(By.CSS_SELECTOR, "div.x1hq5gj4")

            for element in elements:
                name_element = element.find_element(
                    By.CSS_SELECTOR,
                    "span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.xudqn12.x3x7a5m.x6prxxf.xvq8zen.xo1l8bm.xzsf02u a",
                )
                name = name_element.text
                profile_url = name_element.get_attribute("href")
                relationship_element = element.find_element(
                    By.CSS_SELECTOR, "span.xi81zsa.x1nxh6w3.x1sibtaa"
                )
                relationship = relationship_element.text

                data.append(
                    {"name": name, "relationship": relationship, "url": profile_url}
                )
        except Exception as e:
            logging.error(f"Error extracting family data: {e}")

        return data

    @property
    def is_pipeline_successful(self) -> bool:
        """Check if pipeline is successful"""
        return self.success

    def work_and_education_pipeline(self) -> None:
        """
        Pipeline to run extract work and education data
        """
        try:
            rprint("[bold]Step 1 of 3 - Load cookies[/bold]")
            self._load_cookies()

            rprint("[bold]Step 2 of 3 - Refresh driver[/bold]")
            self._driver.refresh()

            if not person_exists(self._user_id):
                create_person(self._user_id)

            person_id = get_person(self._user_id).id

            rprint("[bold]Step 3 of 3 - Extract work and education data[/bold]")
            work_and_education = self.extract_work_and_education()
            for data in work_and_education:
                create_work_and_education(data["name"], person_id)
                rprint(f"[cyan]{data['name']}[/cyan]")

            self._driver.quit()

            self.success = True
        except Exception as e:
            logging.error(f"Error running pipeline: {e}")
            rprint(f"[bold red]Something went wrong[/bold red] {e}")

    def localization_pipeline(self) -> None:
        """
        Pipeline to return localization data
        """
        try:
            rprint("[bold]Step 1 of 4 - Load cookies[/bold]")
            self._load_cookies()

            rprint("[bold]Step 2 of 4 - Refresh driver[/bold]")
            self._driver.refresh()

            rprint("[bold]Step 3 of 4 - Extract full name[/bold]")

            if not person_exists(self._user_id):
                create_person(self._user_id)

            person_id = get_person(self._user_id).id

            rprint("[bold]Step 4 of 4 - Extract localization data[/bold]")
            places = self.extract_places()
            for place in places:
                create_places(place["name"], place["date"], person_id)
                rprint(f"[cyan]{place['name']}[/cyan] - [blue]{place['date']}[/blue]")

            self._driver.quit()

            self.success = True
        except Exception as e:
            logging.error(f"Error running pipeline: {e}")
            rprint(f"[bold red]Something went wrong[/bold red] {e}")

    def family_member_pipeline(self) -> None:
        """
        Pipeline to extract family members data
        """
        try:
            rprint("[bold]Step 1 of 3 - Load cookies[/bold]")
            self._load_cookies()

            rprint("[bold]Step 2 of 3 - Refresh driver[/bold]")
            self._driver.refresh()

            if not person_exists(self._user_id):
                create_person(self._user_id)

            person_id = get_person(self._user_id).id

            rprint("[bold]Step 3 of 3 - Extract family members[/bold]")
            family_members = self.extract_family()
            for member in family_members:
                create_family_member(
                    member["name"],
                    member["relationship"],
                    member["url"],
                    person_id,
                )
                rprint(
                    f"[cyan]{member['name']}[/cyan] - [magenta]{member['relationship']}[/magenta] - [blue]{member['url']}[/blue]"
                )

            self._driver.quit()

            self.success = True
        except Exception as e:
            logging.error(f"Error running pipeline: {e}")
            rprint(f"[bold red]Something went wrong[/bold red] {e}")

    def full_name_pipeline(self) -> None:
        """
        Pipeline to extract full name data
        """
        try:
            rprint("[bold]Step 1 of 3 - Load cookies[/bold]")
            self._load_cookies()

            rprint("[bold]Step 2 of 3 - Refresh driver[/bold]")
            self._driver.refresh()

            rprint("[bold]Step 3 of 3 - Extract full name[/bold]")
            full_name = self.extract_full_name()
            rprint(f"[cyan]{full_name}[/cyan]")

            if not person_exists(self._user_id):
                create_person(self._user_id, full_name)

            self._driver.quit()

            self.success = True
        except Exception as e:
            logging.error(f"Error running pipeline: {e}")
            rprint(f"[bold red]Something went wrong[/bold red] {e}")

    def pipeline(self) -> None:
        """
        Pipeline to run full script
        """
        try:
            rprint("[bold]Step 1 of 6 - Load cookies[/bold]")
            self._load_cookies()

            rprint("[bold]Step 2 of 6 - Refresh driver[/bold]")
            self._driver.refresh()

            rprint("[bold]Step 3 of 6 - Extract full name[/bold]")
            full_name = self.extract_full_name()
            rprint(f"[cyan]{full_name}[/cyan]")

            if not person_exists(self._user_id):
                create_person(self._user_id, full_name)

            person_id = get_person(self._user_id).id

            rprint("[bold]Step 4 of 6 - Extract family members[/bold]")
            family_members = self.extract_family()
            for member in family_members:
                create_family_member(
                    member["name"],
                    member["relationship"],
                    member["url"],
                    person_id,
                )
                rprint(
                    f"[cyan]{member['name']}[/cyan] - [magenta]{member['relationship']}[/magenta] - [blue]{member['url']}[/blue]"
                )

            rprint("[bold]Step 5 of 6 - Extract localization data[/bold]")
            places = self.extract_places()
            for place in places:
                create_places(place["name"], place["date"], person_id)
                rprint(f"[cyan]{place['name']}[/cyan] - [blue]{place['date']}[/blue]")

            rprint("[bold]Step 6 of 6 - Extract work and education data[/bold]")
            work_and_education = self.extract_work_and_education()
            for data in work_and_education:
                create_work_and_education(data["name"], person_id)
                rprint(f"[cyan]{data['name']}[/cyan]")

            self._driver.quit()

            self.success = True
        except Exception as e:
            logging.error(f"Error running pipeline: {e}")
            rprint(f"[bold red]Something went wrong[/bold red] {e}")
