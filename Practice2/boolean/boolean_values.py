print(10 > 9)
print(10 == 9)
print(10 < 9)


#True
print(bool("Hello"))
print(bool(15))

bool("abc")
bool(123)
bool(["apple", "cherry", "banana"])


#False
bool(False)
bool(None)
bool(0)
bool("")
bool(())
bool([])
bool({})

class myclass():
    def __len__(self):
        return 0
myobj = myclass()
print(bool(myobj))


