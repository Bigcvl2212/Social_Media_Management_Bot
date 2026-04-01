"""
Automation Rules Engine
Event-driven rules that fire based on triggers from posts, comments, leads, and ads.
"""

import asyncio
from typing import Dict, Any, Optional, List, Callable, Awaitable
from datetime import datetime, timezone
from enum import Enum

import logging
logger = logging.getLogger(__name__)


class TriggerType(str, Enum):
    NEW_LEAD = "new_lead"
    NEW_COMMENT = "new_comment"
    POST_ENGAGEMENT_HIGH = "post_engagement_high"
    AD_COST_PER_LEAD_HIGH = "ad_cost_per_lead_high"
    SCHEDULED_POST_FAILED = "scheduled_post_failed"
    MESSENGER_NEW = "messenger_new"


class ActionType(str, Enum):
    NOTIFY_OWNER = "notify_owner"
    PUSH_TO_GYMBOT = "push_to_gymbot"
    REPLY_TO_COMMENT = "reply_to_comment"
    PAUSE_AD_SET = "pause_ad_set"
    BOOST_POST = "boost_post"
    LOG_EVENT = "log_event"


class AutomationRule:
    """A single automation rule: trigger → condition → action."""

    def __init__(
        self,
        rule_id: str,
        name: str,
        trigger: TriggerType,
        action: ActionType,
        condition: Optional[Callable[[Dict], bool]] = None,
        enabled: bool = True,
    ):
        self.rule_id = rule_id
        self.name = name
        self.trigger = trigger
        self.action = action
        self.condition = condition or (lambda _: True)
        self.enabled = enabled
        self.fire_count = 0
        self.last_fired: Optional[str] = None


class AutomationEngine:
    """Event-driven automation engine.  Services emit events, rules react."""

    def __init__(self):
        self.rules: List[AutomationRule] = []
        self.event_log: List[Dict[str, Any]] = []
        self._action_handlers: Dict[ActionType, Callable] = {}
        self._setup_default_rules()

    # ── Rule Management ──────────────────────────────────────

    def add_rule(self, rule: AutomationRule):
        self.rules.append(rule)
        logger.info(f"Automation rule added: {rule.name}")

    def remove_rule(self, rule_id: str):
        self.rules = [r for r in self.rules if r.rule_id != rule_id]

    def enable_rule(self, rule_id: str):
        for r in self.rules:
            if r.rule_id == rule_id:
                r.enabled = True

    def disable_rule(self, rule_id: str):
        for r in self.rules:
            if r.rule_id == rule_id:
                r.enabled = False

    def get_rules(self) -> List[Dict[str, Any]]:
        return [
            {
                "rule_id": r.rule_id,
                "name": r.name,
                "trigger": r.trigger.value,
                "action": r.action.value,
                "enabled": r.enabled,
                "fire_count": r.fire_count,
                "last_fired": r.last_fired,
            }
            for r in self.rules
        ]

    # ── Action Handlers ──────────────────────────────────────

    def register_action(self, action_type: ActionType, handler: Callable):
        """Register a handler for an action type."""
        self._action_handlers[action_type] = handler

    # ── Event Emission ───────────────────────────────────────

    async def emit(self, trigger: TriggerType, data: Dict[str, Any]):
        """Fire all matching rules for the given trigger."""
        for rule in self.rules:
            if not rule.enabled or rule.trigger != trigger:
                continue
            try:
                if rule.condition(data):
                    await self._execute_action(rule, data)
                    rule.fire_count += 1
                    rule.last_fired = datetime.now(timezone.utc).isoformat()
            except Exception as e:
                logger.error(f"Rule {rule.name} failed: {e}")

    async def _execute_action(self, rule: AutomationRule, data: Dict[str, Any]):
        """Execute the action for a fired rule."""
        event_entry = {
            "rule_id": rule.rule_id,
            "rule_name": rule.name,
            "trigger": rule.trigger.value,
            "action": rule.action.value,
            "data_summary": str(data)[:200],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        handler = self._action_handlers.get(rule.action)
        if handler:
            try:
                await handler(data, rule)
                event_entry["status"] = "success"
            except Exception as e:
                event_entry["status"] = "failed"
                event_entry["error"] = str(e)
                logger.error(f"Action {rule.action.value} failed: {e}")
        else:
            # Default: just log
            event_entry["status"] = "logged"
            logger.info(f"Rule fired (no handler): {rule.name} — {rule.action.value}")

        self.event_log.append(event_entry)

    # ── Default Rules ────────────────────────────────────────

    def _setup_default_rules(self):
        """Register built-in rules for the gym use case."""

        # Rule 1: New lead → push to GymBot + log
        self.add_rule(AutomationRule(
            rule_id="auto_lead_to_gymbot",
            name="New lead → Push to GymBot",
            trigger=TriggerType.NEW_LEAD,
            action=ActionType.PUSH_TO_GYMBOT,
        ))

        # Rule 2: New lead → notify Dylan
        self.add_rule(AutomationRule(
            rule_id="auto_lead_notify_owner",
            name="New lead → Notify Dylan",
            trigger=TriggerType.NEW_LEAD,
            action=ActionType.NOTIFY_OWNER,
        ))

        # Rule 3: High-engagement post → suggest boosting
        self.add_rule(AutomationRule(
            rule_id="auto_boost_high_engagement",
            name="High engagement → Suggest boost",
            trigger=TriggerType.POST_ENGAGEMENT_HIGH,
            action=ActionType.BOOST_POST,
            condition=lambda d: d.get("engagement", 0) > 50,
        ))

        # Rule 4: Ad cost per lead too high → pause ad set
        self.add_rule(AutomationRule(
            rule_id="auto_pause_expensive_ads",
            name="CPL > $25 → Pause ad set",
            trigger=TriggerType.AD_COST_PER_LEAD_HIGH,
            action=ActionType.PAUSE_AD_SET,
            condition=lambda d: float(d.get("cost_per_lead", 0)) > 25.0,
        ))

        # Rule 5: Scheduled post failed → log + notify
        self.add_rule(AutomationRule(
            rule_id="auto_notify_post_failure",
            name="Scheduled post failed → Notify",
            trigger=TriggerType.SCHEDULED_POST_FAILED,
            action=ActionType.NOTIFY_OWNER,
        ))

    # ── Event Log ────────────────────────────────────────────

    def get_event_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.event_log[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_rules": len(self.rules),
            "enabled_rules": sum(1 for r in self.rules if r.enabled),
            "total_events": len(self.event_log),
            "rules": self.get_rules(),
        }
