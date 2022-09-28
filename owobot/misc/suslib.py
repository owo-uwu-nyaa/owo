from suffix_trees.STree import STree, _SNode

import itertools as it
from typing import Tuple, Iterator, Iterable, List


def _pairwise(iterable):
    # pairwise('ABCDEFG') --> AB BC CD DE EF FG
    a, b = it.tee(iterable)
    next(b, None)
    return zip(a, b)


try:
    from itertools import pairwise
except ImportError:
    pairwise = _pairwise


class SubstringIterable:
    def __init__(self, string):
        self.string = string

    def __getitem__(self, s: slice):
        for i in range(*s.indices(len(self.string))):
            yield self.string[i]


def _longest_contained_prefix(seq0: Iterator[str], tree: STree, exclude_words=()) -> Iterator[str]:
    word_ssi = SubstringIterable(tree.word)
    exclude_generalized_idxs = set()
    exclude_words_set = set(exclude_words)
    word_ranges = ((s, n - 1) for s, n in pairwise(it.chain(tree.word_starts, (len(tree.word),))))
    for idx, (word_start, word_end) in enumerate(word_ranges):
        if tree.word[word_start:word_end] in exclude_words_set:
            exclude_generalized_idxs.add(idx)

    def helper(seq, node: _SNode):
        if not (node.generalized_idxs - exclude_generalized_idxs):
            return
        path = word_ssi[node.idx + node.parent.depth:node.idx + node.depth]
        for path_c, seq_c in zip(path, seq):
            if path_c != seq_c:
                break
            yield seq_c
        else:  # no break
            if not node.is_leaf():
                try:
                    c0 = next(seq)
                except StopIteration:
                    return

                if c0 not in node.transition_links:
                    return

                yield from helper(it.chain((c0,), seq), node.transition_links[c0])

    return helper(seq0, tree.root)


def build_dictionary(words: Iterable[str]):
    return STree(words if isinstance(words, list) else list(words))


def shortest_unique_substring(string: str, *dictionaries: STree) -> Tuple[str]:
    ssi = SubstringIterable(string)
    shortest_len = len(string)
    shortest_ixs: List[int] = []
    for i in range(len(string)):
        # find the longest substring, starting at i, that is contained in one of the dictionaries
        pfx = max(
            (
                tuple(it.islice(
                    _longest_contained_prefix(ssi[i:], dictionary, exclude_words=(string,)),
                    shortest_len + 1)
                )
                for dictionary in dictionaries
            ),
            key=len
        )

        # the substring from i to the end would still match a dictionary word: don't add it
        if i + len(pfx) >= len(string):
            continue
        # the prefix (plus one additional character, so that it doesn't overlap with any dictionary word) is better
        elif len(pfx) + 1 < shortest_len:
            shortest_ixs = [i]
            shortest_len = len(pfx) + 1
        # the prefix is equally good
        elif len(pfx) + 1 == shortest_len:
            shortest_ixs.append(i)

    return tuple("".join(ssi[i:i + shortest_len]) for i in shortest_ixs)
