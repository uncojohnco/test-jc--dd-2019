
import logging

from typing import List, Optional, Set, Union

import lss.util

from lss import SubstrMatch
from lss.dataclass.item import Item
from lss.dataclass.sequence import SequenceStrParts
from lss.error import SequenceError


log = logging.getLogger(__name__)


LazyItem = Union[str, Item]


def find_matching_frame_substrings(
        item1: LazyItem, item2: LazyItem,
        strict=True) -> Optional[SubstrMatch]:
    """
    Diff between item1 and item2 to to resolve the frame representation
    of each item.

    Example:
        >>> find_matching_frame_substrings('file01_0040.rgb', 'file01_0041.rgb')
        SubstrMatch(pos=SubstrPos(start=7, end=11), groups=('0040', '0041'))

        >>> find_matching_frame_substrings('file1.03.rgb', 'file2.03.rgb')
        SubstrMatch(pos=SubstrPos(start=4, end=5), groups=('1', '2'))

        >>> find_matching_frame_substrings('file02_0040.rgb', 'file01_0041.rgb')

    :param item1: The string object for comparison against.
    :param item2: The string to compare to the object string.
    :param strict: If True, the length of the digit padding
                    must be the same when comparing

    :return: List of SeqMatch
    """

    if not isinstance(item1, Item):
        item1 = Item(item1)

    if not isinstance(item2, Item):
        item2 = Item(item2)

    if item1.str_parts != item2.str_parts:
        return None

    if len(item1.str_digits) != len(item2.str_digits):
        return None

    name1, name2 = item1.name, item2.name

    substr_match = lss.util.find_matching_frame_substrings(name1, name2, strict)
    return substr_match


class SequenceBuilder:
    """
    Class to handle the collection of sequential sequence of items.

    >>> s = SequenceBuilder(Item('file.0001.jpg'))
    >>> s.append(Item('file.0002.jpg'))
    >>> s.append(Item('file.0003.jpg'))
    >>> print(s.frames)
    {1, 2, 3}
    """
    _is_sequence: bool

    _base: Item
    _items: List[Item]

    def __init__(self, item: Item):

        self._base = item
        self._items = [item]

        self._is_sequence = False

        self._frames = set()

    def can_include(self, item: Item) -> bool:
        """
        Validate if the supplied item can be a part of this sequence.

        :param item: The item to compare against the base item

        :return: bool
        """

        substr_match = find_matching_frame_substrings(self._base, item)
        if not substr_match:
            return False

        frame = substr_match.groups[1]

        # Dont include if the matched frame of the other item
        # already exists in this sequence frame set.
        if frame in self._frames:
            return False

        return True

    def _init_sequence(self, substr_match: SubstrMatch):
        """
        Method to initialise this as a true sequence.
        """

        basename = self._base.name
        base_frame = substr_match.groups[0]

        frame_pos = substr_match.pos

        pos1, pos2 = frame_pos.start, frame_pos.end

        # This is used later for creating a Concrete Sequence
        seq_str_parts = SequenceStrParts(
            prefix=basename[:pos1],
            suffix=basename[pos2:],
            pad_len=len(base_frame)
        )

        self._frames.add(int(base_frame))

        self._seq_str_parts = seq_str_parts
        self._is_sequence = True

    def append(self, item: Item):

        substr_match = find_matching_frame_substrings(self._base, item)
        log.debug(f'{item} - {substr_match}')

        if not substr_match:
            raise SequenceError('\n'.join(
                'Item dosent belong to this sequence!'
                'Sequence.base: {self._base}'
                'Item: {item}'
            ))

        # The first append will toggle the state that this is a Sequence,
        # i.e it has more than one item
        if not self._is_sequence:
            self._init_sequence(substr_match)

        self._frames.add(int(substr_match.groups[1]))
        self._items.append(item)

    def __str__(self):
        return self._base.str_parts

    @property
    def items(self) -> List[Item]:
        """
        The items used in the creation of this sequence.
        :return: List[Item]
        """
        return self._items

    @property
    def frames(self) -> Set[int]:
        """
        The frames contained in this sequence
        :return: List[int]
        """
        return self._frames

    @property
    def seq_str_parts(self) -> SequenceStrParts:
        """

        :return:
        """

        return self._seq_str_parts
