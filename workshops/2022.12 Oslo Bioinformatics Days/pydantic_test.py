from typing import Dict, List, Type, Union

from pydantic import BaseModel, validator
from unifair.data.dataset import Dataset, MultiModelDataset
from unifair.data.model import Model
from unifair.modules.pandas.models import PandasDataset


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
a['my_data'] = {'a': [3,4,123], 'b':[213,2,234]}
a['my_data_2'] = {'a': [123,234,123], 'b':[213,234,234]}

print(a.to_data())

b = PandasDataset()
b.from_data(a.to_data())

print(type(b['my_data']))

MultiModelDataset
