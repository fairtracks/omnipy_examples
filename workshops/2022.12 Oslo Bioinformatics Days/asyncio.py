import asyncio
from asyncio import gather
import unifair.modules.json.util
import unifair.modules.pandas.util
import unifair.modules.raw.util
unifair.modules.json.util.ROOT_DIR = '../../input/bif'
unifair.modules.pandas.util.ROOT_DIR = '../../input/bif'
unifair.modules.raw.util.ROOT_DIR = '../../input/bif'


# @TaskTemplate

async def fetch_from_api(what: str):
    asyncio.sleep(10)
    return what


# @FuncFlowTemplate
async def caller():
    data = fetch_from_api('asdsda')
    data2 = fetch_from_api('asdd')
    data3 = fetch_from_api('ddd')
    all_data = await gather([data, data2, data3])


caller.run()
