from uuid import UUID

from shared.domain.models.abstract import Model


class UpdatePost(Model):
    post_id: UUID
    post_json: dict
    author_id: UUID
