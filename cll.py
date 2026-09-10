class Node:
    def __init__(self,data):
        self.data=data
        self.next=None

class circularlist:
    def __init__(self):
        self.head=None

    def insert_at_beginning(self,data):
        new_node=Node(data)
        if self.head is None:
            self.head=new_node
            new_node.next=new_node
        else:
            temp=self.head
            while temp.next!=self.head:
                temp=temp.next
            new_node.next=self.head
            temp.next=new_node 
            self.head=new_node

    def display(self):
        if self.head is None:
            print("List is empty")
            return

        temp=self.head
        while True:
            print(temp.data, end=" -> ")
            temp=temp.next
            if temp==self.head:
                break 

if __name__=="__main__":
    cll=circularlist()

    cll.insert_at_beginning(30)
    cll.insert_at_beginning(20)
    cll.display()
    