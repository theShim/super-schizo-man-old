import random

class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

class ProbabilisticMaxBSTLinkedList:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if not self.root:
            self.root = Node(value)
        else:
            self._insert_recursive(self.root, value)

    def _insert_recursive(self, node, value):
        if value < node.value:
            if node.next is None:
                node.next = Node(value)
            else:
                self._insert_recursive(node.next, value)
        else:
            if node.next is None:
                node.next = Node(value)
            else:
                self._insert_recursive(node.next, value)

    def find_max(self):
        if not self.root:
            return None
        else:
            max_val, _ = self._find_max_recursive(self.root)
            return max_val

    def _find_max_recursive(self, node):
        max_val = node.value
        current = node.next

        while current:
            if current.value > max_val:
                max_val = current.value
            current = current.next

        return max_val, None

my_probabilistic_max_bst_linked_list = ProbabilisticMaxBSTLinkedList()
my_list = [3, 7, 1, 9, 4, 6, 5]

for num in my_list:
    my_probabilistic_max_bst_linked_list.insert(num)

print(my_probabilistic_max_bst_linked_list.find_max())
