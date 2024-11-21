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

from setuptools import setup, find_packages, find_namespace_packages

setup(
    # Name of the package
    name="rag_pipeline",
    
    # Version of the package
    version="0.1.0",
    
    # Automatically find and include all packages in the project
    # This specifically looks for packages within 'opensearch_py_ml' and its subpackages
    packages=find_namespace_packages(include=['opensearch_py_ml', 'opensearch_py_ml.*']),
    
    # Define console script entry points
    # This creates a command-line executable named 'rag' that runs the main() function
    # from the opensearch_py_ml.ml_commons.rag_pipeline.rag module
    entry_points={
        'console_scripts': [
            'rag=opensearch_py_ml.ml_commons.rag_pipeline.rag:main',
        ],
    },
)