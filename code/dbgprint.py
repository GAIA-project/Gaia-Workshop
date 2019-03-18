import pprint


class MyPrettyPrinter(pprint.PrettyPrinter):
    def format(self, object, context, maxlevels, level):
        if isinstance(object, unicode):
            return (object.encode('utf8'), True, False)
        return pprint.PrettyPrinter.format(self, object, context, maxlevels, level)


def dbgprint(obj):
    print("---------------------------------------")
    MyPrettyPrinter().pprint(obj)
    print("---------------------------------------")

