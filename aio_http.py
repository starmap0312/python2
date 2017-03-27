# 1) synchronous task
# 2) async tasks
# asyncio:
#   it provides infrastructure for writing single-threaded concurrent code
#   it uses coroutines, multiplexing I/O access over sockets and other resources, running network clients and servers,
#     and other related primitives
#   it provides a framework that revolves around the event loop
# coroutine:
#   a special function that can give up control to its caller without losing its state (i.e. yield)
#     ex. it can be a consumer and an extension of a generator
#   when you call a coroutine function, it doesn’t actually execute
#     instead it returns a coroutine object that you can pass to the event loop to have it executed later/immediately
# event loop:
#   it waits for some task to happen and then acts on the event
#   it is s responsible for handling such things as I/O and system events
#   it basically says when event A happens, react with function B
# future:
#   an object that represents the result of work that has not yet completed
#   event loop can watch for future objects and wait for them to finish
#   when a future finishes, it is set to done
# Task:
#   a wrapper for a coroutine that is also a subclass of Future
#   they give you the ability to keep track of when they finish processing
#     as they are a type of Future, other coroutines can wait for a task, and
#     you can also grab the result of a task when it’s done processing
#   you can schedule a Task using the event loop
# coroutines  vs. threads
#   they benefits over threads is that they don’t use very much memory to execute
# native coroutine
#   defined by async and await
#   ex. async def my_coroutine():
#           await func()
import requests
import aiohttp, asyncio

if __name__ == '__main__':
    urls = ['http://www.google.com', 'http://www.yahoo.com']
    # example1: make single request
    # 1.1) use requests (sync call):
    def sync_http(url):
        return requests.get(url).content
    content = sync_http(urls[0])
    print(content)                                     # b'<!doctype html> ...
    # 1.2) use aiohttp and asyncio (async call)
    #    make your function asynchronous by using async and await keywords
    #    there are actually two asynchronous operations in the following code
    #    a) it fetches response asynchronously, then
    #    b) it reads response body in asynchronous manner
    async def async_http(url):
        async with aiohttp.ClientSession() as session: # use ClientSession as primary interface to make requests
            async with session.get(url) as response:   # a) get  response asynchronously
                # because response.read() is async operation, it does not return result immediately
                #   instead, it returns a generator
                # the generator needs to be called and executed, so we need to add await keyword here
                #   i.e. to actually iterate over generator function (yield from in Python 3.4)
                return await response.read()           # b) read response asynchronously
    # ClientSession():
    #   it allows you to store cookies between requests and keeps objects that are common for all requests
    #     ex. event loop, connection, etc.
    #   after open client session, you can use it to make requests
    #     this is where another asynchronous operation starts: making session.get() request
    #   session needs to be closed after using it (another asynchronous operation)
    #     this is why you need async with ClientSession() as session: every time you deal with sessions

    # to start the task, you need to run it in event loop
    loop = asyncio.get_event_loop()                   # create instance of asyncio loop
    task = asyncio.ensure_future(async_http(urls[0])) # wrap a coroutine in a Task (a subclass of Future)
    loop.run_until_complete(task)                     # put task into the loop
    print(task.result())                              # b'<!doctype html> ...

    # example2: make multiple requests
    # 2.1) use requests (sync call):
    results = []
    for url in urls:
        results.append(requests.get(url).content)
    print(results)

    # 2.2) use aiohttp and asyncio (async call)
    tasks = []
    for url in urls:
        task = asyncio.ensure_future(async_http(url))
        tasks.append(task)
    loop = asyncio.get_event_loop()              # create instance of asyncio loop
    loop.run_until_complete(asyncio.wait(tasks)) # put future into the loop
    for task in tasks:
        print(task.result())

    # example3: collect multiple responses (keep it in list, not just print it out)
    async def fetch(url, session):
        async with session.get(url) as response: # a) get  response asynchronously
            return await response.read()         # b) read response asynchronously

    # get all responses within one Client session,
    # keep connection alive for all requests.
    async def run():
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in urls:
                # ensure_future():
                #   schedule the execution of a coroutine object
                #   wrap it in a future and return a Task object
                task = asyncio.ensure_future(fetch(url, session))
                tasks.append(task)
            # asyncio.gather():
            #   this collects bunch of Future objects in one list (place) and waits for all of them to finish
            return await asyncio.gather(*tasks) # responses: all response bodies
            # note:
            #   this returns a future aggregating results from the given co-routine objects or futures
            #   all futures must share the same event loop
            #   if all the tasks are done successfully, the returned future’s result is the list of results
            #     in the order of the original sequence, not necessarily the order of results arrival
            #   if return_exceptions is true, exceptions in the tasks are treated the same as successful results, and
            #     gathered in the result list
            #     otherwise, the first raised exception will be immediately propagated to the returned future
            # we need await keyword here
            #   always remember about using await keyword if you are awaiting something
    loop = asyncio.get_event_loop()
    gathered_task = asyncio.ensure_future(run())
    loop.run_until_complete(gathered_task)
    for result in gathered_task.result():
        print(result)
