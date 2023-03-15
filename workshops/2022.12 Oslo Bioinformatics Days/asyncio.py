import asyncio

import omnipy.modules.json.util
import omnipy.modules.pandas.util
import omnipy.modules.raw.util

omnipy.modules.json.util.ROOT_DIR = '../../input/bif'
omnipy.modules.pandas.util.ROOT_DIR = '../../input/bif'
omnipy.modules.raw.util.ROOT_DIR = '../../input/bif'


# @TaskTemplate
async def fetch_from_api(what: str):
    asyncio.sleep(10)
    return what


# @FuncFlowTemplate
async def caller():
    data = fetch_from_api('asdsda')
    data2 = fetch_from_api('asdd')
    data3 = fetch_from_api('ddd')
    all_data = await asyncio.gather([data, data2, data3])


caller.run()
