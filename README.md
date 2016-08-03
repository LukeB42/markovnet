# markovnet
Drop-in probabilistic programming.

```
>>> from markovnet import MarkovNet, Func
>>> a = Func(lambda x: x ** 2)
>>> b = Func(lambda x: x ** 3)
>>> c = Func(lambda x: x ** 4)
>>> d = Func(lambda x: x ** 5)

>>> a.update({b: 50, c: 20, d: 30})
>>> b.update({a: 5,  0, c: 30, d: 30})
>>> c.update({a: 90, 0, c: 20       })
>>> d.update({a: 80, 0, b: 50, c: 20})

>>> net = MarkovNet(a, b, c, d)
>>> net(5)
3125
>>> net(5)
25
```
