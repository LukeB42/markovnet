# markovnet
Drop-in probabilistic programming.
```
pip install markovnet
```

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

Subclass instances are tunable:
```
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
```
Produces
```
{<<function <lambda> at 0x76bd6670> (3 neighbours) at 0x76bd4e10>: 0.3333333333333333,
 <<function <lambda> at 0x76bd66b0> (3 neighbours) at 0x76bd4e30>: 0.3333333333333333,
 <<function <lambda> at 0x76bd6630> (3 neighbours) at 0x76bd4df0>: 0.3333333333333333}
{<<function <lambda> at 0x76bd6670> (3 neighbours) at 0x76bd4e10>: 0.3333333333333333,
 <<function <lambda> at 0x76bd66b0> (3 neighbours) at 0x76bd4e30>: 0.3333333333333333,
 <<function <lambda> at 0x76bd65f0> (3 neighbours) at 0x76bd4db0>: 0.3333333333333333}
{<<function <lambda> at 0x76bd66b0> (3 neighbours) at 0x76bd4e30>: 0.3333333333333333,
 <<function <lambda> at 0x76bd65f0> (3 neighbours) at 0x76bd4db0>: 0.3333333333333333,
 <<function <lambda> at 0x76bd6630> (3 neighbours) at 0x76bd4df0>: 0.3333333333333333}
{<<function <lambda> at 0x76bd6670> (3 neighbours) at 0x76bd4e10>: 0.3333333333333333,
 <<function <lambda> at 0x76bd65f0> (3 neighbours) at 0x76bd4db0>: 0.3333333333333333,
 <<function <lambda> at 0x76bd6630> (3 neighbours) at 0x76bd4df0>: 0.3333333333333333}
...
{<<function <lambda> at 0x76bd6670> (3 neighbours) at 0x76bd4e10>: 0.3921568627450981,
 <<function <lambda> at 0x76bd66b0> (3 neighbours) at 0x76bd4e30>: 0.3921568627450981,
 <<function <lambda> at 0x76bd6630> (3 neighbours) at 0x76bd4df0>: 0.21568627450980396}
{<<function <lambda> at 0x76bd6670> (3 neighbours) at 0x76bd4e10>: 0.3921568627450981,
 <<function <lambda> at 0x76bd66b0> (3 neighbours) at 0x76bd4e30>: 0.3921568627450981,
 <<function <lambda> at 0x76bd65f0> (3 neighbours) at 0x76bd4db0>: 0.21568627450980396}
{<<function <lambda> at 0x76bd66b0> (3 neighbours) at 0x76bd4e30>: 0.47619047619047616,
 <<function <lambda> at 0x76bd65f0> (3 neighbours) at 0x76bd4db0>: 0.2619047619047619,
 <<function <lambda> at 0x76bd6630> (3 neighbours) at 0x76bd4df0>: 0.2619047619047619}
{<<function <lambda> at 0x76bd6670> (3 neighbours) at 0x76bd4e10>: 0.47619047619047616,
 <<function <lambda> at 0x76bd65f0> (3 neighbours) at 0x76bd4db0>: 0.2619047619047619,
 <<function <lambda> at 0x76bd6630> (3 neighbours) at 0x76bd4df0>: 0.2619047619047619}
```

Happy hacking!
