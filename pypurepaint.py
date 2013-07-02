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
        RPC_ENCODED_BRANDED     = 'http://paint.pure360.com/paint.pure360.com/ctrlPaint.wsdl'
        RPC_LITERAL_BRANDED     = 'http://paint.pure360.com/paint.pure360.com/ctrlPaintLiteral.wsdl'
        RPC_ENCODED_UNBRANDED   = 'http://emailapi.co.uk/emailapi.co.uk/ctrlPaint.wsdl'
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
        USERNAME        = 'userName'
        PASSWORD        = 'password'
        EMAIL           = 'email'
        EMAIL_COLUMN    = 'emailCol'
        MOBILE          = 'mobile'
        MOBILE_COLUMN   = 'mobileCol'
        MESSAGE_ID      = 'messageId'
        MESSAGE_NAME    = 'messageName'
        BEAN_ID         = 'beanId'
        LIST_IDS        = 'listIds'
        LIST_ID         = 'listId'
        LIST_NAME       = 'listName'
        DELIVERY_TIME   = 'deliveryDtTm'
        FOUND_DATA      = 'idData'
        RESULT          = 'result'
        RESULT_DATA     = 'resultData'
        MSG_MSG_NAME    = 'message_messageName'
        TO_ADDRESS      = 'toAddress'
        CUSTOM_DATA     = 'customData'
        UPLOAD_TYPE     = 'uploadTransactionType'
        PASTE_FILE      = 'pasteFile'
        FIELD_PARTIAL   = 'field'
        COLUMN_PARTIAL  = 'Col'
        NAME_PARTIAL    = 'Name'
        BASE64_PARTIAL  = '_base64'
    
    class VALUES:
        APPEND                  = 'APPEND'
        SUCCESS                 = 'success'
        SCHEDULING_UNIT         = 'minutes'
        SCHEDULING_DELAY        = 3
    
    class EXCEPTIONS:
        VALIDATION          = 'bean_exception_validation'
    
    class ERRORS:
        GENERIC             = 'ERROR_GENERIC'
        NOT_AUTHENTICATED   = 'ERROR_NOT_AUTHENTICATED'
        AUTH_PARAMS         = 'ERROR_AUTHENTICATION_PARAMETERS'
        AUTH_PROCESS        = 'ERROR_AUTHENTICATION_PROCESS'
        LIST_NOT_FOUND      = 'ERROR_LIST_NOT_FOUND'
        LIST_NOT_SAVED      = 'ERROR_LIST_NOT_SAVED'
        CONTACT_NOT_FOUND   = 'ERROR_CONTACT_NOT_FOUND'
        CAMPAIGN_NOT_FOUND  = 'ERROR_CAMPAIGN_NOT_FOUND'
        BEAN_NOT_CREATED    = 'ERROR_BEAN_NOT_CREATED'
        COULD_NOT_DELIVER   = 'ERROR_COULD_NOT_DELIVER'
        INVALID_PARAMS      = 'ERROR_INVALID_PARAMETERS'
    
    def __init__(self, api_version = API.RPC_LITERAL_UNBRANDED):
        self.api_client     = SudsPaint(api_version)
    
    def api_authenticate(self, api_username = '', api_password = ''):
        self.api_username = api_username.encode('utf-8')
        self.api_password = api_password.encode('utf-8')
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
        create = self.api_make_request(
            PureResponseClient.BEAN_TYPES.FACADE
          , PureResponseClient.BEAN_CLASSES.CAMPAIGN_DELIVERY
          , PureResponseClient.BEAN_PROCESSES.CREATE
        )
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
                delivery_input[PureResponseClient.FIELDS.LIST_IDS] = {
                    '0': found['0'].get(PureResponseClient.FIELDS.LIST_ID)
                }
            else:
                return self._dict_err(
                    PureResponseClient.ERRORS.ERROR_CAMPAIGN_NOT_FOUND
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
            if len(found) is 1:
                delivery_input[
                    PureResponseClient.FIELDS.MESSAGE_ID
                ] = found['0'].get(PureResponseClient.FIELDS.MESSAGE_ID)
            else:
                return self._dict_err(
                    PureResponseClient.ERRORS.CAMPAIGN_NOT_FOUND
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
    
    def api_send_to_contact(self, email_to, message_name, custom_data = None):
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
        return self._dict_err(
            PureResponseClient.ERRORS.GENERIC
          , self._response_data(create)
        )
    
    def _api_append_contact_list(self, entity_data):
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
        return self._dict_err(
            PureResponseClient.ERRORS.GENERIC
          , self._response_data(create)
        )
    
    def _api_add_contact_ambiguous(self, list_name, contact_data):
        entity_data = {
            PureResponseClient.FIELDS.LIST_NAME     : list_name
          , PureResponseClient.FIELDS.UPLOAD_TYPE   : PureResponseClient.VALUES.APPEND
        }
        if isinstance(contact_data, list):
            paste_file = self._dictlist_to_csv(contact_data)
        else:
            paste_file = self._dict_to_csv(contact_data)
        entity_data[PureResponseClient.FIELDS.PASTE_FILE
            + PureResponseClient.FIELDS.BASE64_PARTIAL] = base64.b64encode(
            paste_file
        )
        entity_data = dict(
            entity_data
          , **self._build_contact_entity(paste_file)
        )
        return self._api_append_contact_list(entity_data)
        
    def api_add_contact(self, list_name, contact):
        return self._api_add_contact_ambiguous(list_name, contact)
    
    def api_add_contacts(self, list_name, contacts):
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
    
    def _dict_ok(self, result):
        return {'ok' : True, 'result': result}
    
    def _dict_err(self, error, meta):
        return {'ok' : False, 'result' : error, 'meta' : meta}
    
    def _unicode_exceptions(self, key):
        exceptions = [
            PureResponseClient.FIELDS.BEAN_ID
          , PureResponseClient.FIELDS.MESSAGE_ID
        ]
        if key.isdigit():
            return True
        else:
            for field in exceptions:
                if key == unicode(field):
                    return True
            return False
    
    def _dict_to_ptarr(self, dict_):
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
                setattr(val_, PureResponseClient.TYPES.KEYS.STRING, dict_[key_])
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
                field_whole = PureResponseClient.FIELDS.FIELD_PARTIAL + str(count)
                entity_data[
                    field_whole
                  + PureResponseClient.FIELDS.COLUMN_PARTIAL
                ] = count
                entity_data[
                    field_whole
                  + PureResponseClient.FIELDS.NAME_PARTIAL
                ] = key.replace(' ',  '_')
                custom += 1
                if custom is 10:
                    break
            count += 1
        return entity_data
    
    def _fixtype_value(self, value):
        if isinstance(value, str) or isinstance(value, unicode):
            return value
        else:
            return str(value)
    
    def _dictlist_to_csv(self, list_):
        master = set()
        for row in list_:
            master = master.union(row.keys())
        master = sorted(list(master))
        csv_string = StringIO.StringIO()
        csv_writer = csv.DictWriter(csv_string, master)
        csv_writer.writerow(dict([ (k, k) for k in master ]))
        for item in list_:
            csv_writer.writerow(dict(
                [ (k, self._fixtype_value(v).encode('utf-8')) for k, v in item.iteritems() ]
            ))
        output = csv_string.getvalue()
        csv_string.close()
        return output
        
    def _dict_to_csv(self, dict_):
        return self._dictlist_to_csv([dict_])
    
    
    
    
    
    
    
    
    
    
    
    


