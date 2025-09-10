from shared.domain.requests.enums import PublicationType
from .base import PublicationStartedRequest, RequestProcessingStartedRequest, MessageSentRequest, RequestStatusChangedRequest


class PostPublicationStartedRequest(PublicationStartedRequest):
    type: PublicationType = PublicationType.POST


class PostRequestProcessingStartedRequest(RequestProcessingStartedRequest):
    type: PublicationType = PublicationType.POST


class PostMessageSentRequest(MessageSentRequest):
    type: PublicationType = PublicationType.POST


class PostRequestStatusChangedRequest(RequestStatusChangedRequest):
    type: PublicationType = PublicationType.POST
