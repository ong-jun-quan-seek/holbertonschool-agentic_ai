# 0. CRM Server Deployment and Interface Integration

- Configured MSP Server: `crm-server`
- CRM tool detected: `get_customer_status`

## Sumary of result obtained during verification

### Running `/mcp list` ensure it's connected 
```
MCP servers
Per-server rows show standalone token counts.

- crm-server (connected)
- github-mcp-server (connected, builtin)
```

### Prompted `What external (MCP) tools do you have access to?`

It returns the {server-name}-{tool_name} and it's description

```
CRM MCP 
crm-server-get_customer_status — Retrieves an order/customer status using an email address.
```