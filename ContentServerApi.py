from pydantic import BaseModel, Field
import requests
import json
from typing import Literal
from loguru import logger
from log_decorator import log_decorator


def print_json(category: str) -> None:
    """ shortcut to print strings in json format
    Args:
        category: to be printed nicely
    """
    print(json.dumps(category, indent=4))


class ContentServerAPI(BaseModel):
    protocol: Literal["http", "https"] = "https"
    hostname: str = Field(..., description="The hostname is a required field!")
    port: int = Field(443, gt=0, description="The Port must be an int greater 0")
    base_path: str = "/cs/cs"
    auth_header: dict = {}
    session: int = requests.Session()

    @log_decorator()
    def authorize(self, user: str, password: str) -> None:
        """ authorize the user agains the CS and stores the ticket in auth_header
        Args:
            user: to be authorized
            password: users password
        """
        auth_data = {"username": user, "password": password}
        url = self._build_full_url("/api/v1/auth")
        response = self.session.post(url, data=auth_data)
        response.raise_for_status()
        self.auth_header = {"OTCSTICKET": response.json().get("ticket")}

    def _printResponse(self, response: requests.Response) -> None:
        """ helper function to pretty print the response from the API
        Args:
            response: the response which is analyzed
        """
        if response.status_code == 200:
            try:
                # Try to parse the response as JSON
                json_response = response.json()
                print("Response Status: OK")
                print("Response JSON:")
                print(json.dumps(json_response, indent=4))  # Pretty print JSON
            except ValueError:
                # If response is not JSON, print text
                print("Response Status: OK")
                print("Response Text:")
                print(response.text)
        else:
            print(f"Error: {response.status_code} - {response.reason}")
            try:
                error_details = response.json()
                print("Error Details:")
                print(json.dumps(error_details, indent=4))  # Pretty print JSON
            except ValueError:
                # If error response is not JSON, print text
                print("Error Details:")
                print(response.text)

    def _build_full_url(self, apiurl: str) -> str:
        """ builds the full url from internal variables
        Args:
            apiurl: the url of the api
        """
        url = f"{self.protocol}://{self.hostname}"
        if self.port != 443:
            url += f":{self.port}"
        url += self.base_path + apiurl
        return url

    def _get_request(self, url: str, results: str = "results") -> dict:
        """ calls the CS API with a get request
        Args:
            url: Url to be called
            results: part of the response where the results are located
        """
        response = self.session.get(url, headers=self.auth_header)
        response.raise_for_status()
        results = response.json().get(results)
        if results is None:
            logger.error(f"No {results} returned!")
            raise ValueError(f"No {results} returned!")
        return results

    def _put_request(self, url: str, data: str, results: str = "results") -> dict:
        """ calls the CS API with a put request
        Args:
            url: Url to be called
            data: json string which is passed in the request in the data section
            results: part of the response where the results are located
        """
        response = self.session.put(url, headers=self.auth_header, data=json.loads(data))
        response.raise_for_status()
        results = response.json().get(results)
        if results is None:
            logger.error(f"No {results} returned!")
            raise ValueError(f"No {results} returned!")
        return results

    def _post_request(self, url: str, data: str, results: str = "results") -> dict:
        """ calls the CS API with a post request
        Args:
            url: Url to be called
            data: json string which is passed in the request in the data section
            results: part of the response where the results are located
        """
        response = self.session.post(url, headers=self.auth_header, data=data)
        response.raise_for_status()
        results = response.json().get(results)
        if results is None:
            logger.error(f"No {results} returned!")
            raise ValueError(f"No {results} returned!")
        return results

    def append_logFormater(self, logRoundtrip):
        self.session.hooks['response'].append(logRoundtrip)