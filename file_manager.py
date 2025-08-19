import csv
import json
import yaml
from abc import ABC, abstractmethod
from loguru import logger
from typing import Any, Dict, List, Union


class FileManager(ABC):

    @abstractmethod
    def read(self, filepath: str) -> Any:
        pass

    @abstractmethod
    def write(self, filepath: str, data: Any, mode: str = "w"):
        pass

    def _log_write_success(self, filepath: str, mode: str):
        logger.info(f"Successfully wrote data to '{filepath}' with mode '{mode}'")


class JsonManager(FileManager):

    def read(self, filepath: str) -> Union[Dict, List]:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def write(self, filepath: str, data: Any, mode: str = "w", indent: int = 4):

        if mode != "w":
            logger.warning(
                "JSON files are typically overwritten (mode='w'). Using append or other modes may corrupt the file."
            )

        with open(filepath, mode, encoding="utf-8") as f:
            json.dump(data, f, indent=indent)
        self._log_write_success(filepath, mode)


class YamlManager(FileManager):

    def read(self, filepath: str) -> Union[Dict, List]:
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def write(self, filepath: str, data: Any, mode: str = "w"):

        if mode != "w":
            logger.warning(
                "YAML files are typically overwritten (mode='w'). Using append or other modes may corrupt the file."
            )

        with open(filepath, mode, encoding="utf-8") as f:
            yaml.safe_dump(data, f)
        self._log_write_success(filepath, mode)


class CsvManager(FileManager):

    def read(self, filepath: str) -> List[Dict]:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [row for row in reader]

    def write(self, filepath: str, data: List[Dict], mode: str = "w"):
        if not data:
            logger.warning(f"Data is empty. Nothing will be written to '{filepath}'.")
            return

        if not isinstance(data, list) or not all(isinstance(d, dict) for d in data):
            raise TypeError("Data for CSV must be a list of dictionaries.")

        fieldnames = data[0].keys()

        with open(filepath, mode, newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if mode == "w":  # 只有在写入新文件时才写入表头
                writer.writeheader()
            writer.writerows(data)
        self._log_write_success(filepath, mode)


class TxtManager(FileManager):

    def read(self, filepath: str) -> str:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def write(self, filepath: str, data: str, mode: str = "w"):
        if not isinstance(data, str):
            raise TypeError("Data for TXT must be a string.")

        with open(filepath, mode, encoding="utf-8") as f:
            f.write(data)
        self._log_write_success(filepath, mode)


_FILE_MANAGERS = {
    "json": JsonManager,
    "yaml": YamlManager,
    "yml": YamlManager,
    "csv": CsvManager,
    "txt": TxtManager,
}


def get_file_manager(file_type: str) -> FileManager:

    file_manager_class = _FILE_MANAGERS.get(file_type.lower())
    if not file_manager_class:
        raise ValueError(f"Unsupported file type: {file_type}")
    return file_manager_class()
