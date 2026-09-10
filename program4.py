class Node:
    def __init__(self,data):
        self.data=data 
        self.prev=None
        self.next=None

class DoublyLinkedList:
    def __init__(self):
        self.head=None

    def insert_beginning(self,data):
        new_node=Node(data)

        if self.head is not None:
            new_node.next=self.head
            self.head.prev=new_node

        self.head=new_node 

    def delete_beg(self):
        temp=self.head
        if self.head is None:
            print("No Elements")
        elif temp == self.head:
            self.head=temp.next

    def delete_end(self):
        
    def display(self):
        temp=self.head

        while temp is not None:
            print(temp.data, end=" <-> ")
            temp=temp.next

        print("None")

if __name__=="__main__":
    dll=DoublyLinkedList()

    dll.insert_beginning(20)
    dll.insert_beginning(10)
    dll.delete_beg()
    dll.display()
