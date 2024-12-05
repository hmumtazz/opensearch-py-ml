# SPDX-License-Identifier: Apache-2.0
# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.
# Any modifications Copyright OpenSearch Contributors. See
# GitHub history for details.

#  Licensed to Elasticsearch B.V. under one or more contributor
#  license agreements. See the NOTICE file distributed with
#  this work for additional information regarding copyright
#  ownership. Elasticsearch B.V. licenses this file to you under
#  the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the License is distributed on an
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the
#  specific language governing permissions and limitations
#  under the License.

import unittest
from unittest.mock import Mock, patch, call
import json
from io import StringIO
from opensearch_py_ml.ml_commons.rag_pipeline.rag.ml_models.CohereModel import CohereModel

class TestCohereModel(unittest.TestCase):

    def setUp(self):
        self.aws_region = "us-west-2"
        self.opensearch_domain_name = "test-domain"
        self.opensearch_username = "test-user"
        self.opensearch_password = "test-password"
        self.mock_iam_role_helper = Mock()
        self.cohere_model = CohereModel(
            self.aws_region,
            self.opensearch_domain_name,
            self.opensearch_username,
            self.opensearch_password,
            self.mock_iam_role_helper
        )

    def test_init(self):
        self.assertEqual(self.cohere_model.aws_region, self.aws_region)
        self.assertEqual(self.cohere_model.opensearch_domain_name, self.opensearch_domain_name)
        self.assertEqual(self.cohere_model.opensearch_username, self.opensearch_username)
        self.assertEqual(self.cohere_model.opensearch_password, self.opensearch_password)
        self.assertEqual(self.cohere_model.iam_role_helper, self.mock_iam_role_helper)

    @patch('builtins.input', side_effect=['test-secret', 'test-api-key', '1'])
    def test_register_cohere_model(self, mock_input):
        mock_helper = Mock()
        mock_helper.create_connector_with_secret.return_value = "test-connector-id"
        mock_helper.create_model.return_value = "test-model-id"
        
        mock_config = {}
        mock_save_config = Mock()

        self.cohere_model.register_cohere_model(mock_helper, mock_config, mock_save_config)

        mock_helper.create_connector_with_secret.assert_called_once()
        mock_helper.create_model.assert_called_once()
        mock_save_config.assert_called_once_with({'embedding_model_id': 'test-model-id'})

    @patch('builtins.input', side_effect=['test-api-key', '1'])
    @patch('time.time', return_value=1000000)
    def test_register_cohere_model_opensource(self, mock_time, mock_input):
        mock_opensearch_client = Mock()
        mock_opensearch_client.transport.perform_request.side_effect = [
            {'connector_id': 'test-connector-id'},
            {'model_group_id': 'test-model-group-id'},
            {'task_id': 'test-task-id'},
            {'state': 'COMPLETED', 'model_id': 'test-model-id'},
            {}  # for model deployment
        ]
        
        mock_config = {}
        mock_save_config = Mock()

        self.cohere_model.register_cohere_model_opensource(mock_opensearch_client, mock_config, mock_save_config)

        self.assertEqual(mock_opensearch_client.transport.perform_request.call_count, 5)
        mock_save_config.assert_called_once_with({'embedding_model_id': 'test-model-id'})

    def test_get_custom_model_details_default(self):
        with patch('builtins.input', return_value='1'):
            default_input = {"name": "Default Model"}
            result = self.cohere_model.get_custom_model_details(default_input)
            self.assertEqual(result, default_input)

    def test_get_custom_model_details_custom(self):
        with patch('builtins.input', side_effect=['2', '{"name": "Custom Model"}']):
            default_input = {"name": "Default Model"}
            result = self.cohere_model.get_custom_model_details(default_input)
            self.assertEqual(result, {"name": "Custom Model"})

    def test_get_custom_model_details_invalid_json(self):
        with patch('builtins.input', side_effect=['2', 'invalid json']):
            default_input = {"name": "Default Model"}
            result = self.cohere_model.get_custom_model_details(default_input)
            self.assertIsNone(result)

    def test_get_custom_model_details_invalid_choice(self):
        with patch('builtins.input', return_value='3'):
            default_input = {"name": "Default Model"}
            result = self.cohere_model.get_custom_model_details(default_input)
            self.assertIsNone(result)

    def test_get_custom_json_input_valid(self):
        with patch('builtins.input', return_value='{"key": "value"}'):
            result = self.cohere_model.get_custom_json_input()
            self.assertEqual(result, {"key": "value"})

    def test_get_custom_json_input_invalid(self):
        with patch('builtins.input', return_value='invalid json'):
            result = self.cohere_model.get_custom_json_input()
            self.assertIsNone(result)

    @patch('time.time', side_effect=[0, 10, 20, 30])
    @patch('time.sleep', return_value=None)
    def test_wait_for_model_registration_success(self, mock_sleep, mock_time):
        mock_opensearch_client = Mock()
        mock_opensearch_client.transport.perform_request.side_effect = [
            {'state': 'RUNNING'},
            {'state': 'RUNNING'},
            {'state': 'COMPLETED', 'model_id': 'test-model-id'}
        ]
        
        result = self.cohere_model.wait_for_model_registration(mock_opensearch_client, 'test-task-id')
        self.assertEqual(result, 'test-model-id')

    @patch('time.time', side_effect=[0, 10, 20, 30])
    @patch('time.sleep', return_value=None)
    def test_wait_for_model_registration_failure(self, mock_sleep, mock_time):
        mock_opensearch_client = Mock()
        mock_opensearch_client.transport.perform_request.side_effect = [
            {'state': 'RUNNING'},
            {'state': 'FAILED'}
        ]
        
        result = self.cohere_model.wait_for_model_registration(mock_opensearch_client, 'test-task-id')
        self.assertIsNone(result)

    @patch('time.time', side_effect=[0, 1000])
    @patch('time.sleep', return_value=None)
    def test_wait_for_model_registration_timeout(self, mock_sleep, mock_time):
        mock_opensearch_client = Mock()
        mock_opensearch_client.transport.perform_request.return_value = {'state': 'RUNNING'}
        
        result = self.cohere_model.wait_for_model_registration(mock_opensearch_client, 'test-task-id', timeout=5)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()