"""
Simple Moodle API wrapper for Python.

Author: EvickaStudio
Data: 07.10.2023
Github: @EvickaStudio
"""


import logging
import os
from typing import Optional

import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


class MoodleAPI:
    """
    A simple Moodle API wrapper for Python.
    ....
    """

    def __init__(self, url: Optional[str] = None) -> None:
        """
        Initializes the MoodleAPI object with the provided API URL.
        """
        self.url = url or os.getenv("MOODLE_URL")
        self.session = requests.Session()
        self.request_header = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.1; ...) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.99 Mobile Safari/537.36 MoodleMobile",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        self.session.headers.update(self.request_header)
        self.token = None
        self.userid = None

    def login(self, username: str, password: str) -> bool:
        """
        Logs in to the Moodle instance using the provided username and password.
        Sets the token for the MoodleAPI object.
        ....
        Args:
            username (str): Moodle username.
            password (str): Moodle password.
        ....
        Returns:
            bool: True if login is successful, False otherwise.
        ....
        Raises:
            ValueError: If username or password is not provided.
        """
        if not username:
            raise ValueError("Username is required")
        if not password:
            raise ValueError("Password is required")

        login_data = {
            "username": username,
            "password": password,
            "service": "moodle_mobile_app",
        }

        try:
            response = self.session.post(
                f"{self.url}/login/token.php", data=login_data
            )
            response.raise_for_status()

            if "token" in response.json():
                self.token = response.json()["token"]
                logger.info("Login successful")
                return True

            logger.error("Login failed: Invalid credentials")
            return False

        except RequestException as e:
            logger.error("Request to Moodle failed: %s", e)
            return False

    def get_site_info(self) -> dict | None:
        """
        Retrieves site information from the Moodle instance.
        ....
        Returns:
            dict: A dictionary containing site information.
        """
        if self.token is None:
            logger.error("Token not set. Please login first.")
            return None

        wsfunction = "core_webservice_get_site_info"
        params = {
            "wstoken": self.token,
            "wsfunction": wsfunction,
            "moodlewsrestformat": "json",
        }

        response = self.session.post(
            f"{self.url}/webservice/rest/server.php", params=params
        )
        self.userid = response.json().get("userid")
        return response.json()

    def get_user_id(self) -> int | None:
        """
        Retrieve the user id.
        """
        if self.token is None:
            logger.error("Token not set. Please login first.")
            return None

        result = self.get_site_info()
        return result["userid"] if result else None

    def get_popup_notifications(self, user_id: int) -> dict | None:
        """
        Send a post request to retrieve popup notifications for a user.
        """
        return self._post("message_popup_get_popup_notifications", {"useridto": user_id})

    # ==========================================================================
    #
    # NOTE: This method is not in use, but it's a good example to check for
    #
    # def popup_notification_unread_count(self, user_id: int) -> int | None:
    #     """
    #     Send a post request to retrieve the number of unread popup notifications for a user.
    #     """
    #     result = self._post(
    #         "message_popup_get_unread_popup_notification_count", user_id
    #     )
    #     return result.get("count") if result else None
    #
    # ==========================================================================

    def core_user_get_users_by_field(self, user_id: int) -> dict | None:
        """
        Send a post request to retrieve user info based on user id.
        """
        if self.token is None:
            logger.error("Token not set. Please login first.")
            return None

        wsfunction = "core_user_get_users_by_field"
        params = {
            "wstoken": self.token,
            "wsfunction": wsfunction,
            "field": "id",
            "values[0]": user_id,
            "moodlewsrestformat": "json",
        }

        response = self.session.post(
            f"{self.url}/webservice/rest/server.php", params=params
        )
        return response.json()


    def get_course(self, user_id: int) -> dict | None:
        """
        Send a post request to retrieve course info based on user id.
        """
        return self._post("core_enrol_get_users_courses", {"userid": user_id})

    def get_course_content(self, course_id: int) -> dict | None:
        """
        Send a post request to retrieve course content based on user id and course id.
        """
        if self.token is None:
            logger.error("Token not set. Please login first.")
            return None

        wsfunction = "core_course_get_contents"
        params = {
            "wstoken": self.token,
            "wsfunction": wsfunction,
            "courseid": course_id,
            "moodlewsrestformat": "json",
        }

        response = self.session.post(
            f"{self.url}/webservice/rest/server.php", params=params
        )
        return response.json()

    def get_groupselect_details(self, instance_id: int) -> dict | None:
        """
        Send a post request to retrieve group details for a groupselect module.
        """
        if self.token is None:
            logger.error("Token not set. Please login first.")
            return None

        wsfunction = "mod_groupselect_get_groups"
        params = {
            "wstoken": self.token,
            "wsfunction": wsfunction,
            "instanceid": instance_id,
            "moodlewsrestformat": "json",
        }

        response = self.session.post(
            f"{self.url}/webservice/rest/server.php", params=params
        )
        return response.json()

    def get_activity_allowed_groups(self, activityid: int) -> dict | None:
        """
        Retrieves groups allowed in a specific activity.
        """
        if self.token is None:
            logger.error("Token not set. Please login first.")
            return None

        wsfunction = "core_group_get_activity_allowed_groups"
        params = {
            "wstoken": self.token,
            "wsfunction": wsfunction,
            "activityid": activityid,
            "moodlewsrestformat": "json",
        }

        response = self.session.post(
            f"{self.url}/webservice/rest/server.php", params=params
        )
        return response.json()

    def get_course_groups(self, courseid: int) -> dict | None:
        """
        Retrieves all groups in a course.
        """
        if self.token is None:
            logger.error("Token not set. Please login first.")
            return None

        wsfunction = "core_group_get_course_groups"
        params = {
            "wstoken": self.token,
            "wsfunction": wsfunction,
            "courseid": courseid,
            "moodlewsrestformat": "json",
        }

        response = self.session.post(
            f"{self.url}/webservice/rest/server.php", params=params
        )
        return response.json()

    def get_groupselect_groups(self, instance_id: int) -> dict | None:
        """
        Retrieves groups for a groupselect instance.
        """
        if self.token is None:
            logger.error("Token not set. Please login first.")
            return None

        wsfunction = "mod_groupselect_get_groups"
        params = {
            "wstoken": self.token,
            "wsfunction": wsfunction,
            "instanceid": instance_id,
            "moodlewsrestformat": "json",
        }

        try:
            response = self.session.post(
                f"{self.url}/webservice/rest/server.php", data=params
            )
            response.raise_for_status()
            result = response.json()
            if 'exception' in result:
                logger.error(f"API Error: {result['exception']} - {result.get('message', '')}")
                return None
            print("API Response from get_groupselect_groups:", result)  # Debugging line
            return result
        except RequestException as e:
            logger.error(f"Request to Moodle failed: {e}")
            return None

    def get_group_members(self, groupid: int) -> dict | None:
        """
        Retrieves members of a group.
        """
        if self.token is None:
            logger.error("Token not set. Please login first.")
            return None

        wsfunction = "core_group_get_group_members"
        params = {
            "wstoken": self.token,
            "wsfunction": wsfunction,
            "groupids[0]": groupid,
            "moodlewsrestformat": "json",
        }

        response = self.session.post(
            f"{self.url}/webservice/rest/server.php", params=params
        )
        return response.json()

    def _post(self, wsfunction: str, additional_params: dict = None) -> dict | None:
        """Send a POST request to the Moodle API with given wsfunction and parameters."""
        if self.token is None:
            logger.error("Token not set. Please login first.")
            return None

        params = {
            "wstoken": self.token,
            "wsfunction": wsfunction,
            "moodlewsrestformat": "json",
        }

        if additional_params:
            params.update(additional_params)

        try:
            response = self.session.post(
                f"{self.url}/webservice/rest/server.php", data=params
            )
            response.raise_for_status()
            result = response.json()
            if "exception" in result:
                logger.error(
                    f"API Error: {result['exception']} - {result.get('message', '')}"
                )
                return None
            return result
        except RequestException as e:
            logger.error(f"Request to Moodle failed: {e}")
            return None
