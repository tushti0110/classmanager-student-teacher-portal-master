#define Jaccard Similarity function
def jaccard(list1, list2): # return 0-2, 1 when strings are same
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return intersection/union
    