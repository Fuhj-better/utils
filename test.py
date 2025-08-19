# import unittest
# from loguru import logger
# import yaml

# from unittest.mock import patch, Mock
# from chatbot import chatbot

# CONFIG_YAML = """
# llm:
#   deepseek_v3:
#     base_url: https://api.siliconflow.cn/v1
#     api_keys:
#       - sk-lachdvjgzjuvdzdvkawvhrrwtkbqzzkxggozevkifqmzevsv
#       - sk-anvunvcupmyexdovhfhizzvbfaugxpnizajojnnvnwdpgmkf
#       - sk-rkwsxudtnxdvfznwflnetjxhquivnifsguthbgkzixprkhte
#     model: deepseek-ai/DeepSeek-V3
#     temperature: 0.7
#     # other configs
# """
# logger.add("app.log")

# def main():
#     config = yaml.safe_load(CONFIG_YAML)
#     print(config)
#     ds=chatbot("deepseek_v3",config.get("llm"))
#     response=ds.call("hello")
#     print(response)

# if __name__ == "__main__":
#     main()


import threading
import time
import yaml
import concurrent.futures

from file_manager import get_file_manager
from chatbot import Chatbot
from loguru import logger

logger.add("app.log")

# Configuration for the LLM APIs.
# This configuration is loaded from a YAML string.
CONFIG_YAML = """
llm:
  deepseek_v3:
    base_url: https://api.siliconflow.cn/v1
    api_keys:
      - sk-lachdvjgzjuvdzdvkawvhrrwtkbqzzkxggozevkifqmzevsv
      - sk-anvunvcupmyexdovhfhizzvbfaugxpnizajojnnvnwdpgmkf
      - sk-rkwsxudtnxdvfznwflnetjxhquivnifsguthbgkzixprkhte
    model: deepseek-ai/DeepSeek-V3
    temperature: 0.7
    max_tokens: 4096
"""

def make_llm_call(chatbot_instance: Chatbot, thread_id: int):
    """
    Function to be executed by each thread.
    It calls the LLM API and logs the response.
    """
    prompt = f"你好，请用中文简单介绍一下线程是什么。来自线程 {thread_id} 的请求。"
    logger.info(f"Thread {thread_id} 开始向LLM发起请求...")
    
    response = chatbot_instance.call(prompt)
    
    logger.info(f"Thread {thread_id} 收到响应:\n{response}")
    logger.info("-" * 50)

def main():
    """
    The main function to set up the multi-threaded calls.
    """
    logger.info("主程序开始运行。")

    # Load the configuration from the YAML string.
    config = yaml.safe_load(CONFIG_YAML)
    
    # Initialize the chatbot instance with the configuration.
    llm_bot = Chatbot("deepseek_v3",config.get("llm"))

    # Number of concurrent threads you want to run.
    num_threads = 5
    
    # Use a ThreadPoolExecutor for efficient thread management.
    # This is a high-level way to run tasks concurrently.
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(make_llm_call, llm_bot, i): i for i in range(num_threads)}
        
        # Wait for all futures to complete.
        for future in concurrent.futures.as_completed(futures):
            # In this example, we don't need to do anything with the results,
            # but you can handle any exceptions here.
            try:
                future.result()
            except Exception as exc:
                logger.error(f"线程执行时发生异常: {exc}")

    logger.info("所有线程已完成执行。")
    logger.info("请查看 'app.log' 文件以获取完整的日志输出。")

if __name__ == "__main__":
    # main()
  csv_path = 'users.csv'
  my_users = [
      {'id': 1, 'name': 'Alice', 'age': 30},
      {'id': 2, 'name': 'Bob', 'age': 25},
      {'id': 3, 'name': 'Charlie', 'age': 35}
  ]

  csv_manager = get_file_manager("csv")
  csv_manager.write(csv_path, my_users,'a')    
