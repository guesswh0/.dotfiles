from types import SimpleNamespace


class ClaudeAgentOptions(SimpleNamespace):
    pass


class HookMatcher(SimpleNamespace):
    pass


class PermissionResultAllow(SimpleNamespace):
    behavior = "allow"


class PermissionResultDeny(SimpleNamespace):
    behavior = "deny"


class ResultMessage(SimpleNamespace):
    def __init__(self, **fields):
        super().__init__(
            **{
                "is_error": False,
                "subtype": "success",
                "model_usage": {"claude-test": {}},
                "permission_denials": [],
                "errors": [],
                **fields,
            }
        )


class TaskStartedMessage(SimpleNamespace):
    pass


class TaskNotificationMessage(SimpleNamespace):
    pass


class TaskProgressMessage(SimpleNamespace):
    pass
