\
    import os
    from .generic import GenericParser as _Gen

    class AiParser(_Gen):
        @staticmethod
        def can_parse(filename: str, raw: bytes) -> bool:
            return "ai" in os.path.basename(filename).lower()

        def parse(self, filepath: str):
            raw = self.read_file(filepath)
            # start with generic parse then add guesses
            base = super().parse(filepath)
            structured = base["structured"]
            # guessed fields depending on token
            s = structured
            # heuristics: infer GUIDs and strings already done by generic; add guessed names
            if "strings" in s and s["strings"]:
                # example guess: first string could be a resource name
                s["guessed_resource_name"] = s["strings"][0]
            # token-specific guesses
            if "ai" == "inv_name_part":
                # often contains item part names and guids
                s["guessed_type"] = "inventory_name_part"
            if "ai" == "achievement":
                s["guessed_type"] = "achievement_data"
            if "ai" == "loot_config":
                s["guessed_type"] = "loot_configuration"
            # add small metadata
            s.setdefault("metadata", {})
            s["metadata"]["inferred_by"] = "AiParser"
            return { "structured": s, "raw_bytes": base["raw_bytes"] }

        def to_bytes(self, data: dict) -> bytes:
            # prefer original raw_bytes preserved
            if "raw_bytes" in data:
                return data["raw_bytes"]
            return super().to_bytes(data)
