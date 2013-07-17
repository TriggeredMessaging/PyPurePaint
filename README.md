PyPurePaint
========
**PureResponseClient**  
Python API wrapper for PureResponse PAINT by Pure360  
For internal use and public release  

**MIT License (MIT)**  
Copyright (c) 2013 Triggered Messaging Ltd  
Authored by Mikael Kohlmyr  

[Triggered Messaging](http://triggeredmessaging.com)

========
**Examples**
Create a new contact list.  
Will generate a contact list from a set of dictionaries.  
```python
from pypurepaint import PureResponseClient as Pure
pure = Pure()
pure.api_authenticate('username', 'password')
pure.api\_create\_contact\_list('new\_list\_name', [{
    'email' : 'blackhole@example.none'
  , 'name'  : 'John Doe'
}])
pure.api_invalidate()
```

Send a one-to-one message.  
Optionally supply custom merge fields for the recipient as a third parameter.  
```python
from pypurepaint import PureResponseClient as Pure
pure = Pure()
pure.api_authenticate('username', 'password')
pure.api\_send\_to\_contact('blackhole@example.none', 'example\_message\_name')
pure.api_invalidate()
```
