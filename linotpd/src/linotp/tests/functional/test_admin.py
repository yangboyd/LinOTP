# -*- coding: utf-8 -*-
#
#    LinOTP - the open source solution for two factor authentication
#    Copyright (C) 2010 - 2019 KeyIdentity GmbH
#
#    This file is part of LinOTP server.
#
#    This program is free software: you can redistribute it and/or
#    modify it under the terms of the GNU Affero General Public
#    License, version 3, as published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the
#               GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#    E-mail: linotp@keyidentity.com
#    Contact: www.linotp.org
#    Support: www.keyidentity.com
#


"""
"""

import json
import logging
from linotp.tests import TestController

log = logging.getLogger(__name__)

class TestAdminController(TestController):


    def setUp(self):
        TestController.setUp(self)
        self.set_config_selftest()
        self.create_common_resolvers()
        self.create_common_realms()

    def tearDown(self):
        self.delete_all_token()
        self.delete_all_realms()
        self.delete_all_resolvers()
        TestController.tearDown(self)

    def createToken3(self):
        parameters = {
                      "serial": "003e808e",
                      "otpkey" : "e56eb2bcbafb2eea9bce9463f550f86d587d6c71",
                      "description" : "my EToken",
                      }

        response = self.make_admin_request('init', params=parameters)
        self.assertTrue('"value": true' in response, response)

    def createToken2(self, serial="F722362"):
        parameters = {
                      "serial"  : serial,
                      "otpkey"  : "AD8EABE235FC57C815B26CEF3709075580B44738",
                      "description" : "TestToken" + serial,
                      }

        response = self.make_admin_request('init', params=parameters)
        self.assertTrue('"value": true' in response, response)
        return serial

    def createTokenSHA256(self, serial="SHA256"):
        parameters = {
                      "serial" : serial,
                      "otpkey" : "47F6EE05C06FA1CDB8B9AADF520FCF86221DB0A107731452AE140EED0EB518B0",
                      "type" : "hmac",
                      "hashlib" : "sha256"
                      }
        response = self.make_admin_request('init', params=parameters)
        self.assertTrue('"value": true' in response, response)
        return serial

    def createSPASS(self, serial="LSSP0001", pin="1test@pin!42"):
        parameters = {
                      "serial" : serial,
                      "type"   : "spass",
                      "pin"    : pin
                      }
        response = self.make_admin_request('init', params=parameters)
        self.assertTrue('"value": true' in response, response)
        return serial

    def createToken(self):
        parameters = {
                      "serial"  : "F722362",
                      "otpkey"  : "AD8EABE235FC57C815B26CEF3709075580B44738",
                      "user"    : "root",
                      "pin"     : "pin",
                      "description" : "TestToken1",
                      }

        response = self.make_admin_request('init', params=parameters)
        self.assertTrue('"value": true' in response, response)

        parameters = {
                      "serial": "F722363",
                      "otpkey" : "AD8EABE235FC57C815B26CEF3709075580B4473880B44738",
                      "user" : "root",
                      "pin": "pin",
                      "description" : "TestToken2",
                      }

        response = self.make_admin_request('init', params=parameters)
        self.assertTrue('"value": true' in response, response)

        parameters = {
                      "serial": "F722364",
                      "otpkey" : "AD8EABE235FC57C815B26CEF37090755",
                      "user" : "root",
                      "pin": "pin",
                      "description" : "TestToken3",
                      }

        response = self.make_admin_request('init', params=parameters)
        self.assertTrue('"value": true' in response, response)

        ## test the update
        parameters = {
                      "serial": "F722364",
                      "otpkey" : "AD8EABE235FC57C815B26CEF37090755",
                      "user" : "root",
                      "pin": "Pin3",
                      "description" : "TestToken3",
                      }

        response = self.make_admin_request('init', params=parameters)
        #log.error("response %s\n",response)
        self.assertTrue('"value": true' in response, response)

    def removeTokenByUser(self, user):
        ### final delete all tokens of user root
        parameters = {
                      "user": user,
                      }

        response = self.make_admin_request('remove', params=parameters)
        return response


    def showToken(self):
        response = self.make_admin_request('show')
        return response

    def test_0000_000(self):
        self.delete_all_token()

    def test_set(self):
        self.createToken()

        parameters = {
                      "serial": "F722364",
                      "pin": "pin",
                      "MaxFailCount" : "20",
                      "SyncWindow" : "400",
                      "OtpLen" : "6",
                      "hashlib" : "sha256"
                      }

        response = self.make_admin_request('set', params=parameters)
        #log.debug("response %s",response)
        self.assertTrue('"set pin": 1' in response, response)
        self.assertTrue('"set SyncWindow": 1' in response, response)
        self.assertTrue('"set OtpLen": 1' in response, response)
        self.assertTrue('"set MaxFailCount": 1' in response, response)
        self.assertTrue('"set hashlib": 1' in response, response)

        parameters = {
                      "user": "root",
                      "pin": "pin",
                      "MaxFailCount" : "20",
                      "SyncWindow" : "400",
                      "OtpLen" : "6",
                      }

        response = self.make_admin_request('set', params=parameters)
        #log.error("response %s",response)
        self.assertTrue('"set pin": 3' in response, response)
        self.assertTrue('"set SyncWindow": 3' in response, response)
        self.assertTrue('"set OtpLen": 3' in response, response)
        self.assertTrue('"set MaxFailCount": 3' in response, response)

        self.delete_token("F722362")
        response = self.removeTokenByUser("root")
        self.assertTrue('"value": 2' in response, response)

    def test_remove(self):
        self.createToken()
        response = self.removeTokenByUser("root")
        log.debug(response)

    def test_userlist(self):
        """
        test the admin/userlist for iteration reply and paging

        scope of test:
        - stabilty of the userlist api
        - support of result paging

        """
        # first standard query for users
        parameters = {"username": "*"}
        response = self.make_admin_request('userlist',
                                params=parameters)
        self.assertTrue('"status": true,' in response, response)
        resp = json.loads(response.body)
        values = resp.get('result', {}).get('value', [])
        self.assertTrue(len(values) > 15, "not enough users returned %r" % resp)

        # paged query
        parameters = {"username": "*", "rp": 5, "page": 2}
        response = self.make_admin_request('userlist',
                                params=parameters)
        self.assertTrue('"status": true,' in response, response)
        resp = json.loads(response.body)

        entries = parameters['rp']
        values = resp.get('result', {}).get('value', [])
        self.assertEqual(len(values), parameters['rp'], resp)

        num = parameters['rp'] * (parameters['page'] + 1)
        queried = resp.get('result', {}).get('queried', 0)
        self.assertEqual(queried, num, resp)

        # test for optional pagesize, which falls back to the pagesize of 15
        parameters = {"username": "*", "page": 0}
        response = self.make_admin_request('userlist',
                                params=parameters)
        self.assertTrue('"status": true,' in response, response)
        resp = json.loads(response.body)
        values = resp.get('result', {}).get('value', [])
        self.assertEqual(len(values), 15, resp)

        # test for ValueError Exception if page or rp is not of int
        # though the returned data is a json response
        parameters = {"username": "*", "page": 'page'}
        response = self.make_admin_request('userlist',
                                params=parameters)
        # check that status is false
        self.assertTrue('"status": false,' in response, response)
        # check for valid json
        resp = json.loads(response.body)
        value = resp.get('result', {}).get('error', {}).get("code", 0)
        self.assertEqual(value, 9876, resp)

        return

    def test_enable(self):
        self.createToken()
        parameters = {"serial": "F722364"}
        response = self.make_admin_request('disable', params=parameters)
        self.assertTrue('"value": 1' in response, response)

        parameters = {"serial": "F722364"}
        response = self.make_admin_request('show', params=parameters)

        self.assertTrue('false' in response, response)
        self.assertTrue('F722364' in response, response)

        parameters = {"serial": "F722364"}
        response = self.make_admin_request('enable', params=parameters)
        self.assertTrue('"value": 1' in response, response)

        parameters = {"serial": "F722364"}
        response = self.make_admin_request('show', params=parameters)

        self.assertTrue('true' in response, response)
        self.assertTrue('F722364' in response, response)

        self.removeTokenByUser("root")

    def test_resync(self):

        self.createToken()

        ## test resync of token 2
        parameters = {"user": "root", "otp1": "359864", "otp2": "348449" }
        response = self.make_admin_request('resync', params=parameters)
        #log.error("response %s\n",response)
        self.assertTrue('"value": false' in response, response)


        parameters = {"user": "root", "otp1": "359864", "otp2": "348448" }
        response = self.make_admin_request('resync', params=parameters)
        # Test response...
        log.error("response %s\n", response)
        self.assertTrue('"value": true' in response, response)


        self.delete_token("F722364")
        self.delete_token("F722363")
        self.delete_token("F722362")

    def test_resync_sha256(self):
        self.createTokenSHA256(serial="SHA256")

        parameters = {"serial":"SHA256", "otp1":"778729" , "otp2":"094573" }
        response = self.make_admin_request("resync", params=parameters)

        self.assertTrue('"value": true' in response, response)
        self.delete_token("SHA256")


    def test_setPin(self):
        self.createToken3()

        ## test resync of token 2
        parameters = {"serial":"003e808e", "userpin":"123456", "sopin":"123234" }
        response = self.make_admin_request('setPin', params=parameters)
        # log.error("response %s\n",response)
        # Test response...
        self.assertTrue('"set sopin": 1' in response, response)
        self.assertTrue('"set userpin": 1' in response, response)

        self.delete_token("003e808e")


    def test_assign(self):

        serial = self.createToken2(serial="F722362")

        response = self.make_admin_request('show')


        respRealms = self.make_system_request('getRealms', params=None)
        log.debug(respRealms)

        ## test initial assign
        parameters = {"serial":serial, "user": "root" }
        response = self.make_admin_request('assign', params=parameters)
        # log.error("response %s\n",response)
        # Test response...
        self.assertTrue('"value": true' in response, response)

        ## test initial assign update
        parameters = {"serial": serial, "user": "root", "pin":"NewPin" }
        response = self.make_admin_request('assign', params=parameters)
        #log.error("response %s\n",response)
        # Test response...
        self.assertTrue('"value": true' in response, response)

        response = self.make_admin_request('show')
        #log.error("response %s\n",response)
        self.assertTrue('"User.userid": "0", ' in response, response)


        ## test initial assign update
        parameters = {"serial": serial , "user": "root"}
        response = self.make_admin_request('unassign', params=parameters)
        #log.error("response %s\n",response)
        self.assertTrue('"value": true' in response, response)

        ## test wrong assign
        parameters = {"serial": serial, "user": "NoBody" }
        response = self.make_admin_request('assign', params=parameters)
        #log.error("response %s\n",response)
        self.assertTrue('getUserId failed: no user >NoBody< found!' in response, response)

        response = self.make_admin_request('show')
        #log.error("response %s\n",response)
        self.assertTrue('"User.userid": "",' in response, response)



        self.delete_token(serial)

    def test_assign_umlaut(self):
        self.createTokenSHA256(serial="umlauttoken")

        parameters = {"serial": "umlauttoken", "user": "kölbel"}
        response = self.make_admin_request("assign", params=parameters)
        self.assertTrue('"value": true' in response, response)

        self.delete_token("umlauttoken")
        return

    def test_losttoken_email(self):
        """
        test for losttoken callback - to support email tokens as replacement

        test with user hans, who has an email address
        - is the old one deactivated
        - is the new one active
        - is the new one of type 'email'

        remark:
            other losttoken tests depend on policy definition and are
            part of the test_policy.py

        """
        token_name = "verloren"
        self.createTokenSHA256(serial=token_name)

        parameters = {"serial": token_name, "user": "hans"}
        response = self.make_admin_request("assign", params=parameters)
        self.assertTrue('"value": true' in response, response)

        parameters = {"serial": token_name, 'type': "email"}
        response = self.make_admin_request("losttoken", params=parameters)
        self.assertTrue('"status": true' in response, response)

        resp = json.loads(response.body)
        lost_token_name = resp.get('result', {}).get('value', {}).get('serial')

        # first check if old token is not active
        parameters = {"serial": token_name}
        response = self.make_admin_request("show", params=parameters)
        self.assertTrue('"status": true' in response, response)
        resp = json.loads(response.body)
        data = resp.get("result", {}).get('value', {}).get('data', [{}])[0]
        active = data.get("LinOtp.Isactive", True)
        self.assertFalse(active, response)
        user = data.get("User.username", '')
        self.assertEqual(user, 'hans', response)

        # second check if new token is active
        parameters = {"serial": lost_token_name}
        response = self.make_admin_request("show", params=parameters)
        self.assertTrue('"status": true' in response, response)
        resp = json.loads(response.body)
        data = resp.get("result", {}).get('value', {}).get('data', [{}])[0]
        active = data.get("LinOtp.Isactive", False)
        self.assertTrue(active, response)

        user = data.get("User.username", '')
        self.assertEqual(user, 'hans', response)

        ttype = data.get("LinOtp.TokenType", '')
        self.assertEqual(ttype, 'email', response)

        self.delete_token(token_name)
        self.delete_token(lost_token_name)
        return

    def test_losttoken_sms(self):
        """
        test for losttoken callback - to support sms tokens as replacement

        test with user hans, who has a mobile number
        - is the old one deactivated
        - is the new one active
        - is the new one of type 'sms'

        remark:
            other losttoken tests depend on policy definition and are
            part of the test_policy.py

        """
        token_name = "verloren"
        self.createTokenSHA256(serial=token_name)

        parameters = {"serial": token_name, "user": "hans"}
        response = self.make_admin_request("assign", params=parameters)
        self.assertTrue('"value": true' in response, response)

        parameters = {"serial": token_name, 'type': "sms"}
        response = self.make_admin_request("losttoken", params=parameters)
        self.assertTrue('"status": true' in response, response)

        resp = json.loads(response.body)
        lost_token_name = resp.get('result', {}).get('value', {}).get('serial')

        # first check if old token is not active
        parameters = {"serial": token_name}
        response = self.make_admin_request("show", params=parameters)
        self.assertTrue('"status": true' in response, response)
        resp = json.loads(response.body)
        data = resp.get("result", {}).get('value', {}).get('data', [{}])[0]
        active = data.get("LinOtp.Isactive", True)
        self.assertFalse(active, response)
        user = data.get("User.username", '')
        self.assertEqual(user, 'hans', response)

        # second check if new token is active
        parameters = {"serial": lost_token_name}
        response = self.make_admin_request("show", params=parameters)
        self.assertTrue('"status": true' in response, response)
        resp = json.loads(response.body)
        data = resp.get("result", {}).get('value', {}).get('data', [{}])[0]
        active = data.get("LinOtp.Isactive", False)
        self.assertTrue(active, response)

        user = data.get("User.username", '')
        self.assertEqual(user, 'hans', response)

        ttype = data.get("LinOtp.TokenType", '')
        self.assertEqual(ttype, 'sms', response)

        self.delete_token(token_name)
        self.delete_token(lost_token_name)
        return

    def test_losttoken_fail(self):
        """
        test for losttoken callback - which might fail

        test with user horst, who has no mobile number and no email
        - is the old one deactivated
        - is the new one active
        - is the new one of type 'pw'

        remark:
            other losttoken tests depend on policy definition and are
            part of the test_policy.py
        """
        token_name = "verloren"
        user_name = 'horst'

        self.createTokenSHA256(serial=token_name)

        parameters = {"serial": token_name, "user": user_name}
        response = self.make_admin_request("assign", params=parameters)
        self.assertTrue('"value": true' in response, response)

        parameters = {"serial": token_name, 'type': "sms"}
        response = self.make_admin_request("losttoken", params=parameters)
        self.assertTrue('"status": true' in response, response)

        resp = json.loads(response.body)
        lost_token_name = resp.get('result', {}).get('value', {}).get('serial')

        # first check if old token is not active
        parameters = {"serial": token_name}
        response = self.make_admin_request("show", params=parameters)
        self.assertTrue('"status": true' in response, response)
        resp = json.loads(response.body)
        data = resp.get("result", {}).get('value', {}).get('data', [{}])[0]
        active = data.get("LinOtp.Isactive", True)
        self.assertFalse(active, response)
        user = data.get("User.username", '')
        self.assertEqual(user, user_name, response)

        # second check if new token is active
        parameters = {"serial": lost_token_name}
        response = self.make_admin_request("show", params=parameters)
        self.assertTrue('"status": true' in response, response)
        resp = json.loads(response.body)
        data = resp.get("result", {}).get('value', {}).get('data', [{}])[0]
        active = data.get("LinOtp.Isactive", False)
        self.assertTrue(active, response)

        user = data.get("User.username", '')
        self.assertEqual(user, user_name, response)

        ttype = data.get("LinOtp.TokenType", '')
        self.assertEqual(ttype, 'pw', response)

        self.delete_token(token_name)
        self.delete_token(lost_token_name)
        return

    def test_losttoken_spass(self):
        """
        test for losttoken callback - to register replacement for lost spass

        test with user hans, who has a spass
        - is the old one deactivated
        - is the new one active
        - is the new one of type 'pw'
        - does the new password work

        remark:
            other losttoken tests depend on policy definition and are
            part of the test_policy.py

        """
        token_name = "verloren"
        spass_pin  = "initial_pin"

        new_serial = self.createSPASS(serial=token_name, pin=spass_pin)
        self.assertTrue(token_name == new_serial)

        parameters = {"serial": token_name, "user": "hans"}
        response = self.make_admin_request("assign", params=parameters)
        self.assertTrue('"value": true' in response, response)

        # check if this spass validates
        response = self.make_validate_request('check_s',
                                params={'serial': token_name,
                                        'pass': spass_pin})
        self.assertTrue('"value": true' in response, response)

        parameters = {"serial": token_name, 'type': "spass"}
        response = self.make_admin_request("losttoken", params=parameters)
        self.assertTrue('"status": true' in response, response)

        resp = json.loads(response.body)
        temp_token_name = resp.get('result', {}).get('value', {}).get('serial')
        temp_token_pass = resp.get('result', {}).get('value', {}).get('password')

        # first check if old token is not active
        parameters = {"serial": token_name}
        response = self.make_admin_request("show", params=parameters)
        self.assertTrue('"status": true' in response, response)
        resp = json.loads(response.body)
        data = resp.get("result", {}).get('value', {}).get('data', [{}])[0]
        active = data.get("LinOtp.Isactive", True)
        self.assertFalse(active, response)
        user = data.get("User.username", '')
        self.assertEqual(user, 'hans', response)

        # second check if new token is active and properly assigned
        parameters = {"serial": temp_token_name}
        response = self.make_admin_request("show", params=parameters)
        self.assertTrue('"status": true' in response, response)
        resp = json.loads(response.body)
        data = resp.get("result", {}).get('value', {}).get('data', [{}])[0]
        active = data.get("LinOtp.Isactive", False)
        self.assertTrue(active, response)

        user = data.get("User.username", '')
        self.assertEqual(user, 'hans', response)

        ttype = data.get("LinOtp.TokenType", '')
        self.assertEqual(ttype, 'pw', response)

        # finally, check if old spass is blocked and new one works without previous pin
        response = self.make_validate_request('check_s',
                                params={'serial': token_name,
                                        'pass': spass_pin})
        self.assertTrue('"value": false' in response, response)
        response = self.make_validate_request('check_s',
                                params={'serial': temp_token_name,
                                        'pass': temp_token_pass})
        self.assertTrue('"value": true' in response, response)

        # all fine, clean up
        self.delete_token(token_name)
        self.delete_token(temp_token_name)
        return

    def test_enroll_umlaut(self):

        parameters = {
                      "serial" : "umlauttoken",
                      "otpkey" : "47F6EE05C06FA1CDB8B9AADF520FCF86221DB0A107731452AE140EED0EB518B0",
                      "type" : "hmac",
                      "hashlib" : "sha256",
                      "user" : "kölbel"
                      }
        response = self.make_admin_request('init', params=parameters)
        self.assertTrue('"value": true' in response, response)
        self.delete_token("umlauttoken")

    def test_session(self):
        '''
        Testing getting session and dropping session
        '''
        response = self.make_admin_request('getsession',
                                params={})

        self.assertTrue('"value": true' in response, response)

        response = self.make_admin_request('dropsession',
                                params={})

        self.assertTrue('' in response, response)

    def test_check_serial(self):
        '''
        Checking what happens if serial exists
        '''
        response = self.make_admin_request('init',
                                params={"serial" : 'unique_serial_001',
                                        "type" : 'spass'})

        self.assertTrue('"value": true' in response, response)

        response = self.make_admin_request('check_serial',
                                params={'serial' : 'unique_serial_002'})

        self.assertTrue('"unique": true' in response, response)
        self.assertTrue('"new_serial": "unique_serial_002"' in response, response)

        response = self.make_admin_request('check_serial',
                                params={'serial' : 'unique_serial_001'})

        self.assertTrue('"unique": false' in response, response)
        self.assertTrue('"new_serial": "unique_serial_001_01"' in response, response)

    def test_setPin_empty(self):
        '''
        Testing setting empty PIN and SO PIN
        '''
        response = self.make_admin_request('init',
                                params={'serial': 'setpin_01',
                                        'type': 'spass'})

        self.assertTrue('"value": true' in response, response)

        response = self.make_admin_request('setPin',
                                params={'serial': 'setpin_01'})

        self.assertTrue('"status": false' in response, response)
        self.assertTrue('"code": 77' in response, response)

        response = self.make_admin_request('setPin',
                                params={'serial': 'setpin_01',
                                        'sopin' : 'geheim'})


        self.assertTrue('"set sopin": 1' in response, response)

    def test_set_misc(self):
        '''
        Setting CountWindow, timeWindow, timeStep, timeShift
        '''
        response = self.make_admin_request('init',
                                params={'serial': 'token_set_misc',
                                        'type': 'spass'})

        self.assertTrue('"value": true' in response, response)

        response = self.make_admin_request('set',
                                params={'serial': 'token_set_misc',
                                        'CounterWindow': '100',
                                        'timeWindow': '180',
                                        'timeStep': '30',
                                        'timeShift': '0'})


        self.assertTrue('set CounterWindow": 1' in response, response)
        self.assertTrue('"set timeShift": 1' in response, response)
        self.assertTrue('"set timeWindow": 1' in response, response)
        self.assertTrue('"set timeStep": 1' in response, response)

    def test_set_count(self):
        '''
        Setting countAuth, countAuthMax, countAuthSucces countAuthSuccessMax
        '''
        response = self.make_admin_request('init',
                                params={'serial': 'token_set_count',
                                        'type': 'spass'})

        self.assertTrue('"value": true' in response, response)

        response = self.make_admin_request('set',
                                params={'serial': 'token_set_count',
                                        'countAuth': '10',
                                        'countAuthMax': '180',
                                        'countAuthSuccess': '0',
                                        'countAuthSuccessMax': '10'})


        self.assertTrue('"set countAuthSuccess": 1' in response, response)
        self.assertTrue('"set countAuthSuccessMax": 1' in response, response)
        self.assertTrue('"set countAuth": 1' in response, response)
        self.assertTrue('"set countAuthMax": 1' in response, response)

        return

    def test_set_validity(self):
        '''
        Setting validity period
        '''
        response = self.make_admin_request('init',
                                params={'serial': 'token_set_validity',
                                        'type': 'spass'})

        self.assertTrue('"value": true' in response, response)

        response = self.make_admin_request('set',
                                params={'serial': 'token_set_validity',
                                        'validityPeriodStart': '2012-10-12',
                                        'validityPeriodEnd': '2013-12-30',
                                        })


        self.assertTrue('"status": false' in response, response)
        self.assertTrue('does not match format' in response, response)

        response = self.make_admin_request('set',
                                params={'serial': 'token_set_validity',
                                        'validityPeriodStart': '12/12/12 10:00',
                                        'validityPeriodEnd': '30/12/13 13:00',
                                        })


        self.assertTrue('"status": true' in response, response)
        self.assertTrue('"set validityPeriodStart": 1' in response, response)
        self.assertTrue('"set validityPeriodEnd": 1' in response, response)

    def test_set_validity_interface(self):
        '''
        Setting validity period via admin/setValidity interface
        '''

        token_serial_1 = 'token_set_validity1'
        token_serial_2 = 'token_set_validity2'

        response = self.make_admin_request('init',
                                params={'serial': token_serial_1,
                                        'type': 'spass'})

        self.assertTrue('"value": true' in response, response)

        response = self.make_admin_request('init',
                                params={'serial': token_serial_2,
                                        'type': 'spass'})

        self.assertTrue('"value": true' in response, response)

        response = self.make_admin_request('setValidity',
                                params={
                                    'tokens': [
                                        token_serial_1,
                                        token_serial_2
                                        ],
                                     'validityPeriodStart': '2012-10-12',
                                     'validityPeriodEnd': '2013-12-30',
                                     },
                                content_type='application/json')

        self.assertTrue('"status": false' in response, response)
        msg = "invalid literal for int() with base 10: '2012-10-12'"
        self.assertTrue(msg in response, response)

        response = self.make_admin_request(
                                action='setValidity',
                                params={
                                    'tokens': [
                                        token_serial_1,
                                        token_serial_2,
                                        ],
                                        'validityPeriodStart': '1355302800',
                                        'validityPeriodEnd': '1355310000',
                                        },
                                content_type="application/json"
                                )

        self.assertTrue(
            response.json['result']['status'] is True,
            'Expected response.result.status to be True in response text: "{}"'
                .format(response.text))

        self.assertTrue(
            token_serial_1 in response.json['result']['value'],
            'Expected response.result.value to contain token id "{}" in response text: "{}"'
                .format(token_serial_1, response.text))

        self.assertTrue(
            token_serial_2 in response.json['result']['value'],
            'Expected response.result.value to contain token id "{}" in response text: "{}"'
                .format(token_serial_2, response.text))

    def test_set_empty(self):
        '''
        Running set without parameter
        '''
        response = self.make_admin_request('init',
                                params={'serial': 'token_set_empty',
                                        'type': 'spass'})

        self.assertTrue('"value": true' in response, response)

        response = self.make_admin_request('set',
                                params={'serial': 'token_set_empty',
                                        })


        self.assertTrue('"status": false' in response, response)
        self.assertTrue('"code": 77' in response, response)


    def test_copy_token_pin(self):
        '''
        testing copyTokenPin

        We create one token with a PIN and authenticate.
        Then we copy the PIN to another token and try to authenticate.
        '''
        response = self.make_admin_request('init',
                                params={'serial': 'copy_token_1',
                                        'type': 'spass',
                                        'pin': '1234'})

        self.assertTrue('"value": true' in response, response)

        response = self.make_validate_request('check_s',
                                params={'serial': 'copy_token_1',
                                        'pass': '1234'})

        self.assertTrue('"value": true' in response, response)

        response = self.make_admin_request('init',
                                params={'serial': 'copy_token_2',
                                        'type': 'spass',
                                        'pin': 'otherPassword'})

        self.assertTrue('"value": true' in response, response)

        response = self.make_validate_request('check_s',
                                params={'serial': 'copy_token_2',
                                        'pass': 'otherPassword'})

        self.assertTrue('"value": true' in response, response)

        response = self.make_admin_request('copyTokenPin',
                                params={'from': 'copy_token_1',
                                        'to': 'copy_token_2'})

        self.assertTrue('"value": true' in response, response)

        response = self.make_validate_request('check_s',
                                params={'serial': 'copy_token_2',
                                        'pass': '1234'})

        self.assertTrue('"value": true' in response, response)

    def test_copy_token_user(self):
        '''
        testing copyTokenUser
        '''
        response = self.make_admin_request('init',
                                params={'serial': 'copy_user_1',
                                        'type': 'spass',
                                        'pin': 'copyTokenUser',
                                        'user': 'root'})

        self.assertTrue('"value": true' in response, response)

        response = self.make_validate_request('check',
                                params={'user': 'root',
                                        'pass': 'copyTokenUser'})

        self.assertTrue('"value": true' in response, response)

        response = self.make_admin_request('init',
                                params={'serial': 'copy_user_2',
                                        'type': 'spass',
                                        'pin': 'unknownSecret'})

        self.assertTrue('"value": true' in response, response)

        response = self.make_admin_request('copyTokenUser',
                                params={'from': 'copy_user_1',
                                        'to': 'copy_user_2'})

        self.assertTrue('"value": true' in response, response)

        response = self.make_validate_request('check',
                                params={'user': 'root',
                                        'pass': 'unknownSecret'})

        self.assertTrue('"value": true' in response, response)

    def test_enroll_token_twice(self):
        '''
        test to enroll another token with the same serial number
        '''
        response = self.make_admin_request('init',
                                params={'serial' : 'token01',
                                        'type' : 'hmac',
                                        'otpkey' : '123456'})

        self.assertTrue('"value": true' in response, response)

        # enrolling the token of the same type is possible
        response = self.make_admin_request('init',
                                params={'serial' : 'token01',
                                        'type' : 'hmac',
                                        'otpkey' : '567890'})

        self.assertTrue('"value": true' in response, response)

        # enrolling of another type is not possible
        response = self.make_admin_request('init',
                                params={'serial' : 'token01',
                                        'type' : 'spass',
                                        'otpkey' : '123456'})

        self.assertTrue("already exist with type" in response, response)
        self.assertTrue("Can not initialize token with new type" in response, response)

        # clean up
        response = self.make_admin_request('remove',
                                params={'serial' : 'token01'})

        self.assertTrue('"status": true' in response, response)
