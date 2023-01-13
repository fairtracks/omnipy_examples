from typing import List

from omnipy.compute.task import TaskTemplate
from omnipy.compute.flow import LinearFlowTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from pydantic import PositiveInt
from omnipy import runtime

runtime.config.engine = 'local'


class ListOfNumbers(Model[List[int]]):
    ...


class ListOfPositiveNumbers(Model[List[PositiveInt]]):
    ...


@TaskTemplate(iterate_over_data_files=True)
def make_absolute(numbers: ListOfNumbers) -> ListOfPositiveNumbers:
    return [abs(num) for num in numbers]


@TaskTemplate(iterate_over_data_files=True)
def double(numbers: ListOfPositiveNumbers) -> ListOfPositiveNumbers:
    return [num * 2 for num in numbers]


@LinearFlowTemplate(make_absolute, double, iterate_over_data_files=True)
def my_flow(numbers: ListOfNumbers) -> ListOfPositiveNumbers:
    ...


dataset = Dataset[ListOfNumbers]()
dataset['my_numbers'] = ListOfNumbers(["1243", -123, 3425] * 100)
dataset['my_numbers_2'] = ListOfNumbers([234, -12443, 444] * 100)

output = my_flow.run(dataset)
