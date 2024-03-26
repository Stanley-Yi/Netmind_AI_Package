"""
===============
OpenAIKeyHolder
===============
@file_name: openai_key_holder.py
@author: Bin Liang
@date: 2024-03-22

"""


from typing import List
import os


class OpenAIKeyHolder:
    """
    A class for holding the OpenAI key.

    Parameters
    ----------
    key : str
        The OpenAI key.
    """

    def __init__(self, keys: List[str]):
        self.keys = keys
        self.point = 0
        self.set_key()

    def set_key(self):
        os.environ["OPENAI_API_KEY"] = self.keys[self.point]

    def change_key(self):

        self.point += 1
        if self.point == len(self.keys):
            raise ValueError("All the key is used up.")
        self.set_key()




