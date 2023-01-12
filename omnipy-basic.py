from typing import List

from omnipy.compute.task import TaskTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.model import Model
from pydantic import PositiveInt


class ListOfNumbers(Model[List[int]]):
    ...


class ListOfPositiveNumbers(Model[List[PositiveInt]]):
    ...


my_numbers = ListOfNumbers([1243, -123, 3425])


@TaskTemplate(iterate_over_data_files=True)
def make_absolute(numbers: ListOfNumbers) -> ListOfPositiveNumbers:
    return [abs(num) for num in numbers]


dataset = Dataset[ListOfNumbers]()
dataset['my_numbers'] = ListOfNumbers([1243, -123, 3425])

my_pos_numbers = make_absolute.run(dataset)
