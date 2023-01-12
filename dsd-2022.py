from typing import List, Union

import omnipy.data
from omnipy import runtime
from omnipy.compute.task import TaskTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from pydantic import BaseModel, PositiveInt, StrictStr

print(runtime.config.job.persist_data_dir_path)
#
# int
# str
# float
# dict
# list
# bool
#
# # print(repr(int('asfdas')))
#
#
# class PairOfStr(BaseModel):
#     x: str
#     y: str
#
#     @staticmethod
#     def add(x: Union[int, str], y: Union[int, str]) -> int:
#         return x + y
#
#
# a = PairOfStr(x='False', y=214265)
#
# print(repr(a.x), repr(a.y))
# # output: str = add('dsd', 'wsddsdsd')
#
#


class ListOfNumbers(Model[List[int]]):
    ...


class ListOfPositiveNumbers(Model[List[PositiveInt]]):
    ...


my_numbers = ListOfNumbers([1243, -123, 3425])
print(my_numbers)

# my_python_numbers: List[int] = [1243, 'sdf', 3425]


@TaskTemplate(iterate_over_data_files=True)
def double_numbers(numbers: ListOfNumbers) -> ListOfPositiveNumbers:
    return [abs(num) for num in numbers.contents]


dataset = Dataset[ListOfNumbers]
dataset['my_numbers'] = ListOfNumbers([1243, -123, 3425])

my_pos_numbers = double_numbers.run(my_numbers)
# print(double_numbers
# print(type(ListOfPositiveNumbers(my_pos_numbers)))

print(omnipy.__version__)
