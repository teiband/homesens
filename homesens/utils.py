import inspect


def DEBUG(msg):
    if True:
        print(str(inspect.stack()[1][3]) + ": " + str(msg))
