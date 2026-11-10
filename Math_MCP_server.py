from mcp.server.fastmcp import FastMCP
from typing import Union

mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return int(a) + int(b)

@mcp.tool()
def multiply(a: Union[int, str], b: Union[int, str]) -> int:
    """Multiply two numbers"""
    return int(a) * int(b)

# transport="stdio" argument tells the server to:
#standard input/output(stdin abd stdout) to recieve and  respond to tool function calls.
if __name__ == "__main__":
    mcp.run(transport="stdio") 


'''Ths standard input/output is it like that
if the whole code is server and it is running ,This is specifically run in some kind of Command prompt.Let's say in one of the scenario what we can do that if I have a client  and I want that client to interact with the particular server ten what we will do if we have written this transport is equal to  stdio we will run this particular file directly in the comand prompt and get the input   and output there itself  and get response out there and client should be able to read   the information out directly from the  STDOUT bascially means from the command prompt itself.
so this kind of things  is very helpful if you really want to test out things locally. you have my(your) server excuted in the locally itself and test it with the client.That point of time we use STDIO'''

