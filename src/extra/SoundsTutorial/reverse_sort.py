#Reverse sort, by Bill Dengler <codeofdusk@gmail.com> for use in TWBlue http://twblue.es
def invert_tuples(t):
    "Invert a list of tuples, so that the 0th element becomes the -1th, and the -1th becomes the 0th."
    res=[]
    for i in t:
        res.append(i[::-1])
    return res

def reverse_sort(t):
    "Sorts a list of tuples/lists by their last elements, not their first."
    return invert_tuples(sorted(invert_tuples(t)))