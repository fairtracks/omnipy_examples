#!/usr/bin/env python
# coding: utf-8

import asyncio
import json

import aiohttp
import anyio
import numpy as np
from omnipy import (FuncFlowTemplate,
                    HttpUrlDataset,
                    HttpUrlModel,
                    JsonDataset,
                    JsonModel,
                    StrDataset,
                    StrModel,
                    TaskTemplate)
from omnipy.compute.typing import mypy_fix_task_template
import pandas as pd
import requests

# making the centre name smoother
UiO_list = [
    'University of Oslo',
    'UNIVERSITY OF OSLO',
    'University of Oslo, Department of Biosciences',
    'University of oslo',
    'Universitetet i Oslo',
    'Department of Paediatric Medicine, Oslo University Hospital',
    'Oslo University',
    'Unversity of Oslo',
    'Oslo University Hospital',
    'Insititute of Oral Biology, Univeristy of Oslo',
    'Oslo University Hospital, Rikshopitalet',
    'Archaeogenomics group, Department of Biosciences, University of Oslo',
    'Oslo University Hospital/University of Oslo',
    'OSLO UNIVERSITY HOSPITAL',
    'Department of Biosciences, University of Oslo',
    'Natural History Museum, University of Oslo',
    'UIO',
    'CEES'
]

NTNU_list = [
    'NTNU', 'NTNU - Norwegian University of Science and Technology', 'NTNU University Museum'
]

UiB_list = [
    'University of Bergen',
    'CENTRE FOR GEOBIOLOGY, DEPARTMENT OF BIOLOGY, UNIVERSITY OF BERGEN, NORWAY',
    'Universitetet i Bergen',
    'UNIVERSITY OF BERGEN/DEPT. OF BIOLOGY',
    'K.G. Jebsen center for deep-sea research, University of Bergen',
    'Center for Geobiology, University of Bergen',
    'UNIVERSITY OF BERGEN',
    'UiB'
]

NMBU_list = [
    'FACULTY OF CHEMISTRY, BIOTECHNOLOGY AND FOOD SCIENCE (IKBM), NORWEGIAN UNIVERSITY OF LIFE SCIENCES (NMBU), NORWAY',
    'NMBU Norwegian University of Life Sciences',
    'NMBU',
    'Norwegian University of Life Sciences (NMBU)',
]

UiT_list = [
    'University of Tromso',
    'UiT the Arctic University of Norway',
    'UiT: The Arctic University of Norway',
    'UiT, The Arctic University of Norway',
    'UIT',
    'UiT The Arctic University if Norway',
    'UiT The Arctic University',
    'UiT - The Arctic University of Norway',
    'The Arctic University of Norway',
    'University of Tromsoe',
    'Sletvold H., Department of Pharmacy, University of Tromso, Tromso, N-9037, NORWAY',
    'Tromsoe University Museum',
    'University of Tromso - The Arctic University of Norway',
    'UNIVERSITY OF TROMSO'
]

FHI_list = [
    'Norwegian Institute of Public Health (NIPH)',
    'NIPH',
    'NORWEGIAN INSTITUTE OF PUBLIC HEALTH',
    'Folkehelseinstituttet (FHI), Norway'
]

centres = {
    'UiO': UiO_list,
    'UiB': UiB_list,
    'UiT': UiT_list,
    'NMBU': NMBU_list,
    'NTNU': NTNU_list,
    'FHI': FHI_list
}


def get_api_url(n_size, j_page, fields):
    base = 'https://www.ebi.ac.uk/ebisearch/ws/rest/sra-sample?query=country:Norway'
    api_url = base + '&size=' + str(n_size) + '&start=' + str(
        n_size * j_page) + '&fields=' + ','.join(fields) + '&format=json'
    return api_url


def get_api_url(fields: list[str], page_num: int = 0, page_size: int = 1000) -> HttpUrlModel:
    url = HttpUrlModel('https://www.ebi.ac.uk/ebisearch/ws/rest/')
    url.path // 'sra-sample'
    url.query['query'] = 'country:Norway'
    url.query['fields'] = ','.join(fields)
    url.query['start'] = page_num * page_size
    url.query['size'] = page_size
    url.query['format'] = 'json'
    return url


#
# @dataclass
# class Components:
#     scheme: str = 'https'
#     netloc: str
#     path: str
#     params: dict[str, str] = {}
#     query: str = ''
#     fragment: str = ''
#
#     field_names=['scheme', 'netloc', 'url', 'path', 'query', 'fragment']
# )
#
# def build_url(
#         host: str,
#         path: str = '',
#         params=dict[str, str](),
#         scheme: str = 'https',
# ) -> str:
#     url = urlunparse(
#         Components(
#             scheme='https',
#             netloc='example.com',
#             query=urlencode(query_params),
#             path='',
#             url='/',
#             fragment='anchor'))


async def get_json_from_api_endpoint(url: str) -> JsonModel:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return JsonModel(await response.json())


#
# def get_json_from_api_endpoint(api_url):
#     response = requests.get(api_url)
#     results = json.loads(response.content.decode())
#     return (results)
#

