from dataclasses import dataclass
from typing import List


@dataclass
class Link:
    label: str
    url: str


@dataclass
class Subsection:
    text: str
    links: List[Link]


@dataclass
class Section:
    title: str
    subsections: List[Subsection]
