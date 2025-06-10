import os
from typing import Any, Dict, Type, Tuple
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    JsonConfigSettingsSource,
)

class MergedSettingsSource(PydanticBaseSettingsSource):
    """
    A custom settings source that deep merges several sources.
    It processes both flat keys and nested dictionaries for nested fields.
    After merging, it converts nested dict keys to their alias names,
    re-validates the nested model, and then dumps it with aliases.
    """

    def __init__(
        self,
        settings_cls: Type[BaseSettings],
        init_source: PydanticBaseSettingsSource,
        env_source: PydanticBaseSettingsSource,
        dotenv_source: PydanticBaseSettingsSource,
        file_secret_source: PydanticBaseSettingsSource,
    ) -> None:
        super().__init__(settings_cls)
        self.init_source = init_source
        self.env_source = env_source
        self.dotenv_source = dotenv_source
        self.file_secret_source = file_secret_source
        self._merged: Dict[str, Any] | None = None

    def __call__(self) -> Dict[str, Any]:
        env = os.environ.copy()
        sources = [
            JsonConfigSettingsSource(self.settings_cls)(),
            self.init_source(),
            self.dotenv_source(),
            self.file_secret_source(),
            env,
        ]
        merged: Dict[str, Any] = {}
        for source in sources:
            processed = self.nest_flat_keys(source.copy(), self.settings_cls)
            merged = self.deep_merge(merged, processed)

        merged = self.normalize_nested_fields(merged, self.settings_cls)

        self._merged = merged
        return merged

    def get_field_value(self, field: Any, field_name: str) -> Tuple[Any, str, bool]:
        merged = self()
        if field_name in merged:
            return merged[field_name], field_name, True

        return None, field_name, False

    @classmethod
    def deep_merge(cls, a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        result = a.copy()
        for key, value in b.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = cls.deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    @classmethod
    def nest_flat_keys(cls, data: Dict[str, Any], settings_cls: Type[BaseSettings]) -> Dict[str, Any]:
        for field_name, field in settings_cls.model_fields.items():
            field_type = field.annotation

            if isinstance(field_type, type) and issubclass(field_type, BaseSettings):
                nested_from_flat: Dict[str, Any] = {}
                for subfield_name, subfield in field_type.model_fields.items():
                    alias = subfield.alias or subfield_name
                    if alias in data:
                        nested_from_flat[subfield_name] = data[alias]

                nested_existing: Dict[str, Any] = {}
                if field_name in data and isinstance(data[field_name], dict):
                    nested_existing = data.pop(field_name)

                if nested_from_flat or nested_existing:
                    combined = cls.deep_merge(nested_existing, nested_from_flat)
                    data[field_name] = combined

        return data

    @classmethod
    def convert_to_alias(cls, nested: Dict[str, Any], nested_cls: Type[BaseSettings]) -> Dict[str, Any]:
        """
        Convert keys from field names to alias names for a nested model.
        Only include keys defined by the model.
        """
        alias_dict: Dict[str, Any] = {}
        for field_name, field in nested_cls.model_fields.items():
            alias = field.alias or field_name
            if field_name in nested:
                alias_dict[alias] = nested[field_name]

        return alias_dict

    @classmethod
    def normalize_nested_fields(cls, data: Dict[str, Any], settings_cls: Type[BaseSettings]) -> Dict[str, Any]:
        for field_name, field in settings_cls.model_fields.items():
            field_type = field.annotation
            if isinstance(field_type, type) and issubclass(field_type, BaseSettings):
                if field_name in data and isinstance(data[field_name], dict):
                    # Convert the keys to alias names first.
                    alias_data = cls.convert_to_alias(data[field_name], field_type)
                    # Now, construct the nested model.
                    nested_model = field_type.model_validate(alias_data)
                    # Dump it with aliases.
                    data[field_name] = nested_model.model_dump(by_alias=True)

        return data
