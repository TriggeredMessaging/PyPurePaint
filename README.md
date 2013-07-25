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

**Add a new contact (or several) to a list.**  
Any fields that don't already exist in the list will be ignored.
```python
from pypurepaint import PureResponseClient as Pure
pure = Pure()
pure.api_authenticate('username', 'password')
pure.api_add_contact('contact_list_name', {
    'email' : 'blackhole+a@example.none'
  , 'name'  : 'Jane Doe'
})

pure.api_add_contacts('contact_list_name', [{
        'email' : 'blackhole+b@example.none'
      , 'name'  : 'Jack Doe'
    }
  , {
        'email' : 'blackhole+c@example.none'
      , 'name'  : 'Jill Doe'
    }]
)
pure.api_invalidate()
```

**Create a new email message.**  
Will create an email that can be sent as a one-to-one message or a bulk campaign email.
```python
from pypurepaint import PureResponseClient as Pure
pure = Pure()
pure.api_authenticate('username', 'password')
message_body = 'This is an <strong>example email</strong>'
pure.api_create_email('example_message_name', 'hello world', message_body)
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
pure.api_send_to_list('example_list_name', 'example_message_name')
pure.api_invalidate()
```
