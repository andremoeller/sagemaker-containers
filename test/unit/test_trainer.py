# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License'). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the 'license' file accompanying this file. This file is
# distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import errno
import os

from mock import Mock, patch

from sagemaker_containers import errors, trainer


class TrainingEnv(Mock):
    framework_module = 'my_framework:entry_point'

    def write_success_file(self):
        pass

    def write_failure_file(self, failure_msg):
        pass


@patch('importlib.import_module')
@patch('sagemaker_containers.env.training_env', TrainingEnv)
def test_train(import_module):
    framework = Mock()
    import_module.return_value = framework
    trainer.train()

    import_module.assert_called_with('my_framework')
    framework.entry_point.assert_called()


@patch('importlib.import_module')
@patch('sagemaker_containers.env.training_env', TrainingEnv)
@patch('sagemaker_containers.trainer._exit_processes')
def test_train_with_success(_exit, import_module):
    def success():
        pass

    framework = Mock(entry_point=success)
    import_module.return_value = framework

    trainer.train()

    _exit.assert_called_with(trainer.SUCCESS_CODE)


@patch('importlib.import_module')
@patch('sagemaker_containers.env.training_env', TrainingEnv)
@patch('sagemaker_containers.trainer._exit_processes')
def test_train_fails(_exit, import_module):

    def fail():
        raise OSError(os.errno.ENOENT, 'No such file or directory')

    framework = Mock(entry_point=fail)
    import_module.return_value = framework

    trainer.train()

    _exit.assert_called_with(errno.ENOENT)


@patch('importlib.import_module')
@patch('sagemaker_containers.env.training_env', TrainingEnv)
@patch('sagemaker_containers.trainer._exit_processes')
def test_train_with_client_error(_exit, import_module):

    def fail():
        raise errors.ClientError(os.errno.ENOENT, 'No such file or directory')

    framework = Mock(entry_point=fail)
    import_module.return_value = framework

    trainer.train()

    _exit.assert_called_with(trainer.DEFAULT_FAILURE_CODE)