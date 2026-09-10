stack=[]

def push():
    element=input("Enter element to push:")
    stack.append(element)
    print(element,"pushed into stack")

def pop():
    if len(stack)==0:
        print("Stack Underflow")
    else:
        element=stack.pop()
        print(element,"popped from stack")

def peek():
    if len(stack)==0:
        print("Stack is empty")
    else:
        print("Top element of the stack is:", stack[-1])

def display():
    if len(stack)==0:
        print("Stack is empty")
    else:
        print("Elements of stack:",stack)

while True:
    print("\n----Stack operation----")
    print("\n1)Push")
    print("\n2)Pop")
    print("\n3)Peek")
    print("\n4)Display")
    print("\n5)Exit")

    choice=int(input("Enter the function:"))

    if choice==1:
        push()
    elif choice==2:
        pop()
    elif choice==3:
        peek()
    elif choice==4:
        display()
    elif choice==5:
        print("Exiting the program")
        break
    else:
        print("Invalid choice")