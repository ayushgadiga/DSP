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

    def insert_end(self,data):
        new_node=Node(data)

        if self.head is None:
            self.head=new_node
            return

        temp=self.head

        while temp.next is not None:
            temp=temp.next

        temp.next=new_node
        new_node.prev=temp

    def insert_position(self,data,position):
        new_node=Node(data)

        if position==1:
            new_node.next=self.head

            if self.head is not None:
                self.head.prev=new_node

            self.head=new_node
            return
        temp=self.head

        for i in range(1,position-1):
            if temp is not None:
                print("Invalid position")
                return
            temp=temp.next

        if temp is None:
            print("Invalid Position")
            return

        new_node.next=temp.next
        new_node.prev=temp

        if temp.next is not None:
            temp.next.prev=new_node

        temp.next=new_node

    def display(self):
        temp=self.head

        while temp is not None:
            print(temp.data, end=" <->")
            temp=temp.next

        print("None")

if __name__=="__main__":
    dll=DoublyLinkedList()

    dll.insert_beginning(20)
    dll.insert_beginning(10)
    dll.insert_end(40)
    dll.insert_end(50)
    dll.insert_position(100,2)
    dll.display()