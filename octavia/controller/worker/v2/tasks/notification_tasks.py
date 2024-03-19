# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#

from oslo_log import log as logging
from taskflow import task

from octavia.common import constants # noqa H306
from octavia.common import context
from octavia.common import rpc

LOG = logging.getLogger(__name__)


class BaseNotificationTask(task.Task):
    event_type = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._rpc_notifier = rpc.get_notifier()

    def execute(self, loadbalancer):
        ctx = context.RequestContext(
            project_id=loadbalancer[constants.PROJECT_ID])
        LOG.debug(f"Sending rpc notification: {self.event_type} "
                  f"{loadbalancer[constants.LOADBALANCER_ID]}")
        self._rpc_notifier.info(
            ctx,
            self.event_type,
            loadbalancer
        )
  
class ListenerNotificationTask(task.Task):
    event_type = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._rpc_notifier = rpc.get_notifier()

    def execute(self, listener):
        ctx = context.RequestContext(
            # loadbalancer_id=listener[constants.LOADBALANCER_ID],
            project_id = listener[constants.PROJECT_ID])
        LOG.debug(f"Sending rpc notification: {self.event_type} "
                  f"{listener[constants.LISTENER_ID]}")
        self._rpc_notifier.info(
            ctx,
            self.event_type,
            listener
        )
class PoolNotificationTask(task.Task):
    event_type = None
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._rpc_notifier = rpc.get_notifier()

    def execute(self, pool_id):
        ctx = context.RequestContext()
            # loadbalancer_id=listener[constants.LOADBALANCER_ID],
            # project_id = pool_id[constants.PROJECT_ID])
        # LOG.debug(f"Sending rpc notification: {self.event_type} "
        #           f"{pool_id[constants.POOL_ID]}")
        self._rpc_notifier.info(
            ctx,
            self.event_type,
            pool_id
        )
        
class MemberNotificationTask(task.Task):
    event_type = None
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._rpc_notifier = rpc.get_notifier()

    def execute(self, member):
        ctx = context.RequestContext(
            # loadbalancer_id=listener[constants.LOADBALANCER_ID],
            project_id = member[constants.PROJECT_ID])
        LOG.debug(f"Sending rpc notification: {self.event_type} "
                  f"{member[constants.MEMBER_ID]}")
        self._rpc_notifier.info(
            ctx,
            self.event_type,
            member
        )

class HealthMonitorNotificationTask(task.Task):
    event_type = None
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._rpc_notifier = rpc.get_notifier()

    def execute(self, health_mon):
        ctx = context.RequestContext(
            # loadbalancer_id=listener[constants.LOADBALANCER_ID],
            project_id = health_mon[constants.PROJECT_ID])
        LOG.debug(f"Sending rpc notification: {self.event_type} "
                  f"{health_mon[constants.HEALTHMONITOR_ID]}")
        self._rpc_notifier.info(
            ctx,
            self.event_type,
            health_mon
        )                
class SendUpdateNotification(BaseNotificationTask):
    event_type = 'octavia.loadbalancer.update.end'


class SendCreateNotification(BaseNotificationTask):
    event_type = 'octavia.loadbalancer.create.end'


class SendDeleteNotification(BaseNotificationTask):
    event_type = 'octavia.loadbalancer.delete.end'


class SendCreateListenerNotification(BaseNotificationTask):
    event_type  = 'octavia.listener.create.end'
class SendUpdateListenerNotification(ListenerNotificationTask):
    event_type  = 'octavia.listener.update.end'
class SendDeleteListenerNotification(ListenerNotificationTask):
    event_type  = 'octavia.listener.delete.end'


class SendCreatePoolNotification(BaseNotificationTask):
    event_type  = 'octavia.pool.create.end'
class SendUpdatePoolNotification(PoolNotificationTask):
    event_type  = 'octavia.pool.update.end'
class SendDeletePoolNotification(PoolNotificationTask):
    event_type  = 'octavia.pool.delete.end'


class SendCreateMemberNotification(BaseNotificationTask):
    event_type  = 'octavia.member.create.end'
class SendUpdateMemberNotification(MemberNotificationTask):
    event_type  = 'octavia.member.update.end'
class SendDeleteMemberNotification(MemberNotificationTask):
    event_type  = 'octavia.member.delete.end'


class SendHeathMonitorNotification(BaseNotificationTask):
    event_type  = 'octavia.health-monitor.create.end'
class SendHeathMonitorUpdateNotification(HealthMonitorNotificationTask):
    event_type  = 'octavia.health-monitor.update.end'
class SendHeathMonitorDeleteNotification(HealthMonitorNotificationTask):
    event_type  = 'octavia.health-monitor.delete.end'
# class SendCreateListenerNotification(BaseNotificationTask):
    # event_type  = 'octavia.listener.create.end'
