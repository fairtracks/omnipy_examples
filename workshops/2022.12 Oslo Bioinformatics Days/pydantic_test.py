from typing import Dict, List

from omnipy.data.dataset import Dataset, MultiModelDataset
from omnipy.data.model import Model
from omnipy.modules.pandas.models import PandasDataset
from pydantic import BaseModel, validator


class LimitedInteger(BaseModel):
    ...


class MyForm(BaseModel):
    __root__: List[int]


record = MyForm(__root__=[123, 234, 23])

print(record)

print(type(record))


class ListOfIntegers(Model[List[int]]):
    ...


# a = ListOfIntegers([123,234,'asd'])
# print(a)

a = Dataset[Model[Dict[str, List[int]]]]()
a['my_data'] = {'a': [3, 4, 123], 'b': [213, 2, 234]}
a['my_data_2'] = {'a': [123, 234, 123], 'b': [213, 234, 234]}

print(a.to_data())

b = PandasDataset()
b.from_data(a.to_data())

print(type(b['my_data']))

MultiModelDataset
