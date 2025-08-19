import threading
import time
import sys

from openai import OpenAI, APIStatusError, RateLimitError, APIError
from loguru import logger


class Chatbot:
    """
    A thread-safe API client manager with API key rotation, intelligent failover,
    and a cooldown mechanism.
    This version has been optimized to handle configurations from a nested YAML dictionary.
    """

    def __init__(self, model: str, llm_config: dict):
        self.model = model
        self.api_states = []
        self._lock = threading.Lock()
        self._current_api_index = 0
        self.cooldown_period = 300  # Default cooldown period in seconds (5 minutes)
        self.max_attempts_per_prompt = 5

        # Set temperature and max_tokens as instance attributes, to be read from the config.
        self.temperature = 0.7
        self.max_tokens = 4096

        # Call the new initialization method, which accepts the full llm config dictionary.
        self._initialize_clients(llm_config.get(self.model, {}))

        if not self.api_states:
            logger.error(
                "No available API clients were successfully initialized. Please check your configuration."
            )
            sys.exit(1)

    def _initialize_clients(self, llm_config_dict: dict):
        """
        Initializes API clients based on the YAML config dictionary.
        A separate client instance is created for each API key under each model.
        """

        base_url = llm_config_dict.get("base_url")
        model_name = llm_config_dict.get("model")
        api_keys = llm_config_dict.get("api_keys", [])

        # Load temperature and max_tokens from the config.
        # If not present in the config, the default value will be used.
        self.temperature = llm_config_dict.get("temperature", self.temperature)
        self.max_tokens = llm_config_dict.get("max_tokens", self.max_tokens)

        if not base_url or not model_name or not api_keys:
            logger.warning(
                f"Incomplete configuration for '{self.model}', skipping. Missing base_url, model, or api_keys."
            )

        for i, api_key in enumerate(api_keys):
            try:
                client_instance = OpenAI(base_url=base_url, api_key=api_key)
                self.api_states.append(
                    {
                        "is_available": True,
                        "last_failure_time": 0,
                        "client": client_instance,
                        "model_name": model_name,
                        "name": f"{self.model}-{i}@{base_url}",  # Name includes key index for easy tracking.
                    }
                )
            except Exception as e:
                logger.warning(
                    f"Failed to initialize API client for key {i} of {self.model}: {e}"
                )

    def _get_next_available_client(self):
        """
        Thread-safely cycles through and returns the next available API client.
        """
        with self._lock:
            num_apis = len(self.api_states)
            if num_apis == 0:
                return None, None, None

            for _ in range(num_apis):
                api_info = self.api_states[self._current_api_index]

                if not api_info["is_available"] and (
                    time.time() - api_info["last_failure_time"]
                    > api_info.get("cooldown_until", self.cooldown_period)
                ):
                    api_info["is_available"] = True
                    api_info["last_failure_time"] = 0
                    logger.info(
                        f"API '{api_info['name']}' cooldown period over. Resetting to available."
                    )

                if api_info["is_available"]:
                    temp_client = api_info["client"]
                    temp_model_name = api_info["model_name"]
                    temp_api_name = api_info["name"]
                    self._current_api_index = (self._current_api_index + 1) % num_apis
                    return temp_client, temp_model_name, temp_api_name

                self._current_api_index = (self._current_api_index + 1) % num_apis

            return None, None, None

    def call(
        self, prompt: str, system_prompt: str = "You are a helpful assistant."
    ) -> str:
        """
        Makes a robust API call with retry logic and error handling.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        for attempt in range(self.max_attempts_per_prompt):
            client, model_name, api_name = self._get_next_available_client()

            if client is None:
                logger.warning(
                    f"All API clients are currently unavailable. No retry attempts left."
                )
                break

            logger.info(
                f"Attempting API call with '{api_name}' (Attempt {attempt + 1}/{self.max_attempts_per_prompt})..."
            )

            try:
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                return str(completion.choices[0].message.content).strip()

            except RateLimitError as e:
                logger.warning(f"API '{api_name}' reached rate limit: {e}")
                with self._lock:
                    for api_info in self.api_states:
                        if api_info["client"] == client:
                            retry_after = e.response.headers.get("retry-after")
                            delay = (
                                int(retry_after)
                                if retry_after
                                else self.cooldown_period
                            )
                            api_info["is_available"] = False
                            api_info["last_failure_time"] = time.time()
                            api_info["cooldown_until"] = delay
                            logger.info(
                                f"API '{api_name}' has been marked as unavailable, cooling down for {delay} seconds."
                            )
                            break

            except APIStatusError as e:
                logger.error(
                    f"API '{api_name}' returned a permanent status error: {e}. This API will be permanently disabled."
                )
                with self._lock:
                    self.api_states = [
                        api for api in self.api_states if api["client"] != client
                    ]
                    if not self.api_states:
                        logger.error("All API clients have been permanently disabled.")
                        break

            except APIError as e:
                logger.error(f"API '{api_name}' returned an APIError: {e}")
                with self._lock:
                    for api_info in self.api_states:
                        if api_info["client"] == client:
                            api_info["is_available"] = False
                            api_info["last_failure_time"] = time.time()
                            logger.info(
                                f"API '{api_name}' has been marked as unavailable, cooling down."
                            )
                            break

            except Exception as e:
                logger.error(f"API '{api_name}' failed with an unknown error: {e}")
                with self._lock:
                    for api_info in self.api_states:
                        if api_info["client"] == client:
                            api_info["is_available"] = False
                            api_info["last_failure_time"] = time.time()
                            logger.info(
                                f"API '{api_name}' has been marked as unavailable, cooling down."
                            )
                            break

        logger.error(
            f"Error: All available APIs failed after {self.max_attempts_per_prompt} attempts."
        )
        return "Error: Could not generate content after multiple attempts."
