#!/usr/bin/env python
#
#   PureResponseClient
#   Python API wrapper for PureResponse by Pure360
#   For internal use and public release
#
#   MIT License
#   Copyright (c) 2013 Triggered Messaging Ltd
#   Authored by Mikael Kohlmyr
#

import datetime
from time import strftime as strftime
import suds
from suds.client import Client as SudsPaint
import StringIO
import csv
import base64

class PureResponseClient(object):
    version = '0.1'
    
    api_username    = None
    api_password    = None
    api_context     = None
    api_client      = None
    
    class API:
        RPC_LITERAL_BRANDED     = 'http://paint.pure360.com/paint.pure360.com/ctrlPaintLiteral.wsdl'
        RPC_LITERAL_UNBRANDED   = 'http://emailapi.co.uk/emailapi.co.uk/ctrlPaintLiteral.wsdl'
    
    class TYPES:
        ARRAY   = 'paintArray'
        KVP     = 'paintKeyValuePair'
        
        class KEYS:
            VALUE   = 'value'
            KEY     = 'key'
            STRING  = 'str'
            ARRAY   = 'arr'
            PAIRS   = 'pairs'
    
    class BEAN_PROCESSES:
        SEARCH          = 'search'
        STORE           = 'store'
        CREATE          = 'create'
        LOAD            = 'load'
        REMOVE          = 'remove'
        AUTHENTICATE    = 'login'
        INVALIDATE      = 'logout'
    
    class BEAN_CLASSES:
        CAMPAIGN_DELIVERY   = 'campaign_delivery'
        CAMPAIGN_EMAIL      = 'campaign_email'
        CAMPAIGN_LIST       = 'campaign_list'
        CAMPAIGN_ONE_TO_ONE = 'campaign_one2one'
        CONTEXT             = 'context'
    
    class BEAN_TYPES:
        ENTITY  = 'bus_entity'
        FACADE  = 'bus_facade'
        SEARCH  = 'bus_search'
    
    class FIELDS:
        USERNAME            = 'userName'
        PASSWORD            = 'password'
        EMAIL               = 'email'
        EMAIL_COLUMN        = 'emailCol'
        MOBILE              = 'mobile'
        MOBILE_COLUMN       = 'mobileCol'
        MESSAGE_ID          = 'messageId'
        MESSAGE_NAME        = 'messageName'
        SUBJECT             = 'subject'
        BODY_HTML           = 'bodyHtml'
        BEAN_ID             = 'beanId'
        LIST_IDS            = 'listIds'
        LIST_ID             = 'listId'
        LIST_NAME           = 'listName'
        DELIVERY_TIME       = 'deliveryDtTm'
        FOUND_DATA          = 'idData'
        RESULT              = 'result'
        RESULT_DATA         = 'resultData'
        MSG_MSG_NAME        = 'message_messageName'
        TO_ADDRESS          = 'toAddress'
        CUSTOM_DATA         = 'customData'
        UPLOAD_TYPE         = 'uploadTransactionType'
        UPLOAD_NOTIFY_URI   = 'uploadFileNotifyEmail'
        PASTE_FILE          = 'pasteFile'
        FIELD_PARTIAL       = 'field'
        COLUMN_PARTIAL      = 'Col'
        NAME_PARTIAL        = 'Name'
        BASE64_PARTIAL      = '_base64'
        FIRST_INDEX         = '0'
    
    class VALUES:
        APPEND                  = 'APPEND'
        SUCCESS                 = 'success'
        SCHEDULING_UNIT         = 'minutes'
        NEW_LINE                = '\n'
        EMPTY_STRING            = ''
        ACCOUNT_LEVEL_LITE      = 10
        ACCOUNT_LEVEL_PRO       = 20
        ACCOUNT_LEVEL_EXPERT    = 40
        SCHEDULING_DELAY        = 3
    
    class EXCEPTIONS:
        VALIDATION          = 'bean_exception_validation'
    
    class ERRORS:
        GENERIC             = 'ERROR_GENERIC'
        NOT_AUTHENTICATED   = 'ERROR_NOT_AUTHENTICATED'
        AUTH_PARAMS         = 'ERROR_AUTHENTICATION_PARAMETERS'
        AUTH_PROCESS        = 'ERROR_AUTHENTICATION_PROCESS'
        LIST_NAME_EXISTS    = 'ERROR_LIST_NAME_EXISTS'
        MESSAGE_NAME_EXISTS = 'ERROR_MESSAGE_NAME_EXISTS'
        MESSAGE_NOT_SAVED   = 'ERROR_MESSAGE_NOT_SAVED'
        MESSAGE_NOT_FOUND   = 'ERROR_MESSAGE_NOT_FOUND'
        LIST_NOT_FOUND      = 'ERROR_LIST_NOT_FOUND'
        LIST_NOT_SAVED      = 'ERROR_LIST_NOT_SAVED'
        LIST_NOT_REMOVED    = 'ERROR_LIST_NOT_REMOVED'
        CONTACT_NOT_FOUND   = 'ERROR_CONTACT_NOT_FOUND'
        BEAN_NOT_CREATED    = 'ERROR_BEAN_NOT_CREATED'
        COULD_NOT_DELIVER   = 'ERROR_COULD_NOT_DELIVER'
        INVALID_PARAMS      = 'ERROR_INVALID_PARAMETERS'
    
    def __init__(self, api_version = API.RPC_LITERAL_UNBRANDED):
        self.api_client     = SudsPaint(api_version)
    
    def api_authenticate(self, api_username = '', api_password = '', api_account_level = VALUES.ACCOUNT_LEVEL_LITE):
        """
        Authenticate to receive a context key for use in API requests.
        Worth noting that there may be unexpected behaviour for special 
        characters, it is unclear how these should be handled.
        ----------------------------------------------
        @param api_username         - username.
        @param api_password         - password.
        @param api_account_level    - account level, lite / pro / expert
                                      determines the number of custom fields 
                                      that can be used.
        """
        self.api_username       = api_username.encode('utf-8')
        self.api_password       = api_password.encode('utf-8')
        self.api_account_level  = api_account_level
        if (not api_username) or (not api_password):
            raise Exception(PureResponseClient.ERRORS.AUTH_PARAMS)
        
        auth = self.api_make_request(
            PureResponseClient.BEAN_TYPES.FACADE
          , PureResponseClient.BEAN_CLASSES.CONTEXT
          , PureResponseClient.BEAN_PROCESSES.AUTHENTICATE
          , {
                PureResponseClient.FIELDS.USERNAME : self.api_username
              , PureResponseClient.FIELDS.PASSWORD : self.api_password
            }
        )
        if self._result_success(auth):
            self.api_context = self._get_bean_id(
                auth
              , PureResponseClient.BEAN_TYPES.ENTITY
              , PureResponseClient.BEAN_CLASSES.CONTEXT
            )
            return self._dict_ok(self.api_context)
        elif self._result_exception(auth, PureResponseClient.EXCEPTIONS.VALIDATION):
            return self._dict_err(PureResponseClient.ERRORS.AUTH_PARAMS, auth)
        else:
            return self._dict_err(PureResponseClient.ERRORS.AUTH_PROCESS, auth)
    
    def api_invalidate(self):
        self.api_make_request(
            PureResponseClient.BEAN_TYPES.FACADE
          , PureResponseClient.BEAN_CLASSES.CONTEXT
          , PureResponseClient.BEAN_PROCESSES.INVALIDATE
          , no_response = True
        )
        self.api_context = None
    
    def api_send_to_list(self, list_name, message_name, scheduling_delay = {
        VALUES.SCHEDULING_UNIT : VALUES.SCHEDULING_DELAY}):
        """
        Bulk send for email campaign to a contact list.
        ----------------------------------------------
        @param list_name        - name of a contact list in the system.
        @param message_name     - name of an email in the system.
        @param scheduling_delay - [optional] define how long the system 
                                  should wait before sending the campaign, 
                                  defaults to 3 minutes.
        """
        create = self.api_make_request(
            PureResponseClient.BEAN_TYPES.FACADE
          , PureResponseClient.BEAN_CLASSES.CAMPAIGN_DELIVERY
          , PureResponseClient.BEAN_PROCESSES.CREATE
        )
        if self._result_success(create):
            delivery_input = {
                PureResponseClient.FIELDS.BEAN_ID : self._get_bean_id(
                    create
                  , PureResponseClient.BEAN_TYPES.ENTITY
                  , PureResponseClient.BEAN_CLASSES.CAMPAIGN_DELIVERY
                )
            }
            search_response = self.api_make_request(
                PureResponseClient.BEAN_TYPES.FACADE
              , PureResponseClient.BEAN_CLASSES.CAMPAIGN_LIST
              , PureResponseClient.BEAN_PROCESSES.SEARCH
              , {PureResponseClient.FIELDS.LIST_NAME : list_name}
            )
            if self._result_success(search_response):
                found = self._get_found_data(
                    search_response
                  , PureResponseClient.BEAN_TYPES.SEARCH
                  , PureResponseClient.BEAN_CLASSES.CAMPAIGN_LIST
                )
                if len(found) is not 0:
                    loaded = False
                    for key in found:
                        entity_data = found[key]
                        load_response = self.api_make_request(
                            PureResponseClient.BEAN_TYPES.FACADE
                          , PureResponseClient.BEAN_CLASSES.CAMPAIGN_LIST
                          , PureResponseClient.BEAN_PROCESSES.LOAD
                          , entity_data
                        )
                        
                        if not self._result_success(load_response):
                            continue
                        
                        load_output = self._response_data(
                            load_response
                          , PureResponseClient.BEAN_TYPES.ENTITY
                          , PureResponseClient.BEAN_CLASSES.CAMPAIGN_LIST
                        )
                        
                        loaded_name = load_output.get(
                            PureResponseClient.FIELDS.LIST_NAME
                        )
                        
                        if (unicode(loaded_name) == unicode(list_name)):
                            delivery_input[PureResponseClient.FIELDS.LIST_IDS] = {
                                PureResponseClient.FIELDS.FIRST_INDEX : found[
                                    PureResponseClient.FIELDS.FIRST_INDEX
                                ].get(PureResponseClient.FIELDS.LIST_ID)
                            }
                            loaded = True
                    if loaded is False:
                        return self._dict_err(
                            PureResponseClient.ERRORS.LIST_NOT_FOUND
                          , self._response_data(search_response)
                        )
                else:
                    return self._dict_err(
                        PureResponseClient.ERRORS.LIST_NOT_FOUND
                      , self._response_data(search_response)
                    )
            else:
                return self._dict_err(
                    PureResponseClient.ERRORS.GENERIC
                  , self._response_data(search_response)
                )
            
            search_response = self.api_make_request(
                PureResponseClient.BEAN_TYPES.FACADE
              , PureResponseClient.BEAN_CLASSES.CAMPAIGN_EMAIL
              , PureResponseClient.BEAN_PROCESSES.SEARCH
              , {PureResponseClient.FIELDS.MESSAGE_NAME : message_name}
            )
            
            if self._result_success(search_response):
                found = self._get_found_data(
                    search_response
                  , PureResponseClient.BEAN_TYPES.SEARCH
                  , PureResponseClient.BEAN_CLASSES.CAMPAIGN_EMAIL
                )
                if len(found) is not 0:
                    loaded = False
                    for key in found:
                        entity_data = found[key]
                        load_response = self.api_make_request(
                            PureResponseClient.BEAN_TYPES.FACADE
                          , PureResponseClient.BEAN_CLASSES.CAMPAIGN_EMAIL
                          , PureResponseClient.BEAN_PROCESSES.LOAD
                          , entity_data
                        )
                        
                        if not self._result_success(load_response):
                            continue
                        
                        load_output = self._response_data(
                            load_response
                          , PureResponseClient.BEAN_TYPES.ENTITY
                          , PureResponseClient.BEAN_CLASSES.CAMPAIGN_EMAIL
                        )
                        
                        loaded_name = load_output.get(
                            PureResponseClient.FIELDS.MESSAGE_NAME
                        )
                        
                        if (unicode(loaded_name) == unicode(message_name)):
                            delivery_input[
                                PureResponseClient.FIELDS.MESSAGE_ID
                            ] = found[
                                PureResponseClient.FIELDS.FIRST_INDEX
                            ].get(PureResponseClient.FIELDS.MESSAGE_ID)
                            loaded = True
                    if loaded is False:
                        return self._dict_err(
                            PureResponseClient.ERRORS.MESSAGE_NOT_FOUND
                          , self._response_data(search_response)
                        )
                else:
                    return self._dict_err(
                        PureResponseClient.ERRORS.MESSAGE_NOT_FOUND
                      , self._response_data(search_response)
                    )
            else:
                return self._dict_err(
                    PureResponseClient.ERRORS.GENERIC
                  , self._response_data(search_response)
                )
            schedule_time = datetime.datetime.now() + datetime.timedelta(**scheduling_delay)
            schedule_time = schedule_time.strftime('%d/%m/%Y %H:%M')
            delivery_input[PureResponseClient.FIELDS.DELIVERY_TIME] = schedule_time
            
            response = self.api_make_request(
                PureResponseClient.BEAN_TYPES.FACADE
              , PureResponseClient.BEAN_CLASSES.CAMPAIGN_DELIVERY
              , PureResponseClient.BEAN_PROCESSES.STORE
              , delivery_input
            )
            
            if self._result_success(response):
                return self._dict_ok(PureResponseClient.VALUES.SUCCESS)
            else:
                return self._dict_err(
                    PureResponseClient.ERRORS.COULD_NOT_DELIVER
                  , self._response_data(response)
                )
        elif create.get('result') is PureResponseClient.ERRORS.NOT_AUTHENTICATED:
            return create
        else:
            return self._dict_err(
                PureResponseClient.ERRORS.GENERIC
              , self._response_data(create)
            )
    
    def api_send_to_contact(self, email_to, message_name, custom_data = None):
        """
        Send one to one email message.
        ----------------------------------------------
        @param email_to         - email address of intended recipient
        @param message_name     - name of email message in the system
        @param custom_data      - any desired merge tags, should match 
                                  fully with ones defined in the email 
                                  unless default values are available 
                                  in the contact list
        """
        process_data = {PureResponseClient.FIELDS.MSG_MSG_NAME : message_name}
        entity_data = {PureResponseClient.FIELDS.TO_ADDRESS : email_to}
        if custom_data is not None:
            entity_data[PureResponseClient.FIELDS.CUSTOM_DATA] = custom_data
        
        create = self.api_make_request(
            PureResponseClient.BEAN_TYPES.FACADE
          , PureResponseClient.BEAN_CLASSES.CAMPAIGN_ONE_TO_ONE
          , PureResponseClient.BEAN_PROCESSES.CREATE
          , entity_data
          , process_data
        )
        
        if self._result_success(create):
            entity_data = {
                PureResponseClient.FIELDS.BEAN_ID : self._get_bean_id(
                    create
                  , PureResponseClient.BEAN_TYPES.ENTITY
                  , PureResponseClient.BEAN_CLASSES.CAMPAIGN_ONE_TO_ONE
                )
            }
            
            response = self.api_make_request(
                PureResponseClient.BEAN_TYPES.FACADE
              , PureResponseClient.BEAN_CLASSES.CAMPAIGN_ONE_TO_ONE
              , PureResponseClient.BEAN_PROCESSES.STORE
              , entity_data
            )
            
            if self._result_success(response):
                return self._dict_ok(PureResponseClient.VALUES.SUCCESS)
            else:
                return self._dict_err(
                    PureResponseClient.ERRORS.COULD_NOT_DELIVER
                  , self._response_data(response)
                )
        elif create.get('result') is PureResponseClient.ERRORS.NOT_AUTHENTICATED:
            return create
        else:
            return self._dict_err(
                PureResponseClient.ERRORS.GENERIC
              , self._response_data(create)
            )
    
    def api_create_email(self, message_name, subject, message_body):
        """
        Create a new email message for one-to-one or bulk 
        campaign sending.
        ----------------------------------------------
        @param message_name     - Unique message name.
        @param subject          - Desired subject line.
        @param message_body     - Message content, html enabled.
        """
        search_response = self.api_make_request(
            PureResponseClient.BEAN_TYPES.FACADE
          , PureResponseClient.BEAN_CLASSES.CAMPAIGN_EMAIL
          , PureResponseClient.BEAN_PROCESSES.SEARCH
          , {PureResponseClient.FIELDS.MESSAGE_NAME : message_name}
        )
        if self._result_success(search_response):
            found = self._get_found_data(
                search_response
              , PureResponseClient.BEAN_TYPES.SEARCH
              , PureResponseClient.BEAN_CLASSES.CAMPAIGN_EMAIL
            )
            
            for key in found:
                entity_data = found[key]
                load_response = self.api_make_request(
                    PureResponseClient.BEAN_TYPES.FACADE
                  , PureResponseClient.BEAN_CLASSES.CAMPAIGN_EMAIL
                  , PureResponseClient.BEAN_PROCESSES.LOAD
                  , entity_data
                )
                
                if not self._result_success(load_response):
                    continue
                
                load_output = self._response_data(
                    load_response
                  , PureResponseClient.BEAN_TYPES.ENTITY
                  , PureResponseClient.BEAN_CLASSES.CAMPAIGN_EMAIL
                )
                
                loaded_name = load_output.get(
                    PureResponseClient.FIELDS.MESSAGE_NAME
                )
                if (unicode(loaded_name) == unicode(message_name)):
                    return self._dict_err(
                        PureResponseClient.ERRORS.MESSAGE_NAME_EXISTS
                    )
            
            create_response = self.api_make_request(
                PureResponseClient.BEAN_TYPES.FACADE
              , PureResponseClient.BEAN_CLASSES.CAMPAIGN_EMAIL
              , PureResponseClient.BEAN_PROCESSES.CREATE
            )
            
            if self._result_success(create_response):
                entity_data = {
                    PureResponseClient.FIELDS.MESSAGE_NAME  : message_name
                  , PureResponseClient.FIELDS.SUBJECT       : subject
                  , PureResponseClient.FIELDS.BODY_HTML     : message_body
                  , PureResponseClient.FIELDS.BEAN_ID       : self._get_bean_id(
                        create_response
                      , PureResponseClient.BEAN_TYPES.ENTITY
                      , PureResponseClient.BEAN_CLASSES.CAMPAIGN_EMAIL
                  )
                }
                
                response = self.api_make_request(
                    PureResponseClient.BEAN_TYPES.FACADE
                  , PureResponseClient.BEAN_CLASSES.CAMPAIGN_EMAIL
                  , PureResponseClient.BEAN_PROCESSES.STORE
                  , entity_data
                )
                
                if self._result_success(response):
                    return self._dict_ok(PureResponseClient.VALUES.SUCCESS)
                else:
                    return self._dict_err(
                        PureResponseClient.ERRORS.MESSAGE_NOT_SAVED
                      , self._response_data(response)
                    )
            else:
                return self._dict_err(
                    PureResponseClient.ERRORS.BEAN_NOT_CREATED
                  , self._response_data(create_response)
                )
    
    def api_create_contact_list(self, list_name, list_data
        , notify_uri = None, overwrite_existing = False):
        """
        Create a new contact list.
        Uses internal helpers to achieve this in accordance 
        with supplied arguments.
        ----------------------------------------------
        @param list_name            - name of the contact list
        @param list_data            - list of dictionaries of records
                                      to be entered into the list as 
                                      initial data. Must be non-empty.
        @param notify_uri           - Uri which recieves notifications 
                                      when changes are made to the list.
                                      e.g. blackhole@example.none
        @param overwrite_existing   - Boolean describing the action to 
                                      be taken if a list by the given name 
                                      already exists.
        """
        search_response = self.api_make_request(
            PureResponseClient.BEAN_TYPES.FACADE
          , PureResponseClient.BEAN_CLASSES.CAMPAIGN_LIST
          , PureResponseClient.BEAN_PROCESSES.SEARCH
          , {PureResponseClient.FIELDS.LIST_NAME : list_name}
        )
        if self._result_success(search_response):
            found = self._get_found_data(
                search_response
              , PureResponseClient.BEAN_TYPES.SEARCH
              , PureResponseClient.BEAN_CLASSES.CAMPAIGN_LIST
            )
            if len(found) is 0:
                return self._api_new_contact_list_helper(list_name, list_data, notify_uri)
            elif overwrite_existing:
                remove_response = self._api_remove_contact_list_helper(list_name, found)
                if self._result_success(remove_response):
                    return self._api_new_contact_list_helper(list_name, list_data, notify_uri)
                else:
                    return remove_response
            else:
                return self._dict_err(
                    PureResponseClient.ERRORS.LIST_NAME_EXISTS
                  , self._response_data(search_response)
                )
        elif search_response.get('result') is PureResponseClient.ERRORS.NOT_AUTHENTICATED:
            return search_response
        else:
            return self._dict_err(
                PureResponseClient.ERRORS.GENERIC
              , self._response_data(search_response)
            )
    
    def _api_new_contact_list_helper(self, list_name, list_data, notify_uri):
        """
        Internal use.
        Re-usable helper which does the actual creation of the 
        new list.
        ----------------------------------------------
        @param list_name    - name of the contact list
        @param list_data    - list of dictionaries of records
                              to be entered into the list as 
                              initial data. Must be non-empty.
        @param notify_uri   - Uri which recieves notifications 
                              when changes are made to the list.
                              e.g. blackhole@example.none
        """
        create = self.api_make_request(
            PureResponseClient.BEAN_TYPES.FACADE
          , PureResponseClient.BEAN_CLASSES.CAMPAIGN_LIST
          , PureResponseClient.BEAN_PROCESSES.CREATE
        )
        if self._result_success(create):
            entity_data = {
                PureResponseClient.FIELDS.UPLOAD_NOTIFY_URI : notify_uri
              , PureResponseClient.FIELDS.LIST_NAME         : list_name
              , PureResponseClient.FIELDS.BEAN_ID           : self._get_bean_id(
                    create
                  , PureResponseClient.BEAN_TYPES.ENTITY
                  , PureResponseClient.BEAN_CLASSES.CAMPAIGN_LIST
                )
            }
            
            paste_file = self._dictlist_to_csv(list_data)
            entity_data[
                PureResponseClient.FIELDS.PASTE_FILE
              + PureResponseClient.FIELDS.BASE64_PARTIAL
            ] = base64.b64encode(paste_file)
            
            entity_data = dict(
                entity_data
              , **self._build_contact_entity(
                    paste_file
                )
            )
            response = self.api_make_request(
                PureResponseClient.BEAN_TYPES.FACADE
              , PureResponseClient.BEAN_CLASSES.CAMPAIGN_LIST
              , PureResponseClient.BEAN_PROCESSES.STORE
              , entity_data
            )
            if self._result_success(response):
                return self._dict_ok(PureResponseClient.VALUES.SUCCESS)
            else:
                return self._dict_err(
                    PureResponseClient.ERRORS.LIST_NOT_SAVED
                  , self._response_data(response)
                )
        return self._dict_err(
            PureResponseClient.ERRORS.BEAN_NOT_CREATED
          , self._response_data(search_response)
        )
    
    def _api_remove_contact_list_helper(self, list_name, found):
        """
        Remove existing list by same name.
        From a list of found beans, load them and compare their 
        names to the supplied list_name. If the names are the 
        same make a call to remove the existing bean.
        ----------------------------------------------
        @param list_name    - Name of the list to overwrite
        @param found        - Set of lists where list_name was a 
                              (potentially improper) subset of the 
                              name of the list. If equal (improper) 
                              this list will be removed.
        """
        for key in found:
            entity_data = found[key]
            load_response = self.api_make_request(
                PureResponseClient.BEAN_TYPES.FACADE
              , PureResponseClient.BEAN_CLASSES.CAMPAIGN_LIST
              , PureResponseClient.BEAN_PROCESSES.LOAD
              , entity_data
            )
            
            if not self._result_success(load_response):
                continue
            
            load_output = self._response_data(
                load_response
              , PureResponseClient.BEAN_TYPES.ENTITY
              , PureResponseClient.BEAN_CLASSES.CAMPAIGN_LIST
            )
            
            loaded_name = load_output.get(
                PureResponseClient.FIELDS.LIST_NAME
            )
            if (unicode(loaded_name) == unicode(list_name)):
                entity_data = {
                    PureResponseClient.FIELDS.BEAN_ID : load_output[
                        PureResponseClient.FIELDS.BEAN_ID
                    ]
                }
                
                return self.api_make_request(
                    PureResponseClient.BEAN_TYPES.FACADE
                  , PureResponseClient.BEAN_CLASSES.CAMPAIGN_LIST
                  , PureResponseClient.BEAN_PROCESSES.REMOVE
                  , entity_data
                )
        return self._dict_err(
            PureResponseClient.ERRORS.LIST_NOT_FOUND
          , found
        )
    
    def _api_append_contact_list(self, entity_data):
        """
        Internal use.
        Abstraction layer between built entity data 
        (self._api_add_contact_ambiguous) and sending 
        request (self.api_make_request).
        ----------------------------------------------
        @param entity_data      - information about the contacts 
                                  to append as well as general query 
                                  information
        """
        create = self.api_make_request(
            PureResponseClient.BEAN_TYPES.FACADE
          , PureResponseClient.BEAN_CLASSES.CAMPAIGN_LIST
          , PureResponseClient.BEAN_PROCESSES.CREATE
        )
        if self._result_success(create):
            entity_data[PureResponseClient.FIELDS.BEAN_ID] = self._get_bean_id(
                create
              , PureResponseClient.BEAN_TYPES.ENTITY
              , PureResponseClient.BEAN_CLASSES.CAMPAIGN_LIST
            )
            response = self.api_make_request(
                PureResponseClient.BEAN_TYPES.FACADE
              , PureResponseClient.BEAN_CLASSES.CAMPAIGN_LIST
              , PureResponseClient.BEAN_PROCESSES.STORE
              , entity_data
            )
            
            if self._result_success(response):
                return self._dict_ok(PureResponseClient.VALUES.SUCCESS)
            else:
                return self._dict_err(
                    PureResponseClient.ERRORS.LIST_NOT_SAVED
                  , self._response_data(response)
                )
        elif create.get('result') is PureResponseClient.ERRORS.NOT_AUTHENTICATED:
            return create
        else:
            return self._dict_err(
                PureResponseClient.ERRORS.GENERIC
              , self._response_data(create)
            )
    
    def _api_add_contact_ambiguous(self, list_name, contact_data):
        """
        Internal use.
        Abstraction layer between publically exposed functions 
        (self.api_add_contact, self.api_add_contacts) and request 
        handling (self._api_append_contact_list).
        ----------------------------------------------
        @param list_name        - name of contact list to append to.
        @param contact_data     - dictionary or list of dictionaries 
                                  containing contact data to append.
        """
        entity_data = {
            PureResponseClient.FIELDS.LIST_NAME     : list_name
          , PureResponseClient.FIELDS.UPLOAD_TYPE   : PureResponseClient.VALUES.APPEND
        }
        if isinstance(contact_data, list):
            paste_file = self._dictlist_to_csv(contact_data)
        else:
            paste_file = self._dict_to_csv(contact_data)
		
        entity_data[
            PureResponseClient.FIELDS.PASTE_FILE
          + PureResponseClient.FIELDS.BASE64_PARTIAL
        ] = base64.b64encode(paste_file)
        entity_data = dict(
            entity_data
          , **self._build_contact_entity(paste_file)
        )
        return self._api_append_contact_list(entity_data)
        
    def api_add_contact(self, list_name, contact):
        """
        Add single contact to a given contact list.
        Alias for _api_add_contact_ambiguous.
        ----------------------------------------------
        @param list_name        - name of contact list to append to
        @param contact          - dictionary of contact data
        """
        return self._api_add_contact_ambiguous(list_name, contact)
    
    def api_add_contacts(self, list_name, contacts):
        """
        Add multiple contacts to a given contact list.
        Alias for _api_add_contact_ambiguous.
        The contacts parameter should be a list of dictionaries. 
        The dictionaries do not require matching key sets as a 
        master-list of keys is generated in the process of 
        producing a csv to upload.
        ----------------------------------------------
        @param list_name        - name of contact list to append to
        @param contacts         - list of dictionaries
        """
        return self._api_add_contact_ambiguous(list_name, contacts)
    
    def api_make_request(self, bean_type, bean_class, bean_process
      , entity_data = None, process_data = None, no_response = False):
        if self.api_context or (bean_process is PureResponseClient.BEAN_PROCESSES.AUTHENTICATE):
            api_context = self.api_context or suds.null()
            response    = self.api_client.service.handleRequest(
                            api_context
                          , bean_type + '_' + bean_class
                          , bean_process
                          , self._dict_to_ptarr(entity_data)
                          , self._dict_to_ptarr(process_data)
                        )
            if no_response:
                return True
            else:
                return self._ptarr_to_dict(response)
        else:
            return self._dict_err(
                PureResponseClient.ERRORS.NOT_AUTHENTICATED
              , None
            )
    
    def _response_data(self, response_dict, bean_type = None
        , bean_class = None, field = FIELDS.RESULT_DATA):
        if (bean_type is not None) and (bean_class is not None):
            return response_dict[field][bean_type + '_' + bean_class]
        elif (bean_type is not None) or (bean_class is not None):
            raise Exception(PureResponseClient.ERRORS.INVALID_PARAMS)
        else:
            return response_dict[field]
    
    def _get_result(self, response):
        return self._response_data(response, field=PureResponseClient.FIELDS.RESULT)
    
    def _result_success(self, response):
        return self._get_result(response) == PureResponseClient.VALUES.SUCCESS
    
    def _get_bean_id(self, response, bean_type, bean_class):
        return self._response_data(
            response
          , bean_type
          , bean_class
        ).get(PureResponseClient.FIELDS.BEAN_ID)
    
    def _get_found_data(self, response, bean_type, bean_class):
        return self._response_data(
            response
          , bean_type
          , bean_class
        ).get(PureResponseClient.FIELDS.FOUND_DATA)
    
    def _result_exception(self, response, exception):
        return self._get_result(response) is exception
    
    def _dict_ok(self, result = VALUES.SUCCESS):
        return {'ok' : True, 'result': result}
    
    def _dict_err(self, error = ERRORS.GENERIC, meta = None):
        return {'ok' : False, 'result' : error, 'meta' : meta}
    
    def _unicode_exceptions(self, key):
        exceptions = [
            PureResponseClient.FIELDS.BEAN_ID
          , PureResponseClient.FIELDS.MESSAGE_ID
          , PureResponseClient.FIELDS.LIST_ID
        ]
        if key.isdigit():
            return True
        else:
            for field in exceptions:
                if key == unicode(field):
                    return True
            return False
    
    def _dict_to_ptarr(self, dict_):
        """
        Internal use.
        Convert dictionaries to 'paintArray' objects using suds.
        Works some encoding magic in the process in order to be 
        compliant with the expectations and requirements of the 
        API while attempting to maintain the integrity of the 
        data content.
        ----------------------------------------------
        @param dict_        - dictionary of data to convert.
        """
        if not dict_:
            return suds.null()
        arr_ = self.api_client.factory.create(PureResponseClient.TYPES.ARRAY)
        for key_ in dict_:
            kvp_ = self.api_client.factory.create(PureResponseClient.TYPES.KVP)
            setattr(kvp_, PureResponseClient.TYPES.KEYS.KEY, key_.encode('ascii', 'ignore'))
            val_ = getattr(kvp_, PureResponseClient.TYPES.KEYS.VALUE)
            if isinstance(dict_[key_], dict):
                setattr(val_, PureResponseClient.TYPES.KEYS.ARRAY, self._dict_to_ptarr(dict_[key_]))
            elif (isinstance(dict_[key_], str) or 
                (isinstance(dict_[key_], unicode) and self._unicode_exceptions(key_))):
                setattr(val_, PureResponseClient.TYPES.KEYS.STRING, dict_[key_].encode('utf-8'))
            elif isinstance(dict_[key_], unicode):
                setattr(val_, PureResponseClient.TYPES.KEYS.STRING, base64.b64encode(
                    dict_[key_].encode('utf-8')
                ))
                setattr(
                    kvp_
                  , PureResponseClient.TYPES.KEYS.KEY
                  , getattr(kvp_, PureResponseClient.TYPES.KEYS.KEY) 
                    + PureResponseClient.FIELDS.BASE64_PARTIAL
                )
            else:
                setattr(val_, PureResponseClient.TYPES.KEYS.STRING, str(dict_[key_]))
            getattr(arr_, PureResponseClient.TYPES.KEYS.PAIRS).append(kvp_)
        return arr_
    
    def _ptarr_to_dict(self, ptarr):
        """
        Internal use.
        Convert 'paintArray' objects to dictionaries.
        ----------------------------------------------
        @param ptarr        - 'paintArray' to convert.
        """
        dict_ = {}
        if not hasattr(ptarr, PureResponseClient.TYPES.KEYS.PAIRS):
            return None
        for pair in getattr(ptarr, PureResponseClient.TYPES.KEYS.PAIRS):
            val_ = getattr(pair, PureResponseClient.TYPES.KEYS.VALUE)
            key_ = getattr(pair, PureResponseClient.TYPES.KEYS.KEY)
            if hasattr(val_, PureResponseClient.TYPES.KEYS.ARRAY):
                arr_ = getattr(val_, PureResponseClient.TYPES.KEYS.ARRAY)
                if not arr_:
                    dict_[key_] = {}
                else:
                    dict_[key_] = self._ptarr_to_dict(arr_)
            elif hasattr(val_, PureResponseClient.TYPES.KEYS.STRING):
                dict_[key_] = getattr(val_, PureResponseClient.TYPES.KEYS.STRING)
        return dict_
    
    def _build_contact_entity(self, csv_string):
        """
        Internal use.
        Builds fields necessary to supply csv data to the API.
        ----------------------------------------------
        @param csv_string       - csv data to build fields for.
        """
        entity_data = dict()
        count       = 0
        custom      = 0
        for key in csv_string.splitlines()[0].split(','):
            if ((key is PureResponseClient.FIELDS.EMAIL) or 
                (key == unicode(PureResponseClient.FIELDS.EMAIL))):
                entity_data[PureResponseClient.FIELDS.EMAIL_COLUMN] = count
            elif ((key is PureResponseClient.FIELDS.MOBILE) or 
                (key == unicode(PureResponseClient.FIELDS.MOBILE))):
                entity_data[PureResponseClient.FIELDS.MOBILE_COLUMN] = count
            else:
                field_whole = PureResponseClient.FIELDS.FIELD_PARTIAL + str(count + 1)
                entity_data[
                    field_whole
                  + PureResponseClient.FIELDS.COLUMN_PARTIAL
                ] = count
                entity_data[
                    field_whole
                  + PureResponseClient.FIELDS.NAME_PARTIAL
                ] = key.replace(' ',  '_')
                custom += 1
                if custom is self.api_account_level:
                    break
            count += 1
        return entity_data
    
    def _fixtype_value(self, key, value):
        if isinstance(value, str) or isinstance(value, unicode):
            return (value.encode('utf-8')).replace(
                PureResponseClient.VALUES.NEW_LINE
              , PureResponseClient.VALUES.EMPTY_STRING
            )
        else:
            return str(value)
    
    def _dictlist_to_csv(self, list_):
        """
        Internal use.
        Convert list of dictionaries into csv data.
        The dictionaries may non-matching keys as a 
        master-list of keys will be built in the process.
        ----------------------------------------------
        @param list_        - list of dictionaries to convert.
        """
        master = set()
        for row in list_:
            master = master.union(row.keys())
        master = sorted(list(master))
        csv_string = StringIO.StringIO()
        csv_writer = csv.DictWriter(csv_string, master)
        csv_writer.writerow(dict([ (k, k) for k in master ]))
        for item in list_:
            csv_writer.writerow(dict(
                [ (k, self._fixtype_value(k, v)) for k, v in item.iteritems() ]
            ))
        output = csv_string.getvalue()
        csv_string.close()
        return output
        
    def _dict_to_csv(self, dict_):
        """
        Internal use.
        Convert dictionary into csv data.
        Simple proxy to self._dictlist_to_csv.
        ----------------------------------------------
        @param dict_        - dictionary to convert.
        """
        return self._dictlist_to_csv([dict_])

