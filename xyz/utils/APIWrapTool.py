""" 
===========
APIWrapTool
===========
@file_name: APIWrapTool.py
@author: Bin Liang  
@date: 2024-3-6

"""


# python standard packages


# python third-party packages
from fastapi import FastAPI, Body
import uvicorn

# import from our modules



class APIWrapTool:
    """ 
    A tool for wrapping a function into an API.

    Parameters
    ----------
    function : callable
        The function to be wrapped.
    fun_doc : str
        The documentation for the function.
    host : str, optional
        The host to run the API on. Default is "127.0.0.1".
    port : int, optional
        The port to run the API on. Default is 8501.
    servers : list, optional
        A list of servers where the API is available. Default is an empty list.
    """
    
    def __init__(self, function, fun_doc, host="127..0.1", port=8501,
                 servers=[]):
        """
        Initialize the APIWrapTool.

        Parameters
        ----------
        function : callable
            The function to be wrapped.
        fun_doc : str
            The documentation for the function.
        host : str, optional
            The host to run the API on. Default is "127.0.0.1".
        port : int, optional
            The port to run the API on. Default is 8501.
        servers : list, optional
            A list of servers where the API is available. Default is an empty list.
        """
        # TODO: 现在是本地版本的，并不能映射到公网上。
        
        self.function = function
        self.fun_doc = fun_doc
        
        self.host = host
        self.port = port 
        
        if servers:
            self.actions = FastAPI(servers=servers)
        else:
            self.actions = FastAPI()

    def run_api(self):
        """
        Run the API.

        This method wraps the function into two API endpoints: a GET endpoint at "/" that returns the function's documentation, and a POST endpoint at "/process/" that runs the function with the provided input.

        Raises
        ------
        Exception
            If there is an error while running the API.
        """
        # TODO: 现在我们一次只能 wrap 一个 function，但是我们希望能够 wrap 多个 function

        @self.actions.get("/")
        async def root():
            return {"message": self.fun_doc}

        @self.actions.post("/process/")
        async def process(info: dict = Body(...)):
            
            response = self.function(**info)
            
            return {"request": info, "response" : response}

        uvicorn.run(self.actions, host=self.host, port=self.port)

    def get_info(self):
        """
        Get the function's documentation.

        Returns
        -------
        str
            The function's documentation.
        """
        
        return self.fun_doc

    
