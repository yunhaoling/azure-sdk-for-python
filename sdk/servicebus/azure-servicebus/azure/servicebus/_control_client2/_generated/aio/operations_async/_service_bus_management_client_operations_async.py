# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------
from typing import Any, Callable, Dict, Generic, Optional, TypeVar
import warnings

from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError, map_error
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import AsyncHttpResponse, HttpRequest

from ... import models

T = TypeVar('T')
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, Dict[str, Any]], Any]]

class ServiceBusManagementClientOperationsMixin:

    async def list_entities(
        self,
        queue_or_topic_name: str,
        skip: Optional[int] = 0,
        top: Optional[int] = 100,
        api_version: Optional[str] = "2017_04",
        **kwargs
    ) -> object:
        """Get the details about the entities of the given Service Bus namespace.

        Get Queues or topics.

        :param queue_or_topic_name: The name of the queue or topic relative to the Service Bus
         namespace.
        :type queue_or_topic_name: str
        :param skip:
        :type skip: int
        :param top:
        :type top: int
        :param api_version: Api Version.
        :type api_version: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: object, or the result of cls(response)
        :rtype: object
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType[object]
        error_map = {404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop('error_map', {}))

        # Construct URL
        url = self.list_entities.metadata['url']  # type: ignore
        path_format_arguments = {
            'endpoint': self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
            'queueOrTopicName': self._serialize.url("queue_or_topic_name", queue_or_topic_name, 'str', min_length=1),
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        if skip is not None:
            query_parameters['$skip'] = self._serialize.query("skip", skip, 'int')
        if top is not None:
            query_parameters['$top'] = self._serialize.query("top", top, 'int')
        if api_version is not None:
            query_parameters['api-version'] = self._serialize.query("api_version", api_version, 'str')

        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        header_parameters['Accept'] = 'application/xml'

        # Construct and send request
        request = self._client.get(url, query_parameters, header_parameters)
        pipeline_response = await self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize(models.ServiceBusManagementError, response)
            raise HttpResponseError(response=response, model=error)

        deserialized = self._deserialize('object', pipeline_response)

        if cls:
            return cls(pipeline_response, deserialized, {})

        return deserialized
    list_entities.metadata = {'url': '/$Resources/{entityType}'}  # type: ignore
