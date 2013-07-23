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

**Bulk campaign sending to a list**  
Will send a specified email message to a given list of recipients. Uses values found in the list data if possible, falling back to default values for custom fields if necessary.
```python
from pypurepaint import PureResponseClient as Pure
pure = Pure()
pure.api_authenticate('username', 'password')
pure.api_send_to_list('example_customer_list_name', 'example_message_name')
pure.api_invalidate()
```
