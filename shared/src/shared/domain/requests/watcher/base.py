from uuid import UUID

from pydantic import BaseModel

from shared.domain.requests.enums import PublicationType


class PublicationStartedRequest(BaseModel):
    type: PublicationType
    publication_id: UUID
    child_requests: list[UUID] = []


class RequestProcessingStartedRequest(BaseModel):
    type: PublicationType
    request_id: UUID
    child_messages: list[UUID] = []


class MessageSentRequest(BaseModel):
    type: PublicationType
    message_id: UUID
