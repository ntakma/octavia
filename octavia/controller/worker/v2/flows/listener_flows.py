# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
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
from oslo_config import cfg

from taskflow.patterns import linear_flow

from octavia.common import constants
from octavia.controller.worker.v2.tasks import amphora_driver_tasks
from octavia.controller.worker.v2.tasks import database_tasks
from octavia.controller.worker.v2.tasks import lifecycle_tasks
from octavia.controller.worker.v2.tasks import network_tasks
from octavia.controller.worker.v2.tasks import notification_tasks

CONF = cfg.CONF
class ListenerFlows(object):

    def get_create_listener_flow(self):
        """Create a flow to create a listener

        :returns: The flow for creating a listener
        """
        create_listener_flow = linear_flow.Flow(constants.CREATE_LISTENER_FLOW)
        create_listener_flow.add(lifecycle_tasks.ListenersToErrorOnRevertTask(
            requires=constants.LISTENERS))
        create_listener_flow.add(amphora_driver_tasks.ListenersUpdate(
            requires=constants.LOADBALANCER_ID))
        create_listener_flow.add(network_tasks.UpdateVIP(
            requires=constants.LISTENERS))
        create_listener_flow.add(database_tasks.
                                 MarkLBAndListenersActiveInDB(
                                     requires=(constants.LOADBALANCER_ID,
                                               constants.LISTENERS)))
        if CONF.controller_worker.event_notifications:
            create_listener_flow.add(
                notification_tasks.SendCreateListenerNotification(
                    requires=constants.LOADBALANCER
                )
            )
        return create_listener_flow

    def get_create_all_listeners_flow(self):
        """Create a flow to create all listeners

        :returns: The flow for creating all listeners
        """
        create_all_listeners_flow = linear_flow.Flow(
            constants.CREATE_LISTENERS_FLOW)
        create_all_listeners_flow.add(
            database_tasks.GetListenersFromLoadbalancer(
                requires=constants.LOADBALANCER,
                provides=constants.LISTENERS))
        create_all_listeners_flow.add(database_tasks.ReloadLoadBalancer(
            requires=constants.LOADBALANCER_ID,
            provides=constants.LOADBALANCER))
        create_all_listeners_flow.add(amphora_driver_tasks.ListenersUpdate(
            requires=constants.LOADBALANCER_ID))
        create_all_listeners_flow.add(network_tasks.UpdateVIP(
            requires=constants.LISTENERS))
        create_all_listeners_flow.add(
            database_tasks.MarkHealthMonitorsOnlineInDB(
                requires=constants.LOADBALANCER))
        if CONF.controller_worker.event_notifications:
            create_all_listeners_flow.add(
                notification_tasks.SendCreateListenerNotification(
                    requires=constants.LOADBALANCER,
                )
            )
        return create_all_listeners_flow

    def get_delete_listener_flow(self):
        """Create a flow to delete a listener

        :returns: The flow for deleting a listener
        """
        delete_listener_flow = linear_flow.Flow(constants.DELETE_LISTENER_FLOW)
        delete_listener_flow.add(lifecycle_tasks.ListenerToErrorOnRevertTask(
            requires=constants.LISTENER))
        delete_listener_flow.add(amphora_driver_tasks.ListenerDelete(
            requires=constants.LISTENER))
        delete_listener_flow.add(network_tasks.UpdateVIPForDelete(
            requires=constants.LOADBALANCER_ID))
        delete_listener_flow.add(database_tasks.DeleteListenerInDB(
            requires=constants.LISTENER))
        delete_listener_flow.add(database_tasks.DecrementListenerQuota(
            requires=constants.PROJECT_ID))
        delete_listener_flow.add(database_tasks.MarkLBActiveInDBByListener(
            requires=constants.LISTENER))
        if CONF.controller_worker.event_notifications:
            delete_listener_flow.add(
                notification_tasks.SendDeleteListenerNotification(
                    requires=(constants.LISTENER)
                )
            )
        return delete_listener_flow

    def get_delete_listener_internal_flow(self, listener):
        """Create a flow to delete a listener and l7policies internally

           (will skip deletion on the amp and marking LB active)

        :returns: The flow for deleting a listener
        """
        listener_id = listener[constants.LISTENER_ID]
        delete_listener_flow = linear_flow.Flow(
            constants.DELETE_LISTENER_FLOW + '-' + listener_id)
        # Should cascade delete all L7 policies
        delete_listener_flow.add(network_tasks.UpdateVIPForDelete(
            name='delete_update_vip_' + listener_id,
            requires=constants.LOADBALANCER_ID))
        delete_listener_flow.add(database_tasks.DeleteListenerInDB(
            name='delete_listener_in_db_' + listener_id,
            requires=constants.LISTENER,
            inject={constants.LISTENER: listener}))
        delete_listener_flow.add(database_tasks.DecrementListenerQuota(
            name='decrement_listener_quota_' + listener_id,
            requires=constants.PROJECT_ID))

        return delete_listener_flow

    def get_update_listener_flow(self):
        """Create a flow to update a listener

        :returns: The flow for updating a listener
        """
        update_listener_flow = linear_flow.Flow(constants.UPDATE_LISTENER_FLOW)
        update_listener_flow.add(lifecycle_tasks.ListenerToErrorOnRevertTask(
            requires=constants.LISTENER))
        update_listener_flow.add(amphora_driver_tasks.ListenersUpdate(
            requires=constants.LOADBALANCER_ID))
        update_listener_flow.add(network_tasks.UpdateVIP(
            requires=constants.LISTENERS))
        update_listener_flow.add(database_tasks.UpdateListenerInDB(
            requires=[constants.LISTENER, constants.UPDATE_DICT]))
        update_listener_flow.add(database_tasks.
                                 MarkLBAndListenersActiveInDB(
                                     requires=(constants.LOADBALANCER_ID,
                                               constants.LISTENERS)))
        if CONF.controller_worker.event_notifications:
            update_listener_flow.add(
                notification_tasks.SendUpdateListenerNotification(
                    requires=(constants.LISTENER)
                )
            )
        return update_listener_flow
