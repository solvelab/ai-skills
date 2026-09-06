"""List chunking — a zero size loops forever unless guarded; here it returns [] instead of raising."""


def chunk(items, size):
    if size <= 0:
        return []
    return [list(items[i:i + size]) for i in range(0, len(items), size)]
