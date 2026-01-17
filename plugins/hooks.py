"""
Hook system for Bitsy plugins.

Allows plugins to extend behavior at specific points.
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class HookCallback:
    """A registered hook callback."""
    callback: Callable
    priority: int = 0
    name: str = ""


# Available hooks
HOOK_NAMES = [
    # Generation hooks
    "pre_generate",      # Before sprite generation
    "post_generate",     # After sprite generation

    # Rendering hooks
    "pre_render",        # Before canvas rendering
    "post_render",       # After canvas rendering

    # Export hooks
    "pre_export",        # Before file export
    "post_export",       # After file export

    # Animation hooks
    "pre_animate",       # Before animation frame
    "post_animate",      # After animation frame

    # Effect hooks
    "pre_effect",        # Before effect application
    "post_effect",       # After effect application

    # Sound hooks
    "pre_sound",         # Before sound generation
    "post_sound",        # After sound generation
]


class HookRegistry:
    """Registry for hook callbacks.

    Hooks allow plugins to extend behavior at specific points
    in the generation/rendering pipeline.

    Example:
        hooks = HookRegistry()

        # Register a callback
        def my_post_generate(canvas, **kwargs):
            # Modify canvas after generation
            return add_border(canvas)

        hooks.register("post_generate", my_post_generate)

        # Run hooks
        result = hooks.run("post_generate", canvas, generator="character")
    """

    def __init__(self):
        """Initialize hook registry."""
        self._hooks: Dict[str, List[HookCallback]] = {
            name: [] for name in HOOK_NAMES
        }

    def register(
        self,
        hook_name: str,
        callback: Callable,
        priority: int = 0,
        name: str = ""
    ) -> bool:
        """Register a hook callback.

        Args:
            hook_name: Name of the hook
            callback: Function to call
            priority: Higher runs first (default 0)
            name: Optional name for the callback

        Returns:
            True if registered successfully
        """
        if hook_name not in self._hooks:
            raise ValueError(f"Unknown hook: {hook_name}")

        hook = HookCallback(
            callback=callback,
            priority=priority,
            name=name or callback.__name__
        )

        self._hooks[hook_name].append(hook)

        # Sort by priority (descending)
        self._hooks[hook_name].sort(key=lambda h: -h.priority)

        return True

    def unregister(
        self,
        hook_name: str,
        callback: Optional[Callable] = None,
        name: Optional[str] = None
    ) -> bool:
        """Unregister a hook callback.

        Args:
            hook_name: Name of the hook
            callback: Callback to remove (optional)
            name: Name of callback to remove (optional)

        Returns:
            True if unregistered successfully
        """
        if hook_name not in self._hooks:
            return False

        if callback is None and name is None:
            return False

        original_len = len(self._hooks[hook_name])

        self._hooks[hook_name] = [
            h for h in self._hooks[hook_name]
            if not (
                (callback and h.callback == callback) or
                (name and h.name == name)
            )
        ]

        return len(self._hooks[hook_name]) < original_len

    def run(
        self,
        hook_name: str,
        data: Any = None,
        **kwargs
    ) -> Any:
        """Run all callbacks for a hook.

        Callbacks are called in priority order. Each callback
        receives the result of the previous callback (or the
        initial data).

        Args:
            hook_name: Name of the hook
            data: Initial data to pass to callbacks
            **kwargs: Additional keyword arguments

        Returns:
            Result after all callbacks have run
        """
        if hook_name not in self._hooks:
            return data

        result = data

        for hook in self._hooks[hook_name]:
            try:
                callback_result = hook.callback(result, **kwargs)
                # Only update result if callback returns something
                if callback_result is not None:
                    result = callback_result
            except Exception as e:
                # Log but don't crash on hook errors
                import warnings
                warnings.warn(
                    f"Hook callback {hook.name} failed: {e}",
                    RuntimeWarning
                )

        return result

    def run_all(
        self,
        hook_name: str,
        data: Any = None,
        **kwargs
    ) -> List[Any]:
        """Run all callbacks and collect results.

        Unlike run(), this collects all callback results
        instead of chaining them.

        Args:
            hook_name: Name of the hook
            data: Data to pass to all callbacks
            **kwargs: Additional keyword arguments

        Returns:
            List of results from all callbacks
        """
        if hook_name not in self._hooks:
            return []

        results = []

        for hook in self._hooks[hook_name]:
            try:
                result = hook.callback(data, **kwargs)
                results.append(result)
            except Exception as e:
                import warnings
                warnings.warn(
                    f"Hook callback {hook.name} failed: {e}",
                    RuntimeWarning
                )
                results.append(None)

        return results

    def has_hooks(self, hook_name: str) -> bool:
        """Check if hook has any registered callbacks."""
        return bool(self._hooks.get(hook_name))

    def list_hooks(self) -> List[str]:
        """List all available hook names."""
        return list(self._hooks.keys())

    def list_callbacks(self, hook_name: str) -> List[str]:
        """List callback names for a hook."""
        if hook_name not in self._hooks:
            return []
        return [h.name for h in self._hooks[hook_name]]

    def clear(self, hook_name: Optional[str] = None) -> None:
        """Clear hook callbacks.

        Args:
            hook_name: Hook to clear (None clears all)
        """
        if hook_name:
            if hook_name in self._hooks:
                self._hooks[hook_name].clear()
        else:
            for name in self._hooks:
                self._hooks[name].clear()


# Global hook registry
_global_hooks = HookRegistry()


def get_hooks() -> HookRegistry:
    """Get the global hook registry."""
    return _global_hooks


def register_hook(
    hook_name: str,
    callback: Callable,
    priority: int = 0,
    name: str = ""
) -> bool:
    """Register a hook callback in the global registry."""
    return _global_hooks.register(hook_name, callback, priority, name)


def unregister_hook(
    hook_name: str,
    callback: Optional[Callable] = None,
    name: Optional[str] = None
) -> bool:
    """Unregister a hook callback from the global registry."""
    return _global_hooks.unregister(hook_name, callback, name)


def run_hooks(hook_name: str, data: Any = None, **kwargs) -> Any:
    """Run hooks in the global registry."""
    return _global_hooks.run(hook_name, data, **kwargs)


def list_hook_names() -> List[str]:
    """List available hook names."""
    return HOOK_NAMES.copy()
