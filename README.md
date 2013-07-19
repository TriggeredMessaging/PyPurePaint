PyPurePaint
========
**PureResponseClient**  
Python API wrapper for PureResponse PAINT by Pure360  
For internal use and public release  

**MIT License (MIT)**  
Copyright (c) 2013 Triggered Messaging Ltd  
Authored by Mikael Kohlmyr  

[Triggered Messaging](http://triggeredmessaging.com),  
[Pure360](http://www.pure360.com/)

========
**Create a new contact list.**  
Will generate a contact list from a set of dictionaries.
```python
from pypurepaint import PureResponseClient as Pure
pure = Pure()
pure.api_authenticate('username', 'password')
pure.api_create_contact_list('new_list_name', [{
    'email' : 'blackhole@example.none'
  , 'name'  : 'John Doe'
}])
pure.api_invalidate()
```

**Send a one-to-one message.**  
Optionally supply custom merge fields for the recipient as a third parameter.
```python
from pypurepaint import PureResponseClient as Pure
pure = Pure()
pure.api_authenticate('username', 'password')
pure.api_send_to_contact('blackhole@example.none', 'example_message_name')
pure.api_invalidate()
```
