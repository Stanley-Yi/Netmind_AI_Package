"""
====================
pai_company_utils.py
====================
@file_name: pai_company_utils.py
@date: 2024-3-21
@author: Bin Liang, Tianlei
"""

from typing import Generator, Tuple


def stream_print(response: Generator, justify_finish: str = "") -> tuple[str, bool]:
    """
    Print the response from the generator.

    Parameters
    ----------
    response : Generator
        The response from the generator.
    justify_finish : str
        The flag to justify if the conversation is finished.

    Returns
    -------
    whole_response : str
        The whole response.
    finish_signal : bool
        The flag to justify if the conversation is finished.
    """

    finish_signal = False

    if justify_finish:
        whole_response = ""
        count = 0
        print_label = True
        for res in response:
            whole_response += res
            if count <= 10:
                if justify_finish in whole_response:
                    finish_signal = False
                    return "", finish_signal
            else:
                if print_label:
                    print(whole_response)
                    print_label = False
                else:
                    print(res, end="")
            count += 1
        if print_label:
            print(whole_response)
    else:
        whole_response = ""
        for res in response:
            print(res, end="")
            whole_response += res

    return whole_response, finish_signal