# @mypy_fix_task_template
# @TaskTemplate()
# async def get_dataset_size():
#     data = JsonDataset()
#     await data.load(size=get_api_url(['center_name', 'last_updated_date']))
#     return data['size']['hitCount']


@mypy_fix_task_template
@TaskTemplate()
async def get_all_data() -> JsonDataset:
    data = JsonDataset()
    fields = ['center_name', 'last_updated_date']
    await data.load(page_0=get_api_url(fields, 0))
    hit_count = data['page_0']['hitCount']

    urls = HttpUrlDataset()
    for i in range(hit_count // 1000 + 1):
        urls[f'page_{i}'] = get_api_url(fields, i)

    await data.load(urls)
    return data


print(get_all_data.run())

#
# @mypy_fix_task_template
# @TaskTemplate(iterate_over_data_files=True)
# async def get_all_entries(url: StrModel) -> JsonModel:
#     return JsonModel(get_json_from_api_endpoint(url))

#
# @mypy_fix_task_template
# @TaskTemplate(iterate_over_data_files=True)
# async def get_all_entries(url: StrModel) -> JsonModel:
#     return JsonModel(await get_json_from_api_endpoint(url))


@mypy_fix_task_template
@TaskTemplate()
async def get_all_entries(urls: StrDataset) -> JsonDataset:
    output = JsonDataset()
    for i, (key, url) in enumerate(urls.items()):
        await anyio.sleep(i * 0.1)
        output[key] = JsonModel(await get_json_from_api_endpoint(url.contents))
    return output


#
# @mypy_fix_task_template
# @FuncFlowTemplate()
# def get_all_data() -> JsonDataset:
#     dataset_size = get_dataset_size()
#     url_dataset = get_urls_for_all_data(dataset_size)
#     return url_dataset
#     # return await get_all_entries(url_dataset)

# @mypy_fix_task_template
# @FuncFlowTemplate()
# def get_all_data() -> JsonDataset:
#     # dataset_size = get_dataset_size()
#     dataset_size = 10000
#     urls = get_urls_for_all_data(dataset_size)
#     return get_all_entries(urls)


def get_entries(n_size, n_page, fields):
    entries = []
    for j_page in range(n_page + 1):
        api_url = get_api_url(n_size, j_page, fields)
        data = get_dataset(api_url)
        entries.extend(data['entries'])
    if len(entries) != get_dataset_size():
        print('WARNING: wrong number of entries: ',
              len(entries),
              ' vs ',
              get_dataset_size(),
              ' hits')
    return (entries)


def _get_all_data() -> str:
    # get all the data
    points_perpage = 1000  # max allowed by API
    n_pages = get_dataset_size() // points_perpage  # pages to get the whole database
    fields = ['center_name', 'last_updated_date']  # fields for plotting
    return get_entries(points_perpage, n_pages, fields)


def polish_data_for_plotting(entries: str) -> pd.DataFrame:
    # polish the data for plotting
    df = pd.DataFrame(entries)
    fields = pd.json_normalize(df['fields'])  # extract the variables for plotting
    for column in fields.columns:  # change from list to standard variable
        fields[column] = fields[column].apply(lambda x: x[0] if len(x) > 0 else None)

    # change to proper date/time type
    fields['last_updated_date'] = fields['last_updated_date'].astype('datetime64[ns]')

    for centre in centres.keys():
        fields.loc[fields['center_name'].isin(centres[centre]), 'center_name'] = centre

    # Grouping the data to plot into a unique dataframe, setting to 0. entries lacking data
    data2plot = {}
    for centre in centres.keys():
        data2plot[centre] = \
        fields[fields['center_name'] == centre].groupby(fields['last_updated_date'].dt.year).count()[
            'center_name']
    data2plot = pd.DataFrame(data2plot)

    for centre in data2plot.columns:
        data2plot[centre] = [0 if np.isnan(value) else value for value in data2plot[centre]]
        data2plot[centre] = data2plot[centre].astype(int)
    data2plot.index = data2plot.index.astype(int)

    return data2plot


def generate_plots(data2plot: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt

    # stacked-bars plot universities
    fig, ax = plt.subplots()

    bottom = 0.
    for centre in data2plot.columns:
        if centre != 'FHI':
            ax.bar(data2plot.index, data2plot[centre], bottom=bottom, label=centre)
            bottom = np.add(bottom, data2plot[centre])

    plt.xlabel('YEAR')  # Set the label for the x-axis
    plt.ylabel('# samples submitted')  # Set the label for the y-axis
    plt.xticks(rotation=90)
    plt.xlim(2015.5, 2023.5)

    ax.legend()
    plt.savefig('stacked_bar_plot.png', bbox_inches='tight')

    fig, ax = plt.subplots()

    # bar plot for FHI
    centre = 'FHI'
    ax.bar(data2plot.index, data2plot[centre], label=centre)
    bottom = np.add(bottom, data2plot[centre])

    plt.xlabel('YEAR')  # Set the label for the x-axis
    plt.ylabel('# samples submitted')  # Set the label for the y-axis
    plt.xticks(rotation=90)
    plt.xlim(2015.5, 2023.5)

    ax.legend()
    plt.savefig('bar_plot_FHI.png', bbox_inches='tight')
