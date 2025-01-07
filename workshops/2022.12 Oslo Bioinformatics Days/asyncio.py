import asyncio

import omnipy.components.json.util
import omnipy.components.pandas.util
import omnipy.components.raw.util

omnipy.components.json.util.ROOT_DIR = '../../input/bif'
omnipy.components.pandas.util.ROOT_DIR = '../../input/bif'
omnipy.components.raw.util.ROOT_DIR = '../../input/bif'


# @TaskTemplate()
async def fetch_from_api(what: str):
    asyncio.sleep(10)
    return what


# @FuncFlowTemplate()
async def caller():
    data = fetch_from_api('asdsda')
    data2 = fetch_from_api('asdd')
    data3 = fetch_from_api('ddd')
    all_data = await asyncio.gather([data, data2, data3])


caller.run()
