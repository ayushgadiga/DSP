class Node:
    def __init__(self,key):
        self.key=key
        self.left=None 
        self.right=None 

def insert (root, key):
    if root is None:
        return Node(key)

    if key<root.key:
        root.left=insert(root.left, key)

    elif key>root.key:
        root.right=insert(root.right, key)

    return root 

def inorder(root):
    if root:
        inorder(root.left)
        print(root.key, end=" ")
        inorder(root.right)

root=None 

def preorder(root):
    if root:
        print(root.key, end=" ")
        preorder(root.left)
        preorder(root.right)

root=None

def postfix(root):
    if root:
        postfix(root.left)
        postfix(root.right)
        print(root.key, end=" ")

values=[50,30,70,20,40,60,80]

for value in values:
    root=insert(root, value)

print("Inorder Traversal:")
inorder(root)

print("\nPreorder Traversal:")
preorder(root)

print("\nPostfix Traversal:")
postfix(root)
