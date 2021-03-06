#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# Drop-in probabilistic programming.
# (C) Luke Brooks, 2016.
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

"""
 >>> from markovnet import MarkovNet, Func
 >>> a = Func(lambda x: x ** 2)
 >>> b = Func(lambda x: x ** 3)
 >>> c = Func(lambda x: x ** 4)
 >>> d = Func(lambda x: x ** 5)
 
 >>> a.update({b: 50, c: 20, d: 30})
 >>> b.update({a: 5,  c: 30, d: 30})
 >>> c.update({a: 90, c: 20})
 >>> d.update({a: 80, b: 50, c: 20})
 
 >>> net = MarkovNet(a, b, c, d)
 >>> net(5)
 3125
 >>> net(5)
 25

"""
import random

class ProbDist(dict):
    """
    A Probability Distribution; an {outcome: probability} mapping.
    bag94 = ProbDist(brown=30, yellow=20, red=20, green=10, orange=10, tan=10)
    bag96 = ProbDist(blue=24, green=20, orange=16, yellow=14, red=13, brown=13)
    """
    def __init__(self, mapping=(), **kwargs):
        self.update(mapping, **kwargs)
        # Make probabilities sum to 1.0; assert no negative probabilities
        total = sum(self.values())
        for outcome in self:
            self[outcome] = self[outcome] / total
            assert self[outcome] >= 0

    @property
    def pick(self):
        n = random.uniform(0, 1)
        selection = min(self.values(), key=lambda x: abs(x - n))
        
        # Pick at random to solve for competing equiprobable solutions.
        if list(self.values()).count(selection) > 1:
            c = list(filter(lambda x: x[1] == selection, self.items()))
            return random.choice(c)[0]
        
        for key, value in self.items():
            if value == selection:
                return key

    def joint(self, B, sep=''):
        """The joint distribution of two independent probability distributions. 
        Result is all entries of the form {a+sep+b: P(a)*P(b)}"""
        return ProbDist({a + sep + b: self[a] * B[b]
                        for a in self
                        for b in B})

class Func(object):
    """
    Wrap a callable in order to associate it with other functions.

    The .gain class attribute can be used to control the base probability
    of selection for all subclass instances.

    class XFunc(markovnet.Func):
        gain = -0.3
    
    a = XFunc(lambda x: x ** 2)
    b = XFunc(lambda x: x ** 4, neighbours=a)
    a.update(b)

    XFunc.gain = 0.9
    """
    gain  = 0.0 

    def __init__(self, func, P=1.0, neighbours={}):
        self.P          = P
        self.func       = func
        self.neighbours = {}
        
        self.update(neighbours)

    def update(self, neighbours):
        """
        Add neighbours to this instance.
        """
        if isinstance(neighbours, (list, tuple)):
                for n in neighbours:
                    self.neighbours.update(n.to_dict())
        
        elif isinstance(neighbours, dict):
            self.neighbours.update(neighbours)

        elif hasattr(neighbours, "to_dict"):
            self.neighbours.update(neighbours.to_dict())

    @property
    def proba(self):
        return self.P + self.__class__.gain

    @property
    def probabilities(self):
        """
        Return the probability distribution over
        neighbouring functions.
        """
        weights = {}
        for func, weight in self.neighbours.items():
            weights[func] = weight + func.proba
        
        return ProbDist(weights, **{})
    
    def travel(self):
        """
        Return a neighbouring function, providing we have neighbours.

        Returns self if no neighbours are found.
        """
        if not self.neighbours:
            return self

        if isinstance(self.neighbours, list):
            start = {}
            for node in self.neighbours:
                start.update(node.to_dict())
            pdist = ProbDist(start, **{})
            return pdist.pick

        return self.probabilities.pick

    def to_dict(self):
        """
        Use .to_dict to pass singular instances of this class to the .update method.

        """
        return {self: self.proba}

    def __call__(self, *args, **kwargs):
        """
        Invoke the attached function.
        """
        if not self.func:
            raise Exception("No function associated with %s when __call__ invoked." % repr(self))
        return self.func(*args, **kwargs)

    def __repr__(self):
        return "<%s (%i neighbours) at %s>" % \
            (str(self.func), len(self.neighbours), hex(id(self)))

class MarkovNet(list):
    def __init__(self, *args):
        """
        Implements a callable container that substitutes for its contents
        either based on a Hidden Markov Model using markovnet.Func, or
        at random.

        Examples:
            
            f = MarkovNet(lambda x: x ** 2, lambda x: x ** 5)
            f(4) # 16
            f(4) # 1024

            a = Func(lambda x: x ** 2)
            b = Func(lambda x: x ** 3)
            c = Func(lambda x: x ** 4)
            d = Func(lambda x: x ** 5)
            a.update({b: 50, c: 20, d: 30})
            b.update({a: 5,  c: 30, d: 30})
            c.update({a: 90, c: 20})
            d.update({a: 80, b: 50, c: 20})
            f = MarkovNet(a, b, c, d)
            f(5) # 3125
            f(5) # 25
        
        """
        if not all(map(lambda x: callable(x), args)):
            raise Exception("All nodes must have a __call__ method.")
 
        list.__init__(self, args)
        self.active_node = None

    def append(self, func):
        if not callable(func):
            raise Exception("%s is not callable." % repr(func))
        super(MarkovNet, self).append(func)

    def insert(self, index, func):
        if not callable(func):
            raise Exception("%s is not callable." % repr(func))
        super(MarkovNet, self).insert(index, func)

    def extend(self, iterable):
        for func in iterable:
            if not callable(func):
                raise Exception("%s is not callable." % repr(func))
            super(MarkovNet, self).append(func)
            
    def __call__(self, *args, **kwargs):
        """
        Probabilistically select an object that implements Func to return.
       
        Callables are chosen at random if all members of self don't implement
        markovnet.Func.
        """
        if not self.active_node:
            # Compute probabilities of all nodes in self implement markovnet.Func,
            # otherwise pick a callable at random.
            if all(map(lambda x: hasattr(x, "to_dict"), self)):
                start = {}
                for func in self:
                    start.update(func.to_dict())
                pdist = ProbDist(start, **{})
                self.active_node = pdist.pick
            else:
                self.active_node = random.choice(self)
        
        result = self.active_node(*args, **kwargs)
        
        if not hasattr(self.active_node, "travel"):
            self.active_node = None
        else:
            self.active_node = self.active_node.travel()
       
        return result

    def __repr__(self):
        r = "<MarkovNet %s with " % str(list(self))
        if not self.active_node:
            r += "no active node"
        else:
            r += "active node %s" % self.active_node
        r += " at %s>" % hex(id(self))
        return r

if __name__ == "__main__":
    import pprint
    
    class XFunc(Func): pass
    
    a = XFunc(lambda x: x ** 2)
    b = XFunc(lambda x: x ** 3)
    
    c = Func(lambda x: x ** 4)
    d = Func(lambda x: x ** 5)
    
    a.update([b, c, d])
    b.update([a, c, d])
    c.update([a, b, d])
    d.update([a, b, c])
    
    f = MarkovNet(a, b, c, d)
    
    for func in f.funcs:
        print(pprint.pformat(func.probabilities))

    print("...")
    
    XFunc.gain = -0.9
    
    for func in f.funcs:
        print(pprint.pformat(func.probabilities))
