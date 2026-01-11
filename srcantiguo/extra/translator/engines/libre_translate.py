# -*- coding: utf-8 -*-
""" Modified Libretranslatepy module which adds an user agent for making requests against more instances. """
import json
from typing import Any, Dict
from urllib import request, parse
from libretranslatepy import LibreTranslateAPI

class CustomLibreTranslateAPI(LibreTranslateAPI):
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    def _create_request(self, url: str, method: str, data: Dict[str, str]) -> request.Request:
        url_params = parse.urlencode(data)
        req = request.Request(url, method=method, data=url_params.encode())
        req.add_header("User-Agent", self.USER_AGENT)
        return req

    def translate(self, q: str, source: str = "en", target: str = "es", timeout: int | None = None) -> Any:
        url = self.url + "translate"
        params: Dict[str, str] = {"q": q, "source": source, "target": target}
        if self.api_key is not None:
            params["api_key"] = self.api_key
        req = self._create_request(url=url, method="POST", data=params)
        response = request.urlopen(req, timeout=timeout)
        response_str = response.read().decode()
        return json.loads(response_str)["translatedText"]

    def detect(self, q: str, timeout: int | None = None) -> Any:
        url = self.url + "detect"
        params: Dict[str, str] = {"q": q}
        if self.api_key is not None:
            params["api_key"] = self.api_key
        req = self._create_request(url=url, method="POST", data=params)
        response = request.urlopen(req, timeout=timeout)
        response_str = response.read().decode()
        return json.loads(response_str)

    def languages(self, timeout: int | None = None) -> Any:
        url = self.url + "languages"
        params: Dict[str, str] = dict()
        if self.api_key is not None:
            params["api_key"] = self.api_key
        req = self._create_request(url=url, method="GET", data=params)
        response = request.urlopen(req, timeout=timeout)
        response_str = response.read().decode()
        return json.loads(response_str)