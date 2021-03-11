def memoize(f):
    memory = {}
    def memorized(*args, **kwargs):
        args_hash = hash((args, *kwargs))
        if args_hash not in memory:
            memory[args_hash] = f(*args, **kwargs)
            return memory[args_hash]
        return memory[args_hash]

    return memorized