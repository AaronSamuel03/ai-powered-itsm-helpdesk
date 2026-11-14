SELF_HEAL_PLAYBOOKS = {
    "vpn_reset": {
        "action": "Flushed stale VPN session tokens and re-synced WireGuard/GlobalProtect gateway certificate.",
        "resolved": True,
    },
    "password_reset": {
        "action": "Triggered Active Directory temporary password reset link to employee's verified recovery email.",
        "resolved": True,
    },
    "clear_cache": {
        "action": "Executed remote endpoint script to clear DNS resolver cache and browser SSO cookies.",
        "resolved": True,
    },
}


def attempt_self_heal(intent: str) -> dict:
    playbook = SELF_HEAL_PLAYBOOKS.get(intent)
    if playbook:
        return {"auto_resolved": True, "remediation_steps": playbook["action"]}
    return {"auto_resolved": False, "remediation_steps": "Routed to Tier-2 IT Support Engineer."}
