from urlparse import urlparse

def query2dict(query):
    assgns = query.split('&')
    result = {}
    for assgn in assgns:
        if assgn:
            v = assgn.split('=')
            result[v[0]] = v[1]
    return result

def dict2query(qdict):
    result = ''
    for key in qdict:
        result += key + '=' + qdict[key]
    return result

class Node:
    def __init__(self, name, isFile = False, query = '', fragment = ''):
        self.name = name
        self.isFile = isFile
        self.query = query
        self.fragment = fragment
        self.children = {}
        self.father = None

    def addQuery(self, newQuery):
        q1 = query2dict(self.query)
        q2 = query2dict(newQuery)
        for key in q2.keys():
            if key not in q1.keys():
                q1[key] = q2[key]
        self.query = dict2query(q1)

    def getFullPath(self):
        cur = self
        slicePaths = []
        while cur.name:
            slicePaths.append(cur.name)
            cur = cur.father
        slicePaths.reverse()

        path = '/'.join(slicePaths)

        return path

    def getFullPathWithAll(self):
        frag = ''
        q = ''
        if self.fragment:
            frag = '#' + self.fragment
        if self.query:
            q = '?' + self.query

        return self.getFullPath() + q + frag



class UrlManager:
    def __init__(self):
        self.tree = Node('')

    def addUrl(self, url):
        rs = urlparse(url)
        site = rs.scheme + "://" + rs.netloc
        path = rs.path

        slicePaths = filter(lambda x:x, path.split("/"))
        slicePaths.reverse() # reverse for fast pop later

        slicePaths.append(site)

        currentNode = self.tree

        while slicePaths:
            curSlicePath = slicePaths.pop()
            if curSlicePath not in currentNode.children.keys():
                currentNode.children[curSlicePath] = Node(curSlicePath)
                currentNode.children[curSlicePath].father = currentNode
            currentNode = currentNode.children[curSlicePath]

        currentNode.isFile = True
        if not currentNode.fragment:
            currentNode.fragment = rs.fragment
        if not currentNode.query:
            currentNode.query = rs.query
        else:
            currentNode.addQuery(rs.query)

    def __printLayerImpl(self, node = None, prefix = '>'):
        if not node:
            node = self.tree
        print prefix, node.name
        for child in node.children:
            self.__printLayerImpl(node.children[child], ' ' * 4 + prefix)


    def __mapTreeImpl(self, func, node = None, rdict = {}):
        """

        map func in every node of tree,

        rdict store the result

        Return:
            rdict = {
                node1.name : result1,
                node2.name : result2
            }
        """
        if not node:
            node = self.tree
        else:
            rdict[node.getFullPath()] = func(node)

        for child in node.children:
            self.__mapTreeImpl(func, node.children[child], rdict)

        if node is self.tree:
            return rdict

    def mapTree(self, func):
        return self.__mapTreeImpl(func)

    def printLayer(self):
       self. __printLayerImpl()

def testUrlManager():
    urls = [
        "http://a.com",
        "http://a.com?a=c",
        "http://a.com?r=h",
        "http://a.com/b",
    ]

    manager = UrlManager()
    for url in urls:
        manager.addUrl(url)

    manager.printLayer()

def test2UrlManager():
    lines = None
    with open("taobao.store.bak") as f:
        lines = f.readlines()
    lines = map(lambda x: x.strip('\n'), lines)

    manager = UrlManager()

    for url in lines:
        manager.addUrl(url)
    manager.printLayer()

    print "-" * 80

    cur = manager.tree
    while True:
        keys = cur.children.keys()
        if len(keys) == 0:
            break
        else:
            cur = cur.children[keys[-1]]
    print cur.getFullPath()

    cur = manager.tree
    while True:
        keys = cur.children.keys()
        if len(keys) == 0:
            break
        else:
            cur = cur.children[keys[0]]
    print cur.getFullPathWithAll()

    def func(node):
        return node.getFullPathWithAll()

    rdict = manager.mapTree(func)
    print rdict


if __name__ == '__main__':
    test2UrlManager()

