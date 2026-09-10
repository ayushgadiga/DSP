class Node:
    def __init__(self,data):
        self.data=data
        self.next=None

class circularll:
    def __init__(self):
        self.head=None
        
    def insert_at_beginning(self,data):
            new_node=Node(data)
            if self.head is None:
                self.head=new_node
            else:
                new_node.next=self.head
                self.head=new_node

    def insert_at_end(self,data):
        new_node=Node(data)
        if self.head is None:
            self.head=new_node
            return
        temp=self.head
        while temp.next:
            temp=temp.next
        temp.next=new_node
        new_node.next=self.head

    def display(self):
        temp=self.head
        elements=[]
        while temp:
            elements.append(str(temp.data))
            temp=temp.next
        print(" -> ".join(elements)if elements else "list is empty")

if __name__=="__main__":
    ll=circularll()

    ll.insert_at_beginning(10)
    ll.insert_at_beginning(20)
    ll.insert_at_beginning(5)
    ll.insert_at_end(50)
    ll.display()
        