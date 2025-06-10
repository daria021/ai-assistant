from shared.domain.requests.enums import PublicationType
from .base import PublicationStartedRequest, RequestProcessingStartedRequest, MessageSentRequest


class StoryPublicationStartedRequest(PublicationStartedRequest):
    type: PublicationType = PublicationType.STORY


class StoryRequestProcessingStartedRequest(RequestProcessingStartedRequest):
    type: PublicationType = PublicationType.STORY


class StoryMessageSentRequest(MessageSentRequest):
    type: PublicationType = PublicationType.STORY
