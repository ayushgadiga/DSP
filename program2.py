class Node:
    def __init__(self,data):
        self.data=data
        self.next=None
class LinkedList:
    def __init__(self):
        self.head=None

    def insert_at_end(self,data):
            new_node=Node(data)
            if self.head is None:
                self.head=new_node
                return
            temp=self.head
            while temp.next:
                temp=temp.next
            temp.next=new_node

    def deletion_at_beginning(self):
        current=self.head
        if self.head is None:
            print("No data element to delete")
        elif current==self.head:
            self.head=current.next

    def deletion_at_position(self,position):
        if position<0:
            print("Invalid position")
            return

        

    def deletion_at_end(self):
        current=self.head
        while current.next.next is not None:
            current=current.next
        current.next=None

    def display(self):
        temp=self.head
        elements=[]
        while temp:
            elements.append(str(temp.data))
            temp=temp.next
        print(" -> ".join(elements)if elements else "list is empty")

if __name__=="__main__":
    ll=LinkedList()

    ll.insert_at_end(10)
    ll.insert_at_end(20)
    ll.insert_at_end(30)
    ll.insert_at_end(40)
    ll.display()

    ll.deletion_at_beginning()
    ll.display()

    ll.deletion_at_end()
    ll.display()