class MemoryAliasRegistry:

    def __init__(self):

        self._aliases = {
            "favorite_color": {
                "favorite color",
                "favourite color",
                "preferred color",
                "preferred colour",
                "color i like",
                "colour i like",
            },
            "favorite_food": {
                "favorite food",
                "favourite food",
                "preferred food",
                "food i like",
            },
            "name": {
                "my name",
                "what is my name",
                "whats my name",
            },
        }

    def get_aliases(
        self,
        key: str,
    ) -> set[str]:

        return self._aliases.get(
            key,
            set(),
        )

    def add_alias(
        self,
        key: str,
        alias: str,
    ) -> None:

        alias = alias.strip().lower()

        if not alias:
            return

        if key not in self._aliases:
            self._aliases[key] = set()

        self._aliases[key].add(alias)

    def remove_alias(
        self,
        key: str,
        alias: str,
    ) -> None:

        aliases = self._aliases.get(key)

        if aliases is None:
            return

        aliases.discard(
            alias.strip().lower()
        )

    def has_alias(
        self,
        key: str,
        alias: str,
    ) -> bool:

        return (
            alias.strip().lower()
            in self._aliases.get(
                key,
                set(),
            )
        )

    def keys(self) -> list[str]:

        return list(
            self._aliases.keys()
        )