
from hashlib import sha1

class Tree(object):
    '''State tree.'''

    def __init__(self):
        super(Tree, self).__init__()
        self.visited = {}

    def __getitem__(self, key):
        return self.visited[key]

    def get_key(array):
        return sha1(array).hexdigest()

    def search(self, sim, state, model):
        array = state.get_array()
        key = self.get_key(array)

        if key not in self.visited:
            policy, value = model(array)
            quality, number = np.zeros(policy.shape), np.zeros(policy.shape)
            self.visited[key] = {'s':state, 'p':policy, 'q':quality, 'n':number}

            return value

        node = self.visited[key]
        p, q, n = node['p'], node['q'], node['n']
        confidence = q + c*p*np.sqrt(np.sum(n, 0))/(1 + n)
        action = np.argmax(confidence, 0)

        state = node['s']
        next = sim.next_state(state, action)
        value = self.search(game, next, model)

        j, k = np.mgrid[[slice(i) for i in policy.shape[1:]]]
        node['q'][a,j,k] = (n[a,j,k]*q[a,j,k] + value)/(n[a,j,k] + 1)
        node['n'][a,j,k] += 1

        return value
